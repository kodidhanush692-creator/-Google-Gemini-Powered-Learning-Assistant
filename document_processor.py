import os
from typing import List, Dict

class DocumentProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text_from_pdf(self, file_path: str) -> List[Dict[str, any]]:
        """
        Extracts text from a PDF file page by page using pypdf.
        """
        pages_content = []
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages_content.append({
                        "page": page_idx + 1,
                        "text": text.strip()
                    })
        except Exception as e:
            print(f"Error extracting PDF: {e}")
        return pages_content

    def chunk_documents(self, pages_content: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Splits extracted pages into overlapping chunks with page metadata.
        """
        chunks = []
        for page_data in pages_content:
            page_num = page_data["page"]
            text = page_data["text"]

            start = 0
            while start < len(text):
                end = start + self.chunk_size
                chunk_text = text[start:end]
                chunks.append({
                    "page": page_num,
                    "chunk": chunk_text.strip()
                })
                start += self.chunk_size - self.chunk_overlap
                
        return chunks
