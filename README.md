# 🚀 SigmaTutor

SigmaTutor is a domain-specific AI tutor specialized in Signals, Systems, and Communications Engineering. It combines Retrieval-Augmented Generation (RAG) with a tool-augmented reasoning agent to provide interactive explanations, signal visualization, MATLAB code generation, and course-grounded learning support.

---

## ✨ Features

* 📚 Course-grounded answers using RAG
* 📄 PDF upload support for custom course material
* 🧠 Conversational AI tutor with reasoning agents
* 📊 Interactive signal plotting & Frequency Sandbox
* 💻 MATLAB code generation
* 🧮 Deterministic calculators & formula verification
* 📝 Exam question generation and concept explanations
* 🎨 Clean React frontend with LaTeX rendering

---

## 🏗️ Project Structure

```bash id="a2j8lx"
SigmaTutor/
│── frontend/          # React + Vite frontend
│── backend/           # FastAPI backend
│── requirements.txt
│── README.md
```

---

## ⚙️ Installation

Clone the repository:

```bash id="2t9l1w"
git clone https://github.com/abbass-aoun/SigmaTutor.git
```

Navigate into the project folder:

```bash id="w9g2ms"
cd SigmaTutor
```

Install backend dependencies:

```bash id="7c5lpk"
pip install -r requirements.txt
```

---

## ▶️ Running the Application

You will need two terminals.

### 🖥️ Terminal 1 — Run Frontend

```bash id="m6z8rt"
cd frontend
npm install
npm run dev
```

### ⚙️ Terminal 2 — Run Backend

From the root directory:

```bash id="u5c4dp"
pip install -r backend/requirements.txt
python -m backend.main
```

---

## 🔄 How It Works

1. The user sends a query from the frontend.
2. The FastAPI backend forwards the request to the LangGraph agent.
3. The agent decides whether to:

   * Use RAG from course material
   * Call a tool (calculator, MATLAB generation, sandbox, etc.)
   * Respond directly
4. Results such as explanations, plots, and generated code are returned and rendered in the UI.

---

## 📌 Requirements

* Python 3.9+
* Node.js (v16+ recommended)
* npm

---

## 🧪 Environment Variables

Create a `.env` file and configure your API keys:

```env id="r1x5qm"
GROQ_MODEL=llama-3.1-8b-instant
GROQ_API_KEY=YOUR_API_KEY
```

---
