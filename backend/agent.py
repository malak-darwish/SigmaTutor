import os
from dotenv import load_dotenv
from langchain_core.tools import StructuredTool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from pydantic import BaseModel
from typing import List, Optional
from backend.rag import search_documents, format_search_results

load_dotenv()

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

chat_history = []

# ── ROUTING PATTERNS ──────────────────────────────────────────────────────────

TOOL_PATTERNS = [
    "plot", "show signal", "graph", "draw signal",
    "matlab", "code", "script", "function",
    "block diagram", "draw system", "draw a",
    "exam", "quiz", "test questions", "practice questions",
    "prove", "derive", "derivation", "proof",
    "calculate", "compute", "find the value",
    "from lectures", "from textbook", "course material",
    "sandbox", "frequency sandbox", "build signal",
    "write me", "generate me",
]


def needs_tool(message: str) -> bool:
    msg = message.lower()
    return any(p in msg for p in TOOL_PATTERNS)


# ── SCHEMAS ───────────────────────────────────────────────────────────────────

class Signal(BaseModel):
    signal_type: str = "sine"
    frequency:   float = 1.0
    amplitude:   float = 1.0
    phase_deg:   float = 0.0
    t_start:     float = 0.0
    t_end:       float = 1.0
    sample_rate: float = 1000.0

    class Config:
        extra = "allow"


class PlotInput(BaseModel):
    operation: str = "plot"
    signals:   List[Signal]
    freq_min:  Optional[float] = None
    freq_max:  Optional[float] = None

    class Config:
        extra = "allow"


class InputSchema(BaseModel):
    query: str = ""

    class Config:
        extra = "allow"


# ── TOOL FUNCTIONS ────────────────────────────────────────────────────────────

def rag_search(query: str) -> str:
    results = search_documents(query)
    return format_search_results(results)


def calculate(query: str) -> str:
    try:
        import wolframalpha
        app_id = os.getenv("WOLFRAM_APP_ID")
        if not app_id or app_id == "get_later":
            return f"WolframAlpha not configured. Please solve: {query}"
        client = wolframalpha.Client(app_id)
        res    = client.query(query)
        answer = next(res.results).text
        return f"Solution: {answer}"
    except Exception as e:
        return f"Calculation error: {str(e)}"


def web_search(query: str) -> str:
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=2))
        if not results:
            return "No results found."
        formatted = ""
        for r in results:
            formatted += f"{r['title']}: {r['body'][:300]}\n\n"
        return formatted
    except Exception as e:
        return f"Web search error: {str(e)}"


def plot_signal_tool(query: str) -> str:
    try:
        if not query or query.strip() == '':
            query = "plot a 10Hz sine wave"
        from backend.tools.plotter import plot_signal
        return plot_signal(description=query, llm=llm)  # ← pass llm
    except Exception as e:
        return f"Plot error: {str(e)}"


def generate_matlab(query: str) -> str:
    try:
        print(f"DEBUG WRAPPER: generate_matlab called with query='{query}'")  # ← add
        if not query or query.strip() == '':
            query = "plot a 10Hz sine wave"
        from backend.tools.matlab_gen import generate_matlab as _matlab
        return _matlab(task=query, llm=llm)
    except Exception as e:
        print(f"DEBUG WRAPPER ERROR: {str(e)}")  # ← add
        return f"MATLAB generation error: {str(e)}"


def generate_exam(query: str = "", **kwargs) -> str:
    try:
        if not query:
            query = (
                kwargs.get('topic', '') or
                kwargs.get('exam_type', '') or
                kwargs.get('subject', '') or
                kwargs.get('name', '') or
                "Fourier Transform medium difficulty"
            )
        from backend.tools.exam_gen import generate_exam as _exam
        result = _exam(topic=query)
        return str(result)
    except Exception as e:
        return f"Exam generation error: {str(e)}"


