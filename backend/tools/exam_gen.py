"""
exam_gen.py

SigmaTutor Exam Generator Tool.

Creates custom practice exams for Signals & Systems
and Communication Engineering.

Uses:
- Gemini
- Optional RAG context from Person A's books, lectures, and previous exams
"""

from typing import Dict, Any, Optional

from langchain_groq import ChatGroq
from backend.tools.groq_client import ask_groq_json

SYSTEM_INSTRUCTION = """
You are SigmaTutor, an AI tutor specialized in Signals & Systems and Communication Engineering.

When generating exams:
- Make questions realistic for engineering students.
- Include step-by-step solutions.
- Use LaTeX for equations.
- Include final answers clearly.
- Avoid vague questions.
- Keep numerical values reasonable.
- If course context is provided, follow its style.
- For MCQs, include exactly 4 options and explain the correct answer.
- Do not copy long copyrighted passages from books or previous exams.

Important topic coverage:
Signals & Systems:
- continuous-time and discrete-time signals
- energy and power signals
- periodicity
- LTI systems
- impulse response
- convolution
- Fourier Series
- Fourier Transform
- Laplace Transform
- Z-transform
- sampling and aliasing
- frequency response and filters

Communication Engineering:
- AM, DSB-SC, SSB
- FM and PM
- ASK, FSK, PSK, QAM
- bandwidth
- SNR
- noise power
- Shannon capacity
- Nyquist rate
"""


ALLOWED_DIFFICULTIES = ["easy", "medium", "hard"]
ALLOWED_TYPES = ["mixed", "mcq", "short_problem", "derivation", "numerical"]


def generate_exam(
    topic: str,
    difficulty: str = "medium",
    num_questions: int = 5,
    question_type: str = "mixed",
    course_context: Optional[str] = None
) -> Dict[str, Any]:
    if not topic:
        return {
            "type": "error",
            "message": "Topic is required."
        }

    difficulty = difficulty.lower().strip()
    question_type = question_type.lower().strip()

    if difficulty not in ALLOWED_DIFFICULTIES:
        difficulty = "medium"

    if question_type not in ALLOWED_TYPES:
        question_type = "mixed"

    try:
        num_questions = int(num_questions)
    except (TypeError, ValueError):
        num_questions = 5

    num_questions = max(1, min(num_questions, 10))

    prompt = f"""
Generate a practice exam for an engineering student.

Topic: {topic}
Difficulty: {difficulty}
Number of questions: {num_questions}
Question type: {question_type}

Course context from RAG, books, lectures, or previous exams:
{course_context if course_context else "No extra course context provided."}

Return ONLY valid JSON with this exact structure:

{{
  "type": "exam",
  "topic": "...",
  "difficulty": "...",
  "question_type": "...",
  "estimated_time_minutes": 0,
  "questions": [
    {{
      "question_number": 1,
      "type": "mcq | conceptual | numerical | derivation | interpretation",
      "question": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_answer": "...",
      "step_by_step_solution": ["...", "...", "..."],
      "final_answer": "...",
      "exam_tip": "..."
    }}
  ],
  "overall_study_tip": "..."
}}

Content requirements:
- If question_type = "mixed", create a balanced exam:
  1. At least one MCQ if num_questions >= 2.
  2. At least one numerical problem if num_questions >= 2.
  3. At least one conceptual or interpretation question if num_questions >= 3.
  4. At least one derivation question if num_questions >= 4.
- If question_type is not "mixed", keep all questions in that requested style.
- Include realistic engineering formulas and units.
- Include mistakes students commonly make.
- Include questions that test understanding, not only memorization.
- For Signals & Systems topics, include time-domain and frequency-domain thinking when relevant.
- For Communication Engineering topics, include bandwidth, SNR, modulation, or capacity when relevant.
- If previous exam context is provided, imitate its style without copying exact long wording.
- If no context is provided, generate a normal high-quality engineering practice set.

Rules:
- If the question is not MCQ, use an empty list for "options".
- Every question must have a complete solution.
- Use LaTeX where useful.
"""

    result = ask_gemini_json(
        prompt=prompt,
        system_instruction=SYSTEM_INSTRUCTION,
        max_output_tokens=8192,
        temperature=0.75
    )

    if result.get("type") == "error":
        return result

    result.setdefault("type", "exam")
    result.setdefault("topic", topic)
    result.setdefault("difficulty", difficulty)
    result.setdefault("question_type", question_type)
    result.setdefault("used_course_context", bool(course_context))

    return result


if __name__ == "__main__":
    output = generate_exam(
        topic="Sampling and Aliasing",
        difficulty="medium",
        num_questions=4,
        question_type="mixed"
    )
    print(output)