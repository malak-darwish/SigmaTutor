import json

from tools.knowledge_router import route_knowledge_tool


def print_result(title, result):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    print("\nRunning final Person C smoke test...")

    # Test 1: Calculator through router, no Gemini needed
    calc_result = route_knowledge_tool(
        "shannon_capacity",
        bandwidth_hz=3000,
        snr_db=20
    )

    print_result("Test 1 — Router Calculator: Shannon Capacity", calc_result)

    if calc_result.get("type") != "calculation":
        print("\n❌ Calculator test failed.")
        return

    # Test 2: Concept explainer through router with fake RAG context
    concept_result = route_knowledge_tool(
        "concept",
        topic="Fourier Transform",
        level="beginner",
        course_context=(
            "Course context: Fourier Transform converts signals from time domain "
            "to frequency domain. It is used to analyze spectra, filters, and "
            "communication systems."
        )
    )

    print_result("Test 2 — Router Concept Explainer With Course Context", concept_result)

    if concept_result.get("type") == "concept_explanation":
        print("\n✅ FINAL TEST PASSED: Person C tools are working and integration-ready.")
        return

    if concept_result.get("type") == "error":
        print("\n⚠️ Gemini returned an API/quota/high-demand error, but the code handled it safely.")
        print("✅ Calculator/router part passed. Gemini availability depends on API quota.")
        return

    print("\n⚠️ Test finished with unexpected output type, check the printed result.")


if __name__ == "__main__":
    main()