def prove_formula(query: str = "", **kwargs) -> str:
    try:
        if not query:
            query = (
                kwargs.get('formula', '') or
                kwargs.get('theorem', '') or
                kwargs.get('name', '') or
                kwargs.get('formula_or_theorem', '') or
                "Parseval theorem"
            )
        formula = query.replace("Prove ", "").replace("Derive ", "").strip()
        from backend.tools.prover import prove_formula as _prove
        result = _prove(formula_or_theorem=formula)
        return str(result)
    except Exception as e:
        return f"Proof error: {str(e)}"


def generate_diagram(query: str) -> str:
    try:
        if not query or query.strip() == '':
            query = "simple block diagram"
        from backend.tools.diagram_gen import generate_diagram as _diagram
        return _diagram(system_description=query)
    except Exception as e:
        return f"Diagram error: {str(e)}"


def explain_concept(query: str = "", **kwargs) -> str:
    try:
        if not query:
            query = (
                kwargs.get('topic', '') or
                kwargs.get('concept', '') or
                kwargs.get('name', '') or
                kwargs.get('subject', '') or
                "Fourier Transform"
            )
        topic = query.replace("Explain ", "").replace(" in detail", "").strip()
        from backend.tools.concept_explainer import explain_concept as _explain
        result = _explain(topic=topic)
        return str(result)
    except Exception as e:
        return f"Explanation error: {str(e)}"


def frequency_sandbox(query: str) -> str:
    try:
        from backend.tools.frequency_sandbox import run_sandbox
        return run_sandbox(instruction=query, llm=llm)  # ← pass llm
    except Exception as e:
        return f"Sandbox error: {str(e)}"


# ── TOOLS LIST ────────────────────────────────────────────────────────────────

tools = [
    StructuredTool.from_function(
        func=rag_search,
        name="RAG_Search",
        description="Search course lectures and textbooks for signals & systems content.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=calculate,
        name="Calculator",
        description="Calculate using WolframAlpha. Good for Nyquist rate, Shannon capacity, SNR, bandwidth.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=plot_signal_tool,
        name="Signal_Plotter",
        description=(
        "Plot signals in time and frequency domain from natural language. "
        "Supports: sine, cosine, square, sawtooth, triangle, rect, impulse, step, comb, chirp. "
        "Supports operations: plot, add, multiply, convolve."
        ),
        args_schema=InputSchema  # ← back to simple InputSchema
    ),
    StructuredTool.from_function(
        func=generate_matlab,
        name="MATLAB_Generator",
        description="Generate MATLAB code. Input: query (string) describing the task.",
        args_schema=InputSchema
),
    StructuredTool.from_function(
        func=generate_exam,
        name="Exam_Generator",
        description="Generate exam questions and quizzes about signals and systems topics.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=prove_formula,
        name="Formula_Prover",
        description="Prove or derive mathematical formulas and theorems step by step with LaTeX.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=generate_diagram,
        name="Diagram_Generator",
        description="Generate Mermaid block diagrams for systems like AM modulator, receiver, LTI systems.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=explain_concept,
        name="Concept_Explainer",
        description="Explain signals and systems concepts in detail with examples and LaTeX math.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=frequency_sandbox,
        name="Frequency_Sandbox",
        description="Interactive frequency domain sandbox. Build and modify signals step by step.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=web_search,
        name="Web_Search",
        description="Search the internet for current information.",
        args_schema=InputSchema
    ),
]

# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are SigmaTutor, an AI tutor for Signals, Systems and Communications.

FORMATTING: Use LaTeX for math. Inline: $formula$. Display: $$formula$$

TOOL RULES — call tool ONCE then STOP:
- "matlab" or "code" or "script"   → call MATLAB_Generator ONCE then STOP
- "plot" or "show signal"          → call Signal_Plotter ONCE then STOP
- "block diagram" or "draw"        → call Diagram_Generator ONCE then STOP
- "exam" or "quiz"                 → call Exam_Generator ONCE then STOP
- "prove" or "derive"              → call Formula_Prover ONCE then STOP
- "from lectures" or "textbook"    → call RAG_Search ONCE then STOP
- "calculate" or "compute"         → call Calculator ONCE then STOP
- "explain in detail"              → call Concept_Explainer ONCE then STOP
- "sandbox" or "build signal"      → call Frequency_Sandbox ONCE then STOP

