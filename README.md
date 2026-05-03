🚀 SigmaTutor

SigmaTutor is a domain-specific AI tutor for Signals, Systems, and Communications Engineering. It combines retrieval-augmented generation (RAG) with a tool-augmented agent architecture to provide structured explanations, signal visualization, MATLAB code generation, and interactive learning.

✨ Features
📚 Course-grounded answers using RAG (PDF upload supported)
🧠 Conversational AI tutor with reasoning agent
📊 Signal plotting & Frequency Sandbox (interactive signal construction)
💻 MATLAB code generation
🧮 Deterministic calculators + formula verification
📝 Exam question generation & concept explanations
🎨 Clean React frontend with LaTeX rendering
🏗️ Project Structure
SigmaTutor/
│── frontend/        # React + Vite frontend
│── backend/         # FastAPI backend
│── requirements.txt
│── README.md
⚙️ Installation
1. Clone the repository
git clone https://github.com/abbass-aoun/SigmaTutor.git
cd SigmaTutor
2. Install backend dependencies

pip install -r requirements.txt
▶️ Running the Application

You need two terminals:

🖥️ Terminal 1 — Run Frontend (React + Vite)
cd frontend
npm install
npm run dev

⚙️ Terminal 2 — Run Backend (FastAPI)

From the root directory:
pip install -r backend/requirements.txt
python -m backend.main


🔄 How It Works
User sends a query from the frontend
Backend (FastAPI) forwards it to the LangGraph agent
Agent decides:
Use RAG (course material)
Call a tool (calculator, MATLAB, sandbox, etc.)
Or respond directly
Results (text, plots, code) are returned and rendered in the UI
📌 Requirements
Python 3.9+
Node.js (v16+ recommended)
npm
🧪 Notes
Make sure .env is configured with API keys (Groq, etc.)

GROQ_MODEL=llama-3.1-8b-instant
GROQ_API_KEY=[INSERT API KEY]


