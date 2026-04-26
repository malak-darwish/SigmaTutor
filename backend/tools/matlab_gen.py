from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=os.environ.get("GEMINI_MODEL"),
    api_key=os.environ.get("GOOGLE_API_KEY"),
    temperature=0.0
)


def generate_matlab_code(task: str) -> str:
    """
    Generates clean, commented MATLAB code for any signals and systems task.
    Automatically detects required toolboxes and structures code into clear sections.
    Always includes proper figure formatting for any plots.
    Args:
        task (str): A natural language description of the MATLAB task to generate code for
    Returns:
        str: Clean, commented MATLAB code that solves the given task
    """
    prompt = f"""
You are an expert in signals and systems and MATLAB programming.
The student asks: "{task}"

Generate clean, well-commented MATLAB code that solves this task.

Rules:
1. TOOLBOX DETECTION — automatically use the correct toolbox functions:
   - Signal processing tasks (filtering, FFT, convolution, windowing) → use Signal Processing Toolbox: butter, fft, freqz, conv, fftshift, filter, filtfilt
   - Communications tasks (modulation, demodulation, noise) → use Communications Toolbox: ammod, amdemod, fmmod, fmdemod, awgn
   - Control systems tasks (transfer functions, Bode, step response) → use Control System Toolbox: tf, bode, step, impulse, rlocus
   - Basic math tasks → use built-in MATLAB functions only

2. CODE STRUCTURE — always organize code into these sections with comments:
   %% Parameters
   (all variables and constants defined here)

   %% Signal Generation
   (create signals, time vectors, etc.)

   %% Processing
   (filtering, FFT, modulation, convolution, etc. — skip if not needed)

   %% Plotting
   (all figures here)

3. FIGURE FORMATTING — every figure must have:
   - title()
   - xlabel()
   - ylabel()
   - grid on
   - legend() if multiple signals
   - Use subplot() if showing time and frequency domain together

4. Only return the MATLAB code, no explanation outside of comments.
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    code = response.content.strip()

    # Remove markdown fences if Gemini adds them
    if code.startswith("```matlab"):
        code = code[len("```matlab"):].strip()
    elif code.startswith("```"):
        code = code.split("\n", 1)[1]
    if code.endswith("```"):
        code = code.rsplit("```", 1)[0]

    return code.strip()