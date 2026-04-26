import os
import json
import re
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def get_model_name() -> str:
    return os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from .env file.")
    return Groq(api_key=api_key)

def ask_gemini_json(
    prompt: str,
    system_instruction: Optional[str] = None,
    max_output_tokens: int = 4096,
    temperature: float = 0.7,
    retries: int = 1
) -> Dict[str, Any]:
    client = get_client()
    model_name = get_model_name()
    
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_output_tokens,
            temperature=temperature
        )
        
        raw_text = response.choices[0].message.content or ""
        
        # Clean markdown fences
        cleaned = re.sub(r'```(?:json)?\s*(.*?)```', r'\1', raw_text, flags=re.DOTALL).strip()
        
        try:
            parsed = json.loads(cleaned)
            parsed["_model_used"] = model_name
            return parsed
        except:
            return {
                "type": "error",
                "message": "Could not parse response as JSON.",
                "raw_response": raw_text
            }
    except Exception as e:
        return {
            "type": "error",
            "message": str(e),
            "model_used": model_name
        }

def ask_gemini_text(
    prompt: str,
    system_instruction: Optional[str] = None,
    max_output_tokens: int = 4096,
    temperature: float = 0.7,
    retries: int = 1
) -> str:
    client = get_client()
    model_name = get_model_name()
    
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_output_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"Error: {str(e)}"