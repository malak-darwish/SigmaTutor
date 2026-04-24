import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from backend.rag import search_documents, format_search_results

# Load environment variables
load_dotenv()

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
   model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
)

# Conversation history
chat_history = []

# ── TOOL FUNCTIONS 

def rag_search(query: str) -> str:
    """Search lecture PDFs and course materials"""
    results = search_documents(query)
    return format_search_results(results)

def calculate(problem: str) -> str:
    """Solve math problems using WolframAlpha"""
    try:
        import wolframalpha
        app_id = os.getenv("WOLFRAM_APP_ID")
        if not app_id or app_id == "get_later":
            return f"WolframAlpha not configured. Please solve: {problem}"
        client = wolframalpha.Client(app_id)
        res = client.query(problem)
        answer = next(res.results).text
        return f"Solution: {answer}"
    except Exception as e:
        return f"Calculation error: {str(e)}"

def web_search(query: str) -> str:
    """Search the web for current information"""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        if not results:
            return "No results found."
        formatted = ""
        for r in results:
            formatted += f"Title: {r['title']}\n"
            formatted += f"Summary: {r['body']}\n\n"
        return formatted
    except Exception as e:
        return f"Web search error: {str(e)}"

def plot_signal(description: str) -> str:
    """Plot signals from description"""
    try:
        from backend.tools.plotter import plot_signal as _plot
        result = _plot(description)
        return result
    except Exception as e:
        return f"Plot error: {str(e)}"

def generate_matlab(request: str) -> str:
    """Generate MATLAB code"""
    try:
        from backend.tools.matlab_gen import generate_matlab_code
        result = generate_matlab_code(request)
        return result
    except Exception as e:
        return f"MATLAB generation error: {str(e)}"

def generate_exam(request: str) -> str:
    """Generate exam questions"""
    try:
        from backend.tools.exam_gen import generate_exam as _exam
        result = _exam(request)
        return result
    except Exception as e:
        return f"Exam generation error: {str(e)}"

def prove_formula(request: str) -> str:
    """Prove or derive formulas step by step"""
    try:
        from backend.tools.prover import prove_formula as _prove
        result = _prove(request)
        return result
    except Exception as e:
        return f"Proof error: {str(e)}"

def generate_diagram(request: str) -> str:
    """Generate block diagrams"""
    try:
        from backend.tools.diagram_gen import generate_diagram as _diagram
        result = _diagram(request)
        return result
    except Exception as e:
        return f"Diagram error: {str(e)}"

def explain_concept(request: str) -> str:
    """Explain concepts step by step"""
    try:
        from backend.tools.concept_explainer import explain_concept as _explain
        result = _explain(request)
        return result
    except Exception as e:
        return f"Explanation error: {str(e)}"

def frequency_sandbox(request: str) -> str:
    """Interactive frequency domain exploration"""
    try:
        from backend.tools.frequency_sandbox import run_sandbox
        result = run_sandbox(request)
        return result
    except Exception as e:
        return f"Sandbox error: {str(e)}"

# ── TOOLS LIST 

tools = [
    Tool(
        name="RAG_Search",
        func=rag_search,
        description="Search course lectures, textbooks, past exams. Use for course-specific questions about Signals & Systems or Communications Systems."
    ),
    Tool(
        name="Calculator",
        func=calculate,
        description="Solve mathematical problems step by step. Use for numerical calculations, Fourier transforms, SNR, bandwidth, Nyquist rate."
    ),
    Tool(
        name="Web_Search",
        func=web_search,
        description="Search the internet for current information or topics not in course materials."
    ),
    Tool(
        name="Signal_Plotter",
        func=plot_signal,
        description="Plot signals in time and frequency domain from a text description."
    ),
    Tool(
        name="MATLAB_Generator",
        func=generate_matlab,
        description="Generate clean commented MATLAB code for signals and communications tasks."
    ),
    Tool(
        name="Exam_Generator",
        func=generate_exam,
        description="Generate exam questions with solutions based on topic and difficulty."
    ),
    Tool(
        name="Formula_Prover",
        func=prove_formula,
        description="Prove or derive mathematical formulas step by step with LaTeX."
    ),
    Tool(
        name="Diagram_Generator",
        func=generate_diagram,
        description="Generate block diagrams for LTI systems, receivers, filters, etc."
    ),
    Tool(
        name="Concept_Explainer",
        func=explain_concept,
        description="Explain concepts step by step with examples at the student's level."
    ),
    Tool(
        name="Frequency_Sandbox",
        func=frequency_sandbox,
        description="Interactive tool to explore signals in time and frequency domain."
    ),
]

# ── SYSTEM PROMPT 

SYSTEM_PROMPT = """You are SigmaTutor, an expert AI tutor specializing in Signals & Systems and Communications Systems. You have access to course materials, past exams, and powerful tools.

You can help with:
- Explaining concepts in Signals & Systems and Communications
- Solving problems step by step
- Generating and plotting signals
- Writing MATLAB code
- Creating practice exams
- Proving and deriving formulas
- Drawing block diagrams
- Answering general questions about any topic including AI and LLMs

Always search course materials first for course-specific questions.
Be encouraging, educational, and show step-by-step solutions."""

# ── CREATE AGENT

agent = create_react_agent(
    llm,
    tools,
    prompt=SYSTEM_PROMPT
)
# ── MAIN FUNCTION 
def run_agent(user_message: str) -> dict:
    """Main function to run the agent"""
    try:
        chat_history.append(HumanMessage(content=user_message))
        
        response = agent.invoke({
            "messages": chat_history
        })
        
        # Get the last message content
        messages = response["messages"]
        ai_message = None
        
        for msg in reversed(messages):
            if hasattr(msg, 'content') and msg.content:
                content = msg.content
                # Handle list format
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
        
        return {
            "success": True,
            "response": ai_message
        }
    except Exception as e:
        return {
            "success": False,
            "response": f"Error: {str(e)}"
        }
    
def clear_memory():
    """Clear conversation history"""
    chat_history.clear()

# ── TEST

if __name__ == "__main__":
    print("Testing SigmaTutor Agent...")
    print("=" * 50)
    response = run_agent("What is the Fourier Transform?")
    print(f"Response: {response['response']}")