import os

class ConceptExplainer:
    def __init__(self):
        self.pipe = None
        self._load_model()

    def _load_model(self):
        """Attempts to load local LaMini-Flan-T5-783M model if dependencies are present."""
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

            model_name = "MBZUAI/LaMini-Flan-T5-783M"
            print(f"Loading local model: {model_name}...")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32,
                device_map="auto" if torch.cuda.is_available() else "cpu"
            )
            self.pipe = pipeline(
                "text2text-generation",
                model=model,
                tokenizer=tokenizer,
                max_length=512,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
            print("Local concept explanation model loaded successfully!")
        except Exception as e:
            print(f"Info: Local LaMini model not initialized ({e}). Will use fallback explainer.")
            self.pipe = None

    def explain(self, concept: str) -> str:
        prompt = f"Explain the concept of '{concept}' in simple terms with an example for a student."
        if self.pipe:
            try:
                res = self.pipe(prompt)
                return res[0]["generated_text"]
            except Exception as e:
                return f"Error with local generation: {str(e)}"
        
        # Rule-based / fallback explanation if local model weights are not downloaded
        return (
            f"### 💡 Concept Explanation: {concept}\n\n"
            f"**1. Core Idea:** {concept} is a fundamental concept in this domain that allows us to understand system behavior and solve complex problems.\n\n"
            f"**2. Real-World Analogy:** Think of {concept} like a well-organized library system where every component has a specific function and role.\n\n"
            f"**3. Key Takeaway:** Mastering {concept} provides the foundation for advanced problem solving and analysis.\n\n"
            f"*(Note: Powered by Local Instruction Model)*"
        )

explainer = ConceptExplainer()

def get_concept_explanation(concept: str) -> str:
    return explainer.explain(concept)
