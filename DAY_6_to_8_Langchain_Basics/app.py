import streamlit as st
from pathlib import Path

# --- Updated LangChain Imports ---
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
# --- End of Updated Imports ---

from sqlalchemy import create_engine, URL
from langchain_groq import ChatGroq

st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🦜")
st.title("🦜 LangChain: Chat with SQL DB")

# --- Constants and Sidebar Setup ---
LOCALDB = "USE_LOCALDB"
POSTGRESQL = "USE_POSTGRESQL"
radio_opt = ["Use SQLite3 Database - student.db", "Connect to your PostgreSQL Database"]

selected_opt = st.sidebar.radio(label="Choose the DB you want to chat with", options=radio_opt)

# --- API Key and LLM Initialization ---
api_key = st.sidebar.text_input(label="Groq API Key", type="password")

if not api_key:
    st.warning("Please enter your Groq API Key to continue.")
    st.stop()

llm = ChatGroq(
    groq_api_key=api_key,
    model_name="deepseek-r1-distill-llama-70b",
    streaming=True
)

# --- Database Configuration ---
@st.cache_resource(ttl="2h")
def get_db_engine(db_type, connection_args=None):
    """Creates and returns a SQLAlchemy engine for the selected database."""
    if db_type == LOCALDB:
        db_path = (Path(__file__).parent / "student.db").absolute()
        return create_engine(f"sqlite:///{db_path}")
    
    if db_type == POSTGRESQL:
        try:
            url_object = URL.create(
                drivername="postgresql+psycopg2",
                username=connection_args['user'],
                password=connection_args['password'],
                host=connection_args['host'],
                port=connection_args['port'],
                database=connection_args['db'],
            )
            return create_engine(url_object)
        except Exception as e:
            st.error(f"Failed to create database engine: {e}")
            st.stop()

# --- Main Application Logic ---
db = None
engine = None

if selected_opt == radio_opt[0]:  # SQLite
    engine = get_db_engine(LOCALDB)
    st.success("Successfully connected to the SQLite database!")

elif selected_opt == radio_opt[1]:  # PostgreSQL
    st.sidebar.info("Please provide your PostgreSQL credentials.")
    pg_host = st.sidebar.text_input("PostgreSQL Host", key="pg_host")
    pg_port = st.sidebar.text_input("PostgreSQL Port", value="5432", key="pg_port")
    pg_user = st.sidebar.text_input("PostgreSQL User", key="pg_user")
    pg_password = st.sidebar.text_input("PostgreSQL Password", type="password", key="pg_password")
    pg_db = st.sidebar.text_input("PostgreSQL Database Name", key="pg_db")

    if all([pg_host, pg_port, pg_user, pg_password, pg_db]):
        conn_args = {
            "host": pg_host,
            "port": int(pg_port), # Ensure port is an integer
            "user": pg_user,
            "password": pg_password,
            "db": pg_db
        }
        engine = get_db_engine(POSTGRESQL, connection_args=conn_args)
        st.success("Successfully connected to the PostgreSQL database!")
    else:
        st.info("Please fill in all PostgreSQL connection details in the sidebar.")
        st.stop()

# Proceed only if the engine was successfully created
if engine:
    db = SQLDatabase(engine)
    
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
    )

    # --- Chat UI ---
    if "messages" not in st.session_state or st.sidebar.button("Clear chat history"):
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you with your database?"}]

    for msg in st.session_state["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])

    if user_query := st.chat_input("Ask a question about your database"):
        st.session_state["messages"].append({"role": "user", "content": user_query})
        st.chat_message("user").write(user_query)

        with st.chat_message("assistant"):
            st_callback = StreamlitCallbackHandler(st.container())
            try:
                response = agent.run(user_query, callbacks=[st_callback])
            except Exception as e:
                response = f"An error occurred: {e}"
            
            st.session_state["messages"].append({"role": "assistant", "content": response})
            st.write(response)
