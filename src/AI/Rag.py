from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from fastapi import HTTPException, UploadFile
import tempfile
import os
from PyPDF2 import PdfReader   # ✅ Docling hata ke PyPDF2 use kar rahe hain
from pinecone import Pinecone
from src.db.vector_db import vector_store
from dotenv import load_dotenv


load_dotenv()

vc_api_key = os.getenv("PINECONE")

# embedding_model = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )


pc = Pinecone(api_key=vc_api_key)
index = pc.Index("saas0rag")

async def upload_controller(file):
    temp_path = None
    try:
        # 🛑 Validation
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")

        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"{file.filename} is not a PDF file")

        # 📂 Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail=f"{file.filename} is empty")
            temp.write(content)
            temp_path = temp.name

        # 📖 Load PDF with PyPDF2
        reader = PdfReader(temp_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        if not text.strip():
            raise HTTPException(status_code=406, detail="No readable content found in uploaded file")

        # 🔪 Split text
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_text(text)

        docs = [Document(page_content=chunk, metadata={"source": file.filename}) for chunk in chunks]

       
        # vector_store = PineconeVectorStore(index=index,embedding=embedding_model)
    # Purana data hatao
        stats = index.describe_index_stats()

        if "pdf_data" in stats.get("namespaces", {}):
           index.delete(delete_all=True, namespace="pdf_data")        
        # Naya data add karo
        vector_store.add_documents(
            docs
            )
        
        return {
            "status": "success",
            "file_processed": file.filename,
            "chunks_stored": len(docs)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")
    finally:
        # 🧹 Cleanup temp file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
