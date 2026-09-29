import os
from typing import List, Dict
from google import genai
from google.genai import types

class RAGPipeline:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None

    def generate_grounded_answer(self, query: str, context_chunks: List[Dict[str, any]]) -> str:
        if not self.client:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                self.client = genai.Client(api_key=api_key)
            else:
                return "⚠️ Error: GEMINI_API_KEY is not configured in .env."

        if not context_chunks:
            return "No document context available. Please upload an academic PDF first."

        context_str = "\n\n".join([
            f"[Page {chunk['page']}]: {chunk['chunk']}" 
            for chunk in context_chunks
        ])

        system_instruction = (
            "You are EduGenie Document Tutor. Answer the student's question based strictly on "
            "the provided academic document excerpts. Always cite the page number(s) where the "
            "information is located. If the answer is not in the context, clearly state that."
        )

        user_prompt = (
            f"Academic Document Context:\n{context_str}\n\n"
            f"Student Question: {query}\n\n"
            f"Provide a clear, accurate explanation with citations."
        )

        try:
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            response = self.client.models.generate_content(
                model=model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3
                )
            )
            return response.text
        except Exception as e:
            return f"⚠️ Error generating answer with Gemini: {str(e)}"