STRICT RULES:
- Call ONE tool ONCE per request
- After tool returns result, immediately return it to the user
- NEVER call the same tool twice
- NEVER call multiple tools for one request
- Return tool output EXACTLY as received

For theory questions with no tool: answer directly with LaTeX."""

# ── CREATE AGENT ──────────────────────────────────────────────────────────────

agent = create_react_agent(
    llm,
    tools,
    prompt=SYSTEM_PROMPT
)

# ── DIRECT LLM (fast path) ────────────────────────────────────────────────────

DIRECT_LLM_PROMPT = """You are SigmaTutor, an AI tutor for Signals, Systems and Communications.
Answer clearly and concisely. Use LaTeX for math: inline $formula$, display $$formula$$.
Cover both intuition and mathematical formulation.
Mention common mistakes or exam tips where relevant."""


def _direct_answer(user_message: str) -> dict:
    """Answer directly without the agent loop — fast for general questions."""
    try:
        direct_llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3
        )
        response   = direct_llm.invoke([
            SystemMessage(content=DIRECT_LLM_PROMPT),
            HumanMessage(content=user_message)
        ])
        ai_message = response.content
        chat_history.append(AIMessage(content=ai_message))
        return {"success": True, "response": ai_message}
    except Exception as e:
        return {"success": False, "response": f"Error: {str(e)}"}


# ── MAIN FUNCTION ─────────────────────────────────────────────────────────────

def run_agent(user_message: str) -> dict:
    try:
        chat_history.append(HumanMessage(content=user_message))

        # ── FAST PATH: no tool needed ──────────────────────────────────────
        if not needs_tool(user_message):
            print("DEBUG: Fast path — direct LLM answer")
            return _direct_answer(user_message)

        # ── SLOW PATH: tool needed, use agent ─────────────────────────────
        print("DEBUG: Agent path — tool required")
        recent_history = chat_history[-4:]
        total_chars    = sum(len(str(m.content)) for m in recent_history)
        print(f"DEBUG: chars={total_chars}, ~tokens={total_chars // 4}")

        response   = agent.invoke(
            {"messages": recent_history},
            config={"recursion_limit":5} ##was  25
        )
        messages   = response["messages"]
        ai_message = None

        for msg in reversed(messages):
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                continue
            if hasattr(msg, 'type') and msg.type == 'tool':
                continue
            if str(type(msg).__name__) in ['ToolMessage', 'FunctionMessage']:
                continue
            if hasattr(msg, 'content') and msg.content:
                content = msg.content
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            ai_message = item['text']
                            break
                else:
                    ai_message = content
                if ai_message:
                    break

        if not ai_message:
            ai_message = "I processed your request but got an empty response. Please try again."

        chat_history.append(AIMessage(content=ai_message))
        return {"success": True, "response": ai_message}

    except Exception as e:
        error_msg = str(e)

        # Recursion/steps error → fallback to direct answer
        if any(x in error_msg.lower() for x in ["recursion", "steps", "graphrecursion"]):
            print("DEBUG: Recursion error — falling back to direct answer")
            return _direct_answer(user_message)

        # Tool call validation error → fallback
        if "tool_use_failed" in error_msg or "tool call validation failed" in error_msg:
            print("DEBUG: Tool error — falling back to direct answer")
            return _direct_answer(user_message)

        if "Request too large" in error_msg or "rate_limit_exceeded" in error_msg:
            return {"success": False, "response": "Request too large. Please try a shorter query."}

        return {"success": False, "response": f"Error: {error_msg}"}


def clear_memory():
    chat_history.clear()


if __name__ == "__main__":
    print("Testing SigmaTutor Agent...")
    print("=" * 50)
    response = run_agent("What is the Fourier Transform?")
    print(f"Success: {response['success']}")
    print(f"Response: {response['response'][:200]}")