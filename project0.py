# project0.py
import os
import re
import json
import time
from google import genai
from google.genai import errors
from groq import Groq
from openai import OpenAI
from parse_puml import parse_puml_to_ast

# ---------------------------------------------------------------------------
# API CLIENT INITIALIZATION
# ---------------------------------------------------------------------------

#GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "Add your API Key here")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", " ")

#GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "Add your API Key here ")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", " ")

#OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "Add your API Key here ")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", " ")

# Initialize SDK Clients
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception:
    groq_client = None

try:
    openrouter_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
except Exception:
    openrouter_client = None


# ---------------------------------------------------------------------------
# AI GENERATOR FUNCTIONS (INDIVIDUAL PROMPT HANDLING)
# ---------------------------------------------------------------------------

def generate_with_gemini(cur_prom):
    """Generates PlantUML using Gemini 3.5 Flash."""
    max_retries = 5
    delay = 15

    for attempt in range(max_retries):
        try:
            response = gemini_client.models.generate_content(
                model='gemini-1.5-pro',
                contents=cur_prom
            )
            return response.text
        except errors.ClientError as e:
            if e.code == 429 or "RESOURCE_EXHAUSTED" in str(e):
                print(f"\n[Gemini 429 Quota Hit] Waiting {delay}s before retrying...")
                time.sleep(delay)
                delay += 5
            else:
                raise e
    raise Exception("Max retries exceeded for Gemini API call.")


def generate_with_groq(prompt, model_name="llama-3.3-70b-versatile"):
    """Generates PlantUML using Llama 3.3 70B via Groq API."""
    if not groq_client:
        raise ValueError("Groq client not initialized properly.")
    
    max_retries = 3
    delay = 5
    for attempt in range(max_retries):
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_name,
                temperature=0.2
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                print(f"\n[Groq 429 Quota Hit] Waiting {delay}s before retrying...")
                time.sleep(delay)
            else:
                raise e
    raise Exception("Max retries exceeded for Groq API call.")


def generate_with_openrouter(prompt, model_name="nvidia/nemotron-3-super-120b-a12b:free"):
    """Generates PlantUML using Nemotron 120B via OpenRouter API."""
    if not openrouter_client:
        raise ValueError("OpenRouter client not initialized properly.")
    
    max_retries = 3
    delay = 5
    for attempt in range(max_retries):
        try:
            response = openrouter_client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                print(f"\n[OpenRouter 429 Quota Hit] Waiting {delay}s before retrying...")
                time.sleep(delay)
            else:
                raise e
    raise Exception("Max retries exceeded for OpenRouter API call.")


def generate_puml(prompt, model_name="Gemini 1.5 pro"):
    """
    Router function to execute prompt generation for a specific AI model.
    """
    if model_name == "Llama 3.3 70B (Groq)":
        return generate_with_groq(prompt, "llama-3.3-70b-versatile")
    elif model_name == "Nemotron 120B (OpenRouter)":
        return generate_with_openrouter(prompt, "nvidia/nemotron-3-super-120b-a12b:free")
    else:
        return generate_with_gemini(prompt)


# ---------------------------------------------------------------------------
# PARSER & UTILITIES
# ---------------------------------------------------------------------------

def extract_puml(text):
    """Extracts clean PlantUML block enclosed in @startuml and @enduml."""
    if not text or not isinstance(text, str):
        return ""
    match = re.search(r'(@startuml.*?@enduml)', text, re.DOTALL)
    return match.group(1) if match else text.strip()


def parse_puml_string(puml_text):
    """
    Directly converts PlantUML string to AST using pure Python parser.
    Replaces old Node.js wrapper execution.
    """
    if not puml_text:
        return {"error": "No PlantUML text found to parse."}
    
    return parse_puml_to_ast(puml_text)