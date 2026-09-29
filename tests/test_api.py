import pytest
from fastapi.testclient import TestClient
from main import app
from document_processor import DocumentProcessor
from vector_store import VectorStore

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["app"] == "EduGenie"

def test_home_page_rendering():
    response = client.get("/")
    assert response.status_code == 200
    assert "EduGenie" in response.text
    assert "Learning Studio" in response.text

def test_document_processor_chunking():
    processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
    mock_pages = [
        {"page": 1, "text": "Artificial Intelligence is transforming higher education and modern learning systems."},
        {"page": 2, "text": "Vector databases enable fast semantic search across thousands of academic research papers."}
    ]
    chunks = processor.chunk_documents(mock_pages)
    assert len(chunks) >= 2
    assert all("page" in c and "chunk" in c for c in chunks)

def test_vector_store_operations():
    store = VectorStore()
    sample_chunks = [
        {"page": 1, "chunk": "Neural networks use gradient descent for backpropagation optimization."},
        {"page": 2, "chunk": "Photosynthesis converts solar energy into chemical energy."}
    ]
    store.add_documents(sample_chunks)
    
    results = store.search("gradient descent optimization", top_k=1)
    assert len(results) == 1
    assert results[0]["page"] == 1
    
    store.clear()
    assert len(store.metadata) == 0

def test_empty_process_request():
    response = client.post("/api/process", json={
        "action": "qna",
        "input_text": ""
    })
    assert response.status_code == 400
