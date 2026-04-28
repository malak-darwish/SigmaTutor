"""
groq_client.py

Groq helper for SigmaTutor — replaces gemini_client.py

Uses:
- Groq API with llama-3.1-8b-instant
- Same function signatures as gemini_client for easy drop-in replacement
"""

import os
import json
import re
import time
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

try:
    from json_repair import repair_json
    HAS_JSON_REPAIR = True
except ImportError:
    HAS_JSON_REPAIR = False

load_dotenv()


def get_llm() -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing. Add it to your .env file.")
    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        api_key=api_key
    )


def clean_json_text(text: str) -> str:
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def repair_invalid_json_backslashes(text: str) -> str:
    return re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', text)


def safe_json_loads(raw_text: str) -> Dict[str, Any]:
    cleaned = clean_json_text(raw_text)

    try:
        return json.loads(cleaned)
    except Exception:
        pass

    try:
        repaired = repair_invalid_json_backslashes(cleaned)
        return json.loads(repaired)
    except Exception:
        pass

    if HAS_JSON_REPAIR:
        try:
            repaired_obj = repair_json(cleaned, return_objects=True)
            if isinstance(repaired_obj, dict):
                return repaired_obj
        except Exception:
            pass

    raise ValueError("Could not parse Groq response as JSON.")


def ask_groq_text(
    prompt: str,
    system_instruction: Optional[str] = None,
    max_output_tokens: int = 4096,
    temperature: float = 0.7,
    retries: int = 2
) -> str:
    llm = get_llm()
    last_error = ""

    messages = []
    if system_instruction:
        from langchain_core.messages import SystemMessage
        messages.append(SystemMessage(content=system_instruction))
    messages.append(HumanMessage(content=prompt))

    for attempt in range(retries):
        try:
            response = llm.invoke(messages)
            return response.content or ""
        except Exception as error:
            last_error = str(error)
            print(f"[Groq warning] Attempt {attempt + 1}/{retries}: {last_error}")
            if attempt < retries - 1:
                time.sleep(2)

    return f"Groq is temporarily unavailable. Last error: {last_error}"


def ask_groq_json(
    prompt: str,
    system_instruction: Optional[str] = None,
    max_output_tokens: int = 4096,
    temperature: float = 0.7,
    retries: int = 2
) -> Dict[str, Any]:
    llm = get_llm()
    last_error = ""

    full_prompt = prompt + "\n\nIMPORTANT: Return ONLY valid JSON. No explanation, no markdown, no backticks."

    messages = []
    if system_instruction:
        from langchain_core.messages import SystemMessage
        messages.append(SystemMessage(content=system_instruction))
    messages.append(HumanMessage(content=full_prompt))

    for attempt in range(retries):
        try:
            response = llm.invoke(messages)
            raw_text = response.content or ""

            try:
                parsed = safe_json_loads(raw_text)
                parsed["_model_used"] = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
                return parsed
            except Exception as parse_error:
                return {
                    "type": "error",
                    "message": "Groq response could not be parsed as JSON.",
                    "raw_response": raw_text,
                    "error": str(parse_error)
                }

        except Exception as error:
            last_error = str(error)
            print(f"[Groq warning] Attempt {attempt + 1}/{retries}: {last_error}")
            if attempt < retries - 1:
                time.sleep(2)

    return {
        "type": "error",
        "message": "Groq API call failed.",
        "error": last_error
    }