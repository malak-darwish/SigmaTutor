"""
prover.py

SigmaTutor Formula Prover Tool.

Explains derivations and proofs step by step.

Uses:
- Gemini for derivation
- WolframAlpha for optional verification/context
- Optional RAG context from Person A
"""

from typing import Dict, Any, Optional

from tools.gemini_client import ask_gemini_json
from tools.wolfram_client import get_best_wolfram_plaintext


SYSTEM_INSTRUCTION = """
You are SigmaTutor, an AI tutor specialized in Signals & Systems and Communication Engineering.

When proving formulas:
- Start from the definition.
- Show clear mathematical steps.
- Use LaTeX.
- Explain each step in words.
- Mention assumptions.
- End with the final result.
- Keep it understandable for engineering students.
- If course context is provided, prioritize it.
- If WolframAlpha context is provided, use it only as verification/support.

Common derivations SigmaTutor should support:
Signals & Systems:
- convolution theorem
- time-shifting property of Fourier Transform
- frequency-shifting property of Fourier Transform
- scaling property
- Parseval theorem
- Fourier Transform of rectangular pulse
- Fourier Transform of impulse
- Fourier Transform of complex exponential
- LTI output relation y(t) = x(t) * h(t)
- frequency response relation Y(jω) = X(jω)H(jω)
- sampling theorem
- aliasing relation

Communication Engineering:
- AM modulation spectrum
- DSB-SC spectrum
- SSB bandwidth reasoning
- FM instantaneous frequency
- Shannon capacity formula interpretation
- Nyquist rate reasoning
"""


def prove_formula(
    formula_or_theorem: str,
    level: str = "intermediate",
    course_context: Optional[str] = None,
    use_wolfram: bool = True
) -> Dict[str, Any]:
    if not formula_or_theorem:
        return {
            "type": "error",
            "message": "Formula or theorem is required."
        }

    wolfram_context = []

    if use_wolfram:
        wolfram_context = get_best_wolfram_plaintext(
            formula_or_theorem,
            max_items=5
        )

    prompt = f"""
Derive or prove the following formula/theorem.

Formula or theorem: {formula_or_theorem}
Student level: {level}

Course context from RAG, books, lectures, or previous exams:
{course_context if course_context else "No extra course context provided."}

WolframAlpha verification/context:
{wolfram_context if wolfram_context else "No WolframAlpha verification available."}

Return ONLY valid JSON with this exact structure:

{{
  "type": "formula_proof",
  "title": "...",
  "level": "...",
  "category": "Signals & Systems | Communication Engineering",
  "goal": "...",
  "assumptions": ["...", "..."],
  "starting_definition_latex": "...",
  "derivation_steps": [
    {{
      "step_number": 1,
      "explanation": "...",
      "latex": "..."
    }}
  ],
  "final_result_latex": "...",
  "why_it_matters": "...",
  "common_exam_mistake": "...",
  "memory_tip": "...",
  "related_formulas": ["...", "..."]
}}

Rules:
- Use LaTeX for formulas.
- Do not skip important mathematical steps.
- Start from the relevant definition whenever possible.
- Explain why each manipulation is allowed.
- Mention assumptions such as convergence, LTI system behavior, or bandwidth limits when relevant.
- If course context is given, align with it.
- WolframAlpha is only support; do not blindly copy irrelevant output.
- Keep the proof understandable for an engineering student.
"""

    result = ask_gemini_json(
        prompt=prompt,
        system_instruction=SYSTEM_INSTRUCTION,
        max_output_tokens=8192,
        temperature=0.45
    )

    if result.get("type") == "error":
        return result

    result.setdefault("type", "formula_proof")
    result.setdefault("title", formula_or_theorem)
    result.setdefault("level", level)
    result["used_course_context"] = bool(course_context)
    result["wolfram_verification"] = wolfram_context

    return result


if __name__ == "__main__":
    output = prove_formula("Convolution theorem for Fourier Transform")
    print(output)