import os
from dotenv import load_dotenv
from langchain_core.tools import StructuredTool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from pydantic import BaseModel
from backend.rag import search_documents, format_search_results

load_dotenv()

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    api_key=os.getenv("GROQ_API_KEY")
)

chat_history = []

# ── TOOL FUNCTIONS

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
        res = client.query(query)
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

def plot_signal(query: str) -> str:
    try:
        if not query or query.strip() == '':
            query = "10Hz sine wave"
        from backend.tools.plotter import plot_signal as _plot
        return _plot(query)
    except Exception as e:
        return f"Plot error: {str(e)}"

def generate_matlab(query: str) -> str:
    try:
        if not query or query.strip() == '':
            query = "sine wave"
        from backend.tools.matlab_gen import generate_matlab as _matlab
        return _matlab(query)
    except Exception as e:
        return f"MATLAB generation error: {str(e)}"

def generate_exam(query: str) -> str:
    try:
        if not query or query.strip() == '':
            query = "Fourier Transform medium difficulty"
        from backend.tools.exam_gen import generate_exam as _exam
        result = _exam(query)
        return str(result)
    except Exception as e:
        return f"Exam generation error: {str(e)}"

def prove_formula(query: str) -> str:
    try:
        if not query or query.strip() == '':
            query = "Parseval theorem"
        from backend.tools.prover import prove_formula as _prove
        result = _prove(query)
        return str(result)
    except Exception as e:
        return f"Proof error: {str(e)}"

def generate_diagram(query: str) -> str:
    try:
        if not query or query.strip() == '':
            query = "simple block diagram"
        from backend.tools.diagram_gen import generate_diagram as _diagram
        return _diagram(query)
    except Exception as e:
        return f"Diagram error: {str(e)}"

def explain_concept(query: str) -> str:
    try:
        if not query or query.strip() == '':
            query = "Fourier Transform"
        from backend.tools.concept_explainer import explain_concept as _explain
        result = _explain(query)
        return str(result)
    except Exception as e:
        return f"Explanation error: {str(e)}"

def frequency_sandbox(query: str) -> str:
    try:
        from backend.tools.frequency_sandbox import run_sandbox
        return run_sandbox(query)
    except Exception as e:
        return f"Sandbox error: {str(e)}"

# ── SCHEMA

class InputSchema(BaseModel):
    query: str

# ── TOOLS LIST

tools = [
    StructuredTool.from_function(
        func=rag_search,
        name="RAG_Search",
        description="Search course lectures, textbooks, past exams for Signals and Systems or Communications questions.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=calculate,
        name="Calculator",
        description="Solve math problems step by step. Use for SNR, bandwidth, Nyquist rate calculations.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=web_search,
        name="Web_Search",
        description="Search internet for current information.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=plot_signal,
        name="Signal_Plotter",
        description="Plot signals in time and frequency domain from text description.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=generate_matlab,
        name="MATLAB_Generator",
        description="Generate clean commented MATLAB code for signals and communications tasks.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=generate_exam,
        name="Exam_Generator",
        description="Generate exam questions with solutions based on topic and difficulty.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=prove_formula,
        name="Formula_Prover",
        description="Prove or derive mathematical formulas step by step with LaTeX.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=generate_diagram,
        name="Diagram_Generator",
        description="Generate Mermaid block diagrams for signals and systems.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=explain_concept,
        name="Concept_Explainer",
        description="Explain concepts step by step with examples.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=frequency_sandbox,
        name="Frequency_Sandbox",
        description="Interactive tool to explore signals in time and frequency domain.",
        args_schema=InputSchema
    ),
]

# ── SYSTEM PROMPT

SYSTEM_PROMPT = """You are SigmaTutor, an expert AI tutor specializing in Signals and Systems and Communications Systems.

FORMATTING RULES:
- Always use LaTeX for ALL mathematical formulas
- Inline math: $formula$ e.g. $x(t) = A\\sin(2\\pi ft)$
- Display math: $$formula$$ on its own line
- NEVER write math as plain text

TOOL RULES - MANDATORY:
- PLOT request → use Signal_Plotter immediately
- MATLAB request → use MATLAB_Generator immediately
- DIAGRAM or DRAW request → use Diagram_Generator immediately
- EXAM or QUESTIONS request → use Exam_Generator immediately
- PROVE or DERIVE request → use Formula_Prover immediately
- Course specific question → use RAG_Search
- Current or recent info → use Web_Search
- General explanation → answer directly with LaTeX

CRITICAL: When calling tools use ONLY simple plain text in query. NO LaTeX, NO special characters.
CRITICAL: After using a tool always provide complete natural language response based on result.
CRITICAL: Never show raw tool calls or XML tags in your response.

Be concise, educational, and encouraging."""

# ── CREATE AGENT

agent = create_react_agent(
    llm,
    tools,
    prompt=SYSTEM_PROMPT
)

# ── MAIN FUNCTION

def run_agent(user_message: str) -> dict:
    try:
        chat_history.append(HumanMessage(content=user_message))

        # Keep only last 4 messages to minimize tokens
        recent_history = chat_history[-2:]

        response = agent.invoke(
            {"messages": recent_history},
            config={"recursion_limit": 10}
        )
        messages = response["messages"]
        ai_message = None

        for msg in reversed(messages):
            # Skip tool call messages
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
        return {"success": False, "response": f"Error: {str(e)}"}


def clear_memory():
    chat_history.clear()


if __name__ == "__main__":
    print("Testing SigmaTutor Agent...")
    print("=" * 50)
    response = run_agent("What is the Fourier Transform?")
    print(f"Response: {response['response']}")