r"""
gemini_client.py

Final stable Gemini helper for SigmaTutor Person C tools.

This version:
- Uses ONE Gemini model only from .env
- Does NOT use fallback models
- Retries only for temporary 503 high-demand errors
- Does NOT waste retries on 429 quota errors
- Repairs invalid LaTeX backslashes before JSON parsing
- Uses json-repair if installed
- Returns clean dictionaries instead of crashing
"""

import os
import json
import re
import time
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types



try:
    from json_repair import repair_json
    HAS_JSON_REPAIR = True
except ImportError:
    HAS_JSON_REPAIR = False


load_dotenv()


def get_model_name() -> str:
    """
    Reads the Gemini model from .env.

    Example:
    GEMINI_MODEL=gemini-2.5-flash
    """
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def get_client() -> genai.Client:
    """
    Creates a Gemini client using GEMINI_API_KEY from .env.
    """

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing. Add it to your .env file.")

    return genai.Client(api_key=api_key)


def clean_json_text(text: str) -> str:
    """
    Removes markdown code fences if Gemini returns:

    ```json
    {...}
    ```
    """

    text = text.strip()

    match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return text


def repair_invalid_json_backslashes(text: str) -> str:
    r"""
    Fixes invalid JSON escape errors caused by LaTeX.

    Gemini may return LaTeX like:
    \omega
    \infty
    \text
    \pi

    In JSON, single backslash is only valid before:
    ", \, /, b, f, n, r, t, u

    So this function doubles invalid backslashes.
    """

    return re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', text)


def safe_json_loads(raw_text: str) -> Dict[str, Any]:
    """
    Safely parses Gemini JSON.

    Order:
    1. Normal json.loads
    2. Repair LaTeX backslashes, then json.loads
    3. json-repair package
    """

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

        try:
            repaired_text = repair_json(cleaned)
            return json.loads(repaired_text)
        except Exception:
            pass

    raise ValueError("Could not parse Gemini response as JSON.")


def is_quota_error(error_text: str) -> bool:
    """
    Detects 429 quota/rate-limit errors.

    We do NOT retry quota errors many times because it wastes requests.
    """

    error_text = error_text.lower()

    return (
        "429" in error_text
        or "resource_exhausted" in error_text
        or "quota exceeded" in error_text
        or "rate limit" in error_text
    )


def is_temporary_server_error(error_text: str) -> bool:
    """
    Detects temporary Gemini server overload.
    """

    error_text = error_text.lower()

    return (
        "503" in error_text
        or "unavailable" in error_text
        or "high demand" in error_text
        or "temporarily" in error_text
    )


def build_error_response(
    message: str,
    model_name: str,
    error_text: str
) -> Dict[str, Any]:
    """
    Returns a clean error dictionary instead of crashing.
    """

    return {
        "type": "error",
        "message": message,
        "model_used": model_name,
        "error": error_text,
        "api_fallback": False,
        "suggestion": (
            "If this is a 429 quota error, wait before testing again or use a key/project with available quota. "
            "If this is a 503 high-demand error, retry later or reduce the number of Gemini calls."
        )
    }


def ask_gemini_text(
    prompt: str,
    system_instruction: Optional[str] = None,
    max_output_tokens: int = 4096,
    temperature: float = 0.7,
    retries: int = 1
) -> str:
    """
    Sends a text prompt to Gemini and returns plain text.

    Important:
    - retries is 1 by default to avoid burning quota.
    - 429 quota errors are not retried repeatedly.
    """

    client = get_client()
    model_name = get_model_name()

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        max_output_tokens=max_output_tokens,
        temperature=temperature
    )

    last_error = ""

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )

            return response.text or ""

        except Exception as error:
            last_error = str(error)

            print(f"[Gemini warning] Model failed: {model_name}")
            print(f"[Gemini warning] Attempt {attempt + 1}/{retries}")
            print(f"[Gemini warning] Error: {last_error}")

            if is_quota_error(last_error):
                return (
                    "Gemini quota/rate limit reached. "
                    "Stop testing for now and retry later. "
                    f"Error: {last_error}"
                )

            if attempt < retries - 1 and is_temporary_server_error(last_error):
                wait_time = 3
                print(f"[Gemini warning] Waiting {wait_time} seconds...")
                time.sleep(wait_time)

    return (
        "Gemini is temporarily unavailable. "
        f"Last error: {last_error}"
    )


def ask_gemini_json(
    prompt: str,
    system_instruction: Optional[str] = None,
    max_output_tokens: int = 4096,
    temperature: float = 0.7,
    retries: int = 1
) -> Dict[str, Any]:
    """
    Sends a prompt to Gemini and requests JSON output.

    Important:
    - Uses only one model from GEMINI_MODEL.
    - Retries are low to protect quota.
    - 429 quota errors are not retried repeatedly.
    - Repairs LaTeX backslashes before json.loads.
    - Uses json-repair for extra safety.
    - Always returns a dictionary.
    """

    client = get_client()
    model_name = get_model_name()

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        response_mime_type="application/json"
    )

    last_error = ""

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )

            raw_text = response.text or ""

            try:
                parsed = safe_json_loads(raw_text)
                parsed["_model_used"] = model_name
                parsed["api_fallback"] = False
                return parsed

            except Exception as parse_error:
                return {
                    "type": "error",
                    "message": "Gemini response could not be parsed as JSON even after repair.",
                    "model_used": model_name,
                    "raw_response": raw_text,
                    "error": str(parse_error),
                    "api_fallback": False
                }

        except Exception as error:
            last_error = str(error)

            print(f"[Gemini warning] Model failed: {model_name}")
            print(f"[Gemini warning] Attempt {attempt + 1}/{retries}")
            print(f"[Gemini warning] Error: {last_error}")

            if is_quota_error(last_error):
                return build_error_response(
                    message="Gemini quota/rate limit reached. Stop running full tests for now.",
                    model_name=model_name,
                    error_text=last_error
                )

            if attempt < retries - 1 and is_temporary_server_error(last_error):
                wait_time = 3
                print(f"[Gemini warning] Waiting {wait_time} seconds...")
                time.sleep(wait_time)

    return build_error_response(
        message="Gemini API call failed.",
        model_name=model_name,
        error_text=last_error
    )