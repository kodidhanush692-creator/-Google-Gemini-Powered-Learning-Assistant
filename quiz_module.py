import os
import json
from google import genai
from google.genai import types

def generate_quiz(topic: str, num_questions: int = 3) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY not configured in .env file."}

    try:
        client = genai.Client(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        system_instruction = (
            f"You are EduGenie Quiz Generator. Generate a {num_questions}-question multiple choice quiz "
            "on the given topic. You MUST respond in strictly valid JSON matching this schema:\n"
            "{\n"
            '  "topic": "topic name",\n'
            '  "questions": [\n'
            '    {\n'
            '      "question": "Question text here?",\n'
            '      "options": [\n'
            '        {"id": "A", "text": "Option A text"},\n'
            '        {"id": "B", "text": "Option B text"},\n'
            '        {"id": "C", "text": "Option C text"},\n'
            '        {"id": "D", "text": "Option D text"}\n'
            '      ],\n'
            '      "correct_option_id": "A",\n'
            '      "explanation": "Why this answer is correct."\n'
            '    }\n'
            '  ]\n'
            "}"
        )

        response = client.models.generate_content(
            model=model_name,
            contents=f"Generate a {num_questions}-question quiz on the topic: {topic}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.3
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": f"Failed to generate quiz: {str(e)}"}
