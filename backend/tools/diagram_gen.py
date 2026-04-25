import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    api_key=os.environ.get("GOOGLE_API_KEY"),
    temperature=0.0
)

def _clean_mermaid(diagram: str) -> str:
    """Remove special characters from arrow labels that break Mermaid"""
    def clean_label(match):
        label = match.group(1)
        label = label.replace("(", "").replace(")", "")
        label = label.replace("+/-", "pm")
        label = label.replace("/", "-")
        label = label.replace(" ", "_")
        return f"|{label}|"

    diagram = re.sub(r'\|([^|]+)\|', clean_label, diagram)
    return diagram


def generate_diagram(system_description: str) -> str:
    """
    Generates a Mermaid.js block diagram for a signals and systems or communications system.
    Supports simplified and detailed versions with transfer function labels on arrows.
    Args:
        system_description (str): Natural language description of the system to diagram,
                                  e.g. 'draw a detailed superheterodyne receiver',
                                  'draw a simple AM modulator'
    Returns:
        str: A Mermaid.js diagram string that the frontend will render
    """
    desc_lower = system_description.lower()
    if "simple" in desc_lower or "simplified" in desc_lower or "basic" in desc_lower:
        detail_instruction = """
Draw a SIMPLIFIED version — only the essential blocks, no labels on arrows.
Keep it minimal and easy to understand for a beginner.
"""
    else:
        detail_instruction = """
Draw a DETAILED version — include signal labels on arrows (e.g. -->|x_t| or -->|X_f|),
label every block clearly with its name and transfer function if applicable.
"""

    prompt = f"""
You are an expert in signals, systems, and communications engineering.
Generate a Mermaid.js block diagram for this system:
"{system_description}"

{detail_instruction}

Rules:
- Always start your response with "graph LR" on the first line
- Use left-to-right flow
- Only return the raw Mermaid code, no explanation, no markdown fences, no backticks
- Use (( )) for summing or mixing junctions, e.g. SUM((+))
- Use [ ] for system blocks, e.g. H["H(s) LPF"]
- Use --> for signal flow arrows
- Use -->|label| to label signals on arrows, keep labels short
- NEVER use parentheses, slashes, or special characters inside arrow labels
- Use underscores instead of spaces in arrow labels

Examples:

Simple LTI system:
graph LR
    X["Input x(t)"] --> H["H(s)"]
    H --> Y["Output y(t)"]

Detailed LTI system:
graph LR
    X["Input X(s)"] -->|X_s| H["H(s) System"]
    H -->|Y_s| Y["Output Y(s)"]

Simple AM modulator:
graph LR
    MSG["Message m(t)"] --> SUM((+))
    DC["DC Bias"] --> SUM
    SUM --> MUL{{x}}
    CAR["Carrier Ac_cos_2pi_fc_t"] --> MUL{{x}}
    MUL{{x}} --> OUT["AM Signal s(t)"]

Detailed AM modulator:
graph LR
    MSG["Message m(t)"] -->|m_t| SUM((+))
    DC["DC Bias A"] -->|A| SUM
    SUM -->|A_plus_m_t| MUL{{x}}
    CAR["Carrier Ac cos 2pi fc t"] -->|carrier| MUL{{x}}
    MUL{{x}} -->|s_t| OUT["AM Signal s(t)"]

Simple superheterodyne receiver:
graph LR
    ANT[Antenna] --> RFA[RF Amplifier]
    RFA --> MIX[Mixer]
    LO[Local Oscillator] --> MIX
    MIX --> IFF[IF Filter]
    IFF --> IFA[IF Amplifier]
    IFA --> DEM[Demodulator]
    DEM --> OUT[Output]

Detailed superheterodyne receiver:
graph LR
    ANT["Antenna"] -->|RF_signal| RFA["RF Amplifier"]
    RFA -->|amplified_RF| MIX["Mixer"]
    LO["Local Oscillator fLO"] -->|LO_signal| MIX
    MIX -->|IF_signal| IFF["IF Filter"]
    IFF -->|filtered_IF| IFA["IF Amplifier"]
    IFA -->|amplified_IF| DEM["Demodulator"]
    DEM -->|baseband| OUT["Output"]

Simple FM modulator:
graph LR
    MSG["Message m(t)"] --> INT["Integrator"]
    INT --> VCO["VCO Voltage Controlled Oscillator"]
    VCO --> OUT["FM Signal s(t)"]

Detailed sampling system:
graph LR
    X["Continuous x(t)"] -->|x_t| SAM["Sampler fs"]
    SAM -->|x_nTs| ADC["ADC"]
    ADC -->|digital| PROC["Processor"]
    PROC -->|digital| DAC["DAC"]
    DAC -->|x_nTs| REC["Reconstruction Filter"]
    REC -->|x_reconstructed| OUT["Output"]

Common systems to handle: LTI systems, AM modulator, FM modulator,
superheterodyne receiver, sampling and reconstruction, DSB, SSB,
filter structures, communication chain, PLL, multiplexer
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    diagram = response.content.strip()

    if diagram.startswith("```mermaid"):
        diagram = diagram[len("```mermaid"):].strip()
    elif diagram.startswith("```"):
        diagram = diagram[len("```"):].strip()

    if diagram.endswith("```"):
        diagram = diagram[:-3].strip()

    diagram = _clean_mermaid(diagram)
    return diagram.strip()