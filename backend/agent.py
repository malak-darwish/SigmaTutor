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
    model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),  # ← match .env
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
    query: str = ""
    
    class Config:
        extra = "allow"

# ── TOOLS LIST
tools = [
    StructuredTool.from_function(
        func=rag_search,
        name="RAG_Search",
        description="Search course lectures and textbooks.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=plot_signal,
        name="Signal_Plotter",
        description="Plot signals in time and frequency domain.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=generate_matlab,
        name="MATLAB_Generator",
        description="Generate MATLAB code for signals tasks.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=generate_diagram,
        name="Diagram_Generator",
        description="Generate Mermaid block diagrams.",
        args_schema=InputSchema
    ),
    StructuredTool.from_function(
        func=web_search,
        name="Web_Search",
        description="Search internet for current information.",
        args_schema=InputSchema
    ),
]

# ── SYSTEM PROMPT
SYSTEM_PROMPT = """You are SigmaTutor, an AI tutor for Signals, Systems and Communications.

FORMATTING: Always use LaTeX for math. Inline: $formula$. Display: $$formula$$

TOOLS - use immediately when requested:
- "matlab code" or "write script" → MATLAB_Generator
- "plot" or "show signal" → Signal_Plotter  
- "block diagram" or "draw system" → Diagram_Generator
- "exam questions" or "quiz" → Exam_Generator
- "prove" or "derive" → Formula_Prover
- "from lectures" or "course material" → RAG_Search
- "latest" or "current" → Web_Search
- "calculate" or "compute" → Calculator
- "explain in detail" → Concept_Explainer

TOOL QUERY: plain English only, no LaTeX, no special characters.

AFTER TOOL: return result exactly as-is. Never describe it.
For general questions: answer directly with LaTeX math.
Be concise and educational."""

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
        recent_history = chat_history[-2:]

        # Debug token count
        total_chars = sum(len(str(m.content)) for m in recent_history)
        print(f"DEBUG: messages chars={total_chars}, estimated tokens={total_chars//4}")
        response = agent.invoke(
            {"messages": recent_history},
            config={"recursion_limit": 50}
        )
        messages = response["messages"]
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
        
        # If tool call failed → retry without tools, answer directly
        if "tool_use_failed" in error_msg or "tool call validation failed" in error_msg:
            try:
                fallback_llm = ChatGroq(
                    model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
                    api_key=os.getenv("GROQ_API_KEY")
                )
                fallback_response = fallback_llm.invoke([
                    HumanMessage(content=f"Answer this question directly with LaTeX math formatting: {user_message}")
                ])
                ai_message = fallback_response.content
                chat_history.append(AIMessage(content=ai_message))
                return {"success": True, "response": ai_message}
            except Exception as e2:
                return {"success": False, "response": f"Error: {str(e2)}"}
        
        # Token limit error
        if "Request too large" in error_msg or "rate_limit_exceeded" in error_msg:
            return {"success": False, "response": "Request too large. Please try a shorter or simpler query."}
        
        return {"success": False, "response": f"Error: {error_msg}"}


def clear_memory():
    chat_history.clear()


if __name__ == "__main__":
    print("Testing SigmaTutor Agent...")
    print("=" * 50)
    response = run_agent("What is the Fourier Transform?")
    print(f"Response: {response['response']}")