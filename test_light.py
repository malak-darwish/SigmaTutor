"""
test_person_c_light.py

Light test for Person C tools.

This avoids burning Gemini quota by making only ONE Gemini call.
"""

import json

from tools.calculator import shannon_capacity, nyquist_rate
from tools.concept_explainer import explain_concept


def pretty_print(title, data):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    pretty_print(
        "Calculator Test — Shannon Capacity",
        shannon_capacity(3000, 20)
    )

    pretty_print(
        "Calculator Test — Nyquist Rate",
        nyquist_rate(4000)
    )

    # Only ONE Gemini request
    pretty_print(
        "Gemini Test — Concept Explainer",
        explain_concept("Fourier Transform", "beginner")
    )