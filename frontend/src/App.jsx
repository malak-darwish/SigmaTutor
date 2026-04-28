import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './styles/global.css'
import Sidebar from './components/Sidebar'
import ChatPage from './pages/ChatPage'
import SandboxPage from './pages/SandboxPage'
import ExamPage from './pages/ExamPage'

const TOPICS = [
  'Fourier Transform', 'Laplace Transform', 'Z-Transform',
  'Convolution', 'Sampling', 'Aliasing', 'AM Modulation',
  'FM Modulation', 'Filter', 'Shannon', 'LTI', 'Bode',
  'Nyquist', 'Parseval', 'FFT', 'DFT', 'DSP', 'Signal',
]

export default function App() {
  const [messages, setMessages]           = useState([])
  const [loading, setLoading]             = useState(false)
  const [activeSession, setActiveSession] = useState(1)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [todayQuestions, setTodayQuestions]     = useState([])
  const [toolsUsed, setToolsUsed]               = useState(new Set())
  const [coveredTopics, setCoveredTopics]       = useState(new Set())
  const [sessionStart]                          = useState(Date.now())
  const [sessionSeconds, setSessionSeconds]     = useState(0)

  // Session timer
  useEffect(() => {
    const interval = setInterval(() => {
      setSessionSeconds(Math.floor((Date.now() - sessionStart) / 1000))
    }, 1000)
    return () => clearInterval(interval)
  }, [sessionStart])

  function detectTool(text) {
    const t = text.toLowerCase()
    if (t.includes('plot') || t.includes('signal')) return 'Signal Plotter'
    if (t.includes('matlab')) return 'MATLAB Generator'
    if (t.includes('diagram') || t.includes('block')) return 'Diagram Generator'
    if (t.includes('exam') || t.includes('quiz')) return 'Exam Generator'
    if (t.includes('prove') || t.includes('derive')) return 'Formula Prover'
    if (t.includes('explain')) return 'Concept Explainer'
    if (t.includes('calculate') || t.includes('compute')) return 'Calculator'
    return null
  }

  function detectTopics(text) {
    const t = text.toLowerCase()
    return TOPICS.filter(topic => t.includes(topic.toLowerCase()))
  }

  async function handleSend(text) {
    setMessages(prev => [...prev, { role: 'user', content: text }])
    setLoading(true)

    setTodayQuestions(prev => {
      if (prev.includes(text)) return prev
      return [text, ...prev].slice(0, 10)
    })

    const tool = detectTool(text)
    if (tool) setToolsUsed(prev => new Set([...prev, tool]))

    const topics = detectTopics(text)
    if (topics.length > 0) {
      setCoveredTopics(prev => new Set([...prev, ...topics]))
    }

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      })
      const data = await response.json()
      let content = data.response
      content = content.replace(/<[^>]+>\{[^}]+\}<\/[^>]+>/g, '').trim()
      content = content.replace(/<function=[^>]+>.*?<\/function>/gs, '').trim()

      const mermaidFenced = content.match(/```mermaid\n([\s\S]*?)```/)
      const mermaidRaw    = content.match(/(graph LR[\s\S]*?)(?:\n\n|$)/)

      if (mermaidFenced) content = mermaidFenced[1].trim()
      else if (mermaidRaw) content = mermaidRaw[1].trim()

      setMessages(prev => [...prev, { role: 'assistant', content }])
    } catch {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: "Error connecting to backend. Make sure the server is running!" }
      ])
    } finally {
      setLoading(false)
    }
  }

  async function handleNewChat() {
    setMessages([])
    setActiveSession(null)
    try {
      await fetch('http://localhost:8000/clear-history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm: true })
      })
    } catch {
      console.log('Could not clear backend history')
    }
  }

  return (
    <BrowserRouter>
      <div className="app-shell">
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(v => !v)}
          activeSession={activeSession}
          onNewChat={handleNewChat}
          onSelectSession={setActiveSession}
          todayQuestions={todayQuestions}
          toolsUsed={toolsUsed}
          coveredTopics={coveredTopics}
          sessionSeconds={sessionSeconds}
          onSelectQuestion={handleSend}
          onSend={handleSend}
        />
        <main className="main-area">
          <Routes>
            <Route path="/" element={<ChatPage messages={messages} onSend={handleSend} loading={loading} />} />
            <Route path="/sandbox" element={<SandboxPage />} />
            <Route path="/exam" element={<ExamPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}