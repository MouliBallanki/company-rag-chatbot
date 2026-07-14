import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

# 1. Import configurations & pipeline orchestrators
import config
from ingestion.pipeline import IngestionPipeline 
from services.chunker_service import ChunkerService
from services.embedding_service import EmbeddingService
from services.vector_service import VectorService

router = APIRouter()

# Temporary upload workspace directory
UPLOAD_DIR = "data/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    query: str

@router.post("/api/admin/upload")
async def upload_documents(files: list[UploadFile] = File(...)):
    try:
        # Clear out any old residual files in the data directory before starting a fresh run
        for f in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, f)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Save the uploaded multipart form streams down to local disk space
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        
        # 2. Instantiate services directly with your config settings
        chunker = ChunkerService(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
        embedder = EmbeddingService(model_name=config.EMBEDDING_MODEL)
        vector_store = VectorService(chroma_path=config.CHROMA_PATH, collection_name=config.COLLECTION_NAME)
        
        # 3. Initialize your multi-file directory pipeline orchestrator
        pipeline = IngestionPipeline(
            chunker=chunker,
            embedder=embedder,
            vector_store=vector_store
        )
        
        # 4. Run directory ingestion over data/documents/
        summary = pipeline.run_directory(UPLOAD_DIR)
        
        total_chunks = sum(summary.values())
        return {
            "status": "success", 
            "message": f"Successfully ingested {len(summary)} file(s). Generated {total_chunks} total vector chunks inside ChromaDB!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/chat")
async def chat_query(payload: QueryRequest):
    try:
        # Structured mock response for current runtime safety
        return {
            "query": payload.query, 
            "answer_context": ["Ingestion pipeline is completely live! Ready to build real retrieval next."], 
            "sources": ["System Verification Engine"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))