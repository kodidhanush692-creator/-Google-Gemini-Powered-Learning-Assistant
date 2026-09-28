import os
import shutil
from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import core modules
from explanation_module import get_concept_explanation
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import generate_learning_path
from document_processor import DocumentProcessor
from vector_store import VectorStore
from rag_pipeline import RAGPipeline

app = FastAPI(title="EduGenie: Google Gemini Powered Learning Assistant")

# Ensure required directories exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize RAG services
doc_processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)
vector_store = VectorStore()
rag_service = RAGPipeline()

class ProcessRequest(BaseModel):
    action: str  # "explain" | "qna" | "quiz" | "summary" | "learning_path"
    input_text: str
    subject: str = "General"

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serves the main EduGenie Web Interface."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_name": "EduGenie",
        "description": "Google Gemini Powered Learning Assistant"
    })

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "app": "EduGenie"}

@app.post("/api/process")
async def process_text_action(data: ProcessRequest):
    """Handles text-based study actions (explain, Q&A, quiz, summary, learning path)."""
    text = data.input_text.strip()
    action = data.action

    if not text:
        return JSONResponse(status_code=400, content={"error": "Input text cannot be empty."})

    try:
        if action == "explain":
            result = get_concept_explanation(text)
            return {"type": "text", "model": "LaMini-Flan-T5-783M (Local CPU)", "data": result}

        elif action == "qna":
            result = answer_question(text, data.subject)
            return {"type": "text", "model": "Gemini 1.5 Pro (Cloud)", "data": result}

        elif action == "quiz":
            result = generate_quiz(text)
            return {"type": "quiz", "model": "Gemini 1.5 Pro (Cloud)", "data": result}

        elif action == "summary":
            result = summarize_text(text)
            return {"type": "text", "model": "Gemini 1.5 Pro (Cloud)", "data": result}

        elif action == "learning_path":
            result = generate_learning_path(text)
            return {"type": "text", "model": "Gemini 1.5 Pro (Cloud)", "data": result}

        else:
            return JSONResponse(status_code=400, content={"error": f"Unknown action: {action}"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Extracts, chunks, and indexes uploaded academic PDF into FAISS."""
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(status_code=400, content={"error": "Please upload a valid .pdf file."})

    file_path = os.path.join("uploads", file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pages = doc_processor.extract_text_from_pdf(file_path)
        chunks = doc_processor.chunk_documents(pages)

        vector_store.clear()
        vector_store.add_documents(chunks)

        return {
            "status": "success",
            "filename": file.filename,
            "pages": len(pages),
            "chunks": len(chunks),
            "message": f"Successfully indexed {len(pages)} pages ({len(chunks)} chunks) into FAISS."
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"PDF Processing failed: {str(e)}"})

@app.post("/api/ask_doc")
async def ask_document(question: str = Form(...), top_k: int = Form(3)):
    """RAG: Queries indexed PDF chunks and returns answer with page citations."""
    query = question.strip()
    if not query:
        return JSONResponse(status_code=400, content={"error": "Question cannot be empty."})

    try:
        relevant_chunks = vector_store.search(query=query, top_k=top_k)
        answer = rag_service.generate_grounded_answer(query=query, context_chunks=relevant_chunks)
        return {
            "question": query,
            "answer": answer,
            "sources": [{"page": c["page"], "chunk": c["chunk"], "score": round(c.get("score", 0.0), 3)} for c in relevant_chunks]
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
