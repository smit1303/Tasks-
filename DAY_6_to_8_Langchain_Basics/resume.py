from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
import os

# Load API Key
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Initialize LLM
model = ChatGroq(
    api_key=api_key,
    model_name="llama3-8b-8192"
)

# Output parser
parser = JsonOutputParser()

# Prompt
prompt = PromptTemplate(
    input_variables=["role", "achievements"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    template="""
You are a professional resume writer.

Generate one impactful resume bullet point based on the role and achievements. Use strong action verbs and keep it under 30 words.

Respond ONLY in valid JSON format using this schema:
{format_instructions}

Role: {role}
Achievements: {achievements}
""",
)

# Chain
chain = prompt | model | parser

# Input
input_data = {
    "role": "Machine Learning Engineer",
    "achievements": "Deployed scalable ML models to production, reduced inference latency by 50%, collaborated with data scientists"
}

# Run and print
result = chain.invoke(input_data)
print(result)
