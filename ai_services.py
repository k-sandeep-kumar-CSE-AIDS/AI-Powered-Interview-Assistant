import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from sentence_transformers import SentenceTransformer
import spacy
from .config import Config
import os

os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'

class AIServices:
    def __init__(self):
        # Initialize Gemma-2B (faster than Mistral on M1/M2)
        self.tokenizer = AutoTokenizer.from_pretrained(
            Config.LLM_MODEL,
            token=Config.HUGGINGFACE_TOKEN
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            Config.LLM_MODEL,
            device_map="auto",
            torch_dtype=torch.float16,
            token=Config.HUGGINGFACE_TOKEN
        )
        self.pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=300,
            do_sample=True,
            temperature=0.7
        )
        
        # Lightweight models for other tasks
        self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.nlp = spacy.load("en_core_web_sm")
    
    def generate_questions_from_resume(self, resume_text):
        prompt = f"""Generate 5-7 interview questions from this resume:
        {resume_text}
        Include technical, behavioral, and situational questions."""
        return self._generate(prompt)
    
    def evaluate_answer(self, question, answer):
        prompt = f"""Evaluate this interview Q&A:
        Q: {question}
        A: {answer}
        Give scores (1-10) for: relevance, technical accuracy, clarity.
        Suggest 2 improvements."""
        return self._generate(prompt)
    
    def _generate(self, prompt):
        try:
            output = self.pipeline(prompt)[0]['generated_text']
            return output.split("[/INST]")[-1].strip()  # Clean output
        except Exception as e:
            return f"Error generating response: {str(e)}"
