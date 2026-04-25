"""
wolfram_client.py

WolframAlpha helper for SigmaTutor.

Used by:
- calculator.py
- prover.py

Purpose:
- Verify numerical calculations
- Give symbolic/math verification support
- Add a second computational source besides Gemini
"""

import os
from typing import Dict, Any, List

import requests
from dotenv import load_dotenv


load_dotenv()


def get_wolfram_app_id() -> str:
    """
    Reads WolframAlpha AppID from .env.
    """

    return os.getenv("WOLFRAM_APP_ID", "").strip()


def is_wolfram_configured() -> bool:
    """
    Checks whether the WolframAlpha key exists.
    """

    return bool(get_wolfram_app_id())


def query_wolfram(query: str) -> Dict[str, Any]:
    """
    Sends a query to WolframAlpha Full Results API.

    Returns a simplified dictionary with plaintext pods.
    """

    if not query:
        return {
            "type": "wolfram_error",
            "success": False,
            "query": query,
            "message": "Query is required.",
            "pods": []
        }

    app_id = get_wolfram_app_id()

    if not app_id:
        return {
            "type": "wolfram_unavailable",
            "success": False,
            "query": query,
            "message": "WOLFRAM_APP_ID is missing. Add it to your .env file.",
            "pods": []
        }

    try:
        url = "https://api.wolframalpha.com/v2/query"

        params = {
            "appid": app_id,
            "input": query,
            "output": "json",
            "format": "plaintext"
        }

        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        query_result = data.get("queryresult", {})

        if not query_result.get("success"):
            return {
                "type": "wolfram_result",
                "success": False,
                "query": query,
                "message": "WolframAlpha could not compute a clear result.",
                "pods": []
            }

        pods = []

        for pod in query_result.get("pods", []):
            pod_title = pod.get("title", "")

            for subpod in pod.get("subpods", []):
                plaintext = subpod.get("plaintext", "")

                if plaintext:
                    pods.append({
                        "title": pod_title,
                        "plaintext": plaintext
                    })

        return {
            "type": "wolfram_result",
            "success": True,
            "query": query,
            "pods": pods
        }

    except Exception as error:
        return {
            "type": "wolfram_error",
            "success": False,
            "query": query,
            "message": str(error),
            "pods": []
        }


def get_best_wolfram_plaintext(query: str, max_items: int = 5) -> List[str]:
    """
    Returns only the most useful plaintext outputs from WolframAlpha.

    This keeps the frontend output clean.
    """

    result = query_wolfram(query)

    if not result.get("success"):
        return []

    outputs = []

    for pod in result.get("pods", [])[:max_items]:
        title = pod.get("title", "Result")
        plaintext = pod.get("plaintext", "")

        if plaintext:
            outputs.append(f"{title}: {plaintext}")

    return outputs


def wolfram_verification_block(query: str, max_items: int = 5) -> Dict[str, Any]:
    """
    Returns a clean verification block that can be included in tool outputs.
    """

    result = query_wolfram(query)

    if not result.get("success"):
        return {
            "enabled": is_wolfram_configured(),
            "query": query,
            "status": "unavailable_or_no_result",
            "results": [],
            "message": result.get("message", "No WolframAlpha verification available.")
        }

    simplified = []

    for pod in result.get("pods", [])[:max_items]:
        title = pod.get("title", "Result")
        plaintext = pod.get("plaintext", "")

        if plaintext:
            simplified.append({
                "title": title,
                "plaintext": plaintext
            })

    return {
        "enabled": True,
        "query": query,
        "status": "verified",
        "results": simplified,
        "message": "WolframAlpha verification completed."
    }


if __name__ == "__main__":
    print(wolfram_verification_block("3000 * log2(1 + 10^(20/10))"))