import os
import shutil
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Import agent
from backend.agent import run_agent, clear_memory

# Import RAG utilities
from backend.rag import add_document, get_stats

# ── APP SETUP 

app = FastAPI(
    title="SigmaTutor API",
    description="AI Tutor Agent for Signals & Systems and Communications Systems",
    version="1.0.0"
)

# Allow React frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload folder
UPLOAD_DIR = Path("backend/data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# REQUEST MODELS 

class ChatRequest(BaseModel):
    message: str
    
class ClearRequest(BaseModel):
    confirm: bool = True

# ENDPOINTS 

@app.get("/")
def root():
    """Health check"""
    return {
        "status": "running",
        "agent": "SigmaTutor",
        "version": "1.0.0",
        "message": "Welcome to SigmaTutor API!"
    }

@app.get("/health")
def health():
    """Health check for frontend"""
    return {"status": "healthy", "agent": "ready"}

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint — receives user message, returns agent response.
    Handles all types of questions:
    - Signals & Systems course questions (uses RAG)
    - Communications Systems questions (uses RAG)
    - General questions like LLMs, AI, math (uses Gemini knowledge)
    - Signal plotting requests (uses plotter tool)
    - MATLAB code requests (uses MATLAB generator)
    - Exam generation (uses exam generator)
    - Formula proofs (uses prover tool)
    - Block diagrams (uses diagram generator)
    - Web search for current info (uses DuckDuckGo)
    """
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Run the agent
        result = run_agent(request.message)
        
        return {
            "success": result["success"],
            "response": result["response"],
            "message": request.message
        }
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "response": f"Server error: {str(e)}",
                "message": request.message
            }
        )

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a new PDF to the knowledge base.
    Person D (frontend) connects this to the PDF upload button in UI.
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )
        
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Add to RAG vector store
        success = add_document(str(file_path))
        
        if success:
            return {
                "success": True,
                "message": f"'{file.filename}' uploaded and added to knowledge base successfully!",
                "filename": file.filename
            }
        else:
            return {
                "success": False,
                "message": f"File uploaded but failed to add to knowledge base.",
                "filename": file.filename
            }
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Upload error: {str(e)}"
            }
        )

@app.post("/clear-history")
async def clear_history(request: ClearRequest):
    """
    Clear conversation history.
    Person D connects this to the 'New Chat' button in UI.
    """
    try:
        if request.confirm:
            clear_memory()
            return {
                "success": True,
                "message": "Conversation history cleared!"
            }
        return {"success": False, "message": "Confirmation required"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.get("/stats")
async def stats():
    """
    Get knowledge base statistics.
    Person D can show this in the sidebar UI.
    """
    try:
        rag_stats = get_stats()
        return {
            "success": True,
            "rag": rag_stats,
            "upload_dir": str(UPLOAD_DIR),
            "models": {
                "llm": "gemini-2.5-flash",
                "embeddings": "all-MiniLM-L6-v2"
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.get("/tools")
async def list_tools():
    """
    List all available tools.
    Person D can show these in the UI sidebar.
    """
    return {
        "success": True,
        "tools": [
            {
                "name": "RAG Search",
                "description": "Searches course lectures, textbooks, and past exams",
                "icon": "📚"
            },
            {
                "name": "Signal Plotter",
                "description": "Plots signals in time and frequency domain",
                "icon": "📊",
                "status": "Person B implementing"
            },
            {
                "name": "MATLAB Generator",
                "description": "Generates clean MATLAB code",
                "icon": "💻",
                "status": "Person B implementing"
            },
            {
                "name": "Exam Generator",
                "description": "Generates exams with solutions",
                "icon": "📝",
                "status": "Person C implementing"
            },
            {
                "name": "Signal Calculator",
                "description": "Solves math problems step by step",
                "icon": "🔢",
                "status": "Person C implementing"
            },
            {
                "name": "Formula Prover",
                "description": "Proves and derives formulas with LaTeX",
                "icon": "📐",
                "status": "Person C implementing"
            },
            {
                "name": "Diagram Generator",
                "description": "Generates block diagrams",
                "icon": "📡",
                "status": "Person B implementing"
            },
            {
                "name": "Concept Explainer",
                "description": "Explains concepts step by step",
                "icon": "💡",
                "status": "Person C implementing"
            },
            {
                "name": "Frequency Sandbox",
                "description": "Interactive frequency domain exploration",
                "icon": "🌊",
                "status": "Person B implementing"
            },
            {
                "name": "Web Search",
                "description": "Searches the web for current information",
                "icon": "🌐"
            }
        ]
    }


# RUN SERVER 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )