import os
from google import genai
from google.genai import types

def generate_learning_path(goal: str, target_timeline_weeks: int = 4) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ Error: GEMINI_API_KEY is not set in environment or .env file."

    try:
        client = genai.Client(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
        system_instruction = (
            f"You are EduGenie Curriculum Architect. Create a structured {target_timeline_weeks}-week "
            "learning roadmap for the requested goal. For each week include: "
            "\n- Weekly Focus & Concepts"
            "\n- Practical Hands-on Exercises"
            "\n- Milestones & Recommended Practice Projects."
        )

        response = client.models.generate_content(
            model=model_name,
            contents=f"Learning Goal: {goal}\nTarget Timeline: {target_timeline_weeks} weeks",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.5
            )
        )
        return response.text
    except Exception as e:
        return f"⚠️ Error generating learning roadmap: {str(e)}"
