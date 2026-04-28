"""
concept_explainer.py

SigmaTutor Concept Explainer Tool.

This tool explains Signals & Systems and Communication Engineering concepts
in a structured student-friendly format.

Uses:
- Gemini
- Optional RAG context from Person A
"""

from typing import Dict, Any, Optional

from langchain_groq import ChatGroq
from backend.tools.groq_client import ask_groq_json

SYSTEM_INSTRUCTION = """
You are SigmaTutor, an AI tutor specialized in Signals & Systems and Communication Engineering.

Your style:
- Clear and student-friendly
- Engineering-focused
- Explain simply first, then mathematically
- Use LaTeX for mathematical formulas
- Give useful examples
- Mention common exam mistakes
- Do not invent textbook page numbers
- If course context is provided, prioritize it
"""


def explain_concept(
    topic: str,
    level: str = "beginner",
    course_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Explains a concept in a clean JSON format.

    Parameters:
    - topic: e.g. "convolution", "Fourier transform", "AM modulation"
    - level: beginner, intermediate, advanced
    - course_context: optional retrieved text from Person A's RAG system

    Returns:
    dictionary ready for FastAPI/frontend
    """

    if not topic:
        return {
            "type": "error",
            "message": "Topic is required."
        }

    prompt = f"""
Explain the following topic for an engineering student.

Topic: {topic}
Student level: {level}

Course context from RAG, books, lectures, or previous exams:
{course_context if course_context else "No extra course context provided."}

Return ONLY valid JSON with this exact structure:

{{
  "type": "concept_explanation",
  "title": "...",
  "level": "...",
  "simple_definition": "...",
  "intuition": "...",
  "key_formula_latex": "...",
  "step_by_step_explanation": ["...", "...", "..."],
  "example": {{
    "problem": "...",
    "solution": "...",
    "final_answer": "..."
  }},
  "common_exam_mistakes": ["...", "..."],
  "quick_memory_tip": "...",
  "related_topics": ["...", "..."]
}}

Rules:
- Use LaTeX where formulas are needed.
- Keep the explanation suitable for Signals & Systems or Communication Engineering.
- If course context is provided, use it to match the course style.
- If no context is provided, answer from general engineering knowledge.
"""

    result = ask_gemini_json(
        prompt=prompt,
        system_instruction=SYSTEM_INSTRUCTION,
        max_output_tokens=4096,
        temperature=0.6
    )

    if result.get("type") == "error":
        return result

    result.setdefault("type", "concept_explanation")
    result.setdefault("title", topic)
    result.setdefault("level", level)
    result.setdefault("used_course_context", bool(course_context))

    return result


if __name__ == "__main__":
    output = explain_concept("Convolution in Signals and Systems", "beginner")
    print(output)