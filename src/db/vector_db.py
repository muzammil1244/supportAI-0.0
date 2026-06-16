from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
import os
from pinecone import Pinecone

from dotenv import load_dotenv


load_dotenv()

vc_api_key = os.getenv("PINECONE")


embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

pc = Pinecone(api_key=vc_api_key)
index = pc.Index("saas0rag")


vector_store = PineconeVectorStore(index=index,embedding=embedding_model)
