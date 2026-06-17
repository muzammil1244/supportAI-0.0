from langchain_pinecone import PineconeVectorStore, PineconeEmbeddings
import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

vc_api_key = os.getenv("PINECONE")

embedding_model = PineconeEmbeddings(
    model="llama-text-embed-v2",
    pinecone_api_key=vc_api_key
)

pc = Pinecone(api_key=vc_api_key)
index = pc.Index("saas0rag")

vector_store = PineconeVectorStore(index=index, embedding=embedding_model)