# 🧞‍♂️ EduGenie: Google Gemini Powered Learning Assistant

An intelligent, multi-model academic assistant designed for students and educators. EduGenie combines **Google Gemini 1.5 Pro (Cloud)** and **LaMini-Flan-T5-783M (Local CPU)** with a **FAISS-powered RAG pipeline** for grounded academic document Q&A, interactive quizzes, concept explanations, and personalized study paths.

---

## 🏗️ System Architecture

```text
EduGenie/
├── main.py                  # FastAPI Application & API Routes
├── explanation_module.py    # Local Concept Explainer (LaMini-Flan-T5-783M)
├── qna.py                   # Question Answering (Gemini 1.5 Pro)
├── quiz_module.py           # Auto MCQ Quiz Generator (Gemini 1.5 Pro)
├── summary_module.py        # Text & Note Summarizer (Gemini 1.5 Pro)
├── learning_path.py         # Personalized Roadmap Planner (Gemini 1.5 Pro)
├── document_processor.py    # PDF Text Extraction & Chunking
├── vector_store.py          # FAISS Vector Indexing & Semantic Search
├── rag_pipeline.py          # Grounded Context-Augmented Q&A
│
├── templates/
│   └── index.html           # Learning Studio Web UI (Jinja2)
│
├── static/
│   ├── style.css            # Responsive CSS Styles
│   └── app.js               # Client-side Async Controller
│
├── tests/
│   └── test_api.py          # Unit & Integration Tests (pytest)
│
├── requirements.txt         # Python Dependencies
├── .env.example             # Environment Config Template
└── .gitignore               # Git Ignore Rules
```

---

## ⚡ Quick Start Guide

### 1. Clone & Set Up Environment
```bash
# Clone repository
git clone <your-repo-url>
cd EduGenie

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Copy `.env.example` to `.env` and add your Gemini API Key:
```bash
cp .env.example .env
```
Inside `.env`:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-pro
```

### 4. Run Locally
Start the development server with auto-reload:
```bash
uvicorn main:app --reload --port 8000
```

- 🌐 **Web Interface**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📖 **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 🩺 **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🧪 Running Automated Tests
```bash
pytest tests/ -v
```

---

## 🌟 Key Features
- **📚 Grounded Academic PDF Q&A (RAG)**: Ingest research papers and textbooks; retrieve answers with exact page citations and confidence scores.
- **💡 Local Concept Explainer**: Run lightweight instruction explanations locally on CPU.
- **🎯 Interactive MCQ Quiz Generator**: Dynamic multiple-choice questions with instant scoring and explanations.
- **📝 Executive Summaries**: Condense long papers and study guides into structured notes.
- **🗺️ Learning Roadmap Builder**: Synthesize multi-week step-by-step curriculum with hands-on exercises.
