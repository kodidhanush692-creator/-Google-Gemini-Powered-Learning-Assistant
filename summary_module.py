import os
from google import genai
from google.genai import types

def summarize_text(content: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ Error: GEMINI_API_KEY is not set in environment or .env file."

    try:
        client = genai.Client(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
        system_instruction = (
            "You are EduGenie Summarizer. Break down the provided study material or topic into:"
            "\n1. **Key Takeaways** (Bulleted list)"
            "\n2. **Core Concepts & Definitions**"
            "\n3. **Quick Review Summary** (1-2 sentences summarizing the core idea)."
        )

        response = client.models.generate_content(
            model=model_name,
            contents=f"Please summarize the following material:\n\n{content}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.4
            )
        )
        return response.text
    except Exception as e:
        return f"⚠️ Error summarizing text: {str(e)}"
