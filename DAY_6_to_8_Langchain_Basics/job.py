from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
import os

# Load GROQ_API_KEY from .env
load_dotenv()

# Initialize LLM
model = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-8b-8192"
)

# Output parser
parser = JsonOutputParser()

# Prompt template for skill extraction
prompt = PromptTemplate(
    input_variables=["job_description"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    template="""
You are an HR assistant. Extract the required skills from the job description below. Return your answer in JSON format.

Categorize into:
- technical_skills
- soft_skills

Job Description:
{job_description}

{format_instructions}
"""
)

# Chain
chain = prompt | model | parser

# Input
input_data = {
    "job_description": """
We are looking for a Backend Developer with strong experience in Python, FastAPI, and PostgreSQL.
The candidate should also demonstrate excellent communication and collaboration skills.
Knowledge of Docker and AWS is a plus.
"""
}

# Run the chain
result = chain.invoke(input_data)
print(result)

# Optional: Visualize the flow
chain.get_graph().print_ascii()
