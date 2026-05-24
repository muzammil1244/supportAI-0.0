from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os


llm = os.getenv("GROQ_API")


agent = ChatGroq(api_key=llm,model="allam-2-7b")






