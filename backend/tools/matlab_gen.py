"""
matlab_gen.py
SigmaTutor MATLAB Code Generator.
"""

from langchain_core.messages import HumanMessage, SystemMessage


def generate_matlab(task: str, llm) -> str:

    print(f"DEBUG MATLAB: generating for '{task}'")

    try:
        response = llm.invoke([
            SystemMessage(content="You are a MATLAB expert. Return a short explanation then MATLAB code in a ```matlab block."),
            HumanMessage(content=f"Write MATLAB code for: {task}")
        ])
        print("DEBUG MATLAB: done")
        return response.content.strip()

    except Exception as e:
        print(f"DEBUG MATLAB ERROR: {type(e).__name__} — {str(e)}")
        raise  # ← re-raise so agent.py catches it too