import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './styles/global.css'
import Sidebar from './components/Sidebar'
import ChatPage from './pages/ChatPage'
import SandboxPage from './pages/SandboxPage'
import ExamPage from './pages/ExamPage'

const MOCK_MESSAGES = [
  {
    role: 'assistant',
    content: `Welcome to **ΣTutor** — your Signals & Systems AI companion.

I can help you understand Fourier analysis, Laplace transforms, convolution, filter design, Z-transforms, and more. What would you like to explore?`,
  },
  {
    role: 'user',
    content: 'Can you explain the Fourier Transform and its key properties?',
  },
  {
    role: 'assistant',
    content: `The **Fourier Transform** decomposes a time-domain signal into its constituent frequencies, giving us the spectrum $X(f)$.

## Definition

For a continuous-time signal $x(t)$:

$$X(f) = \\mathcal{F}\\{x(t)\\} = \\int_{-\\infty}^{\\infty} x(t)\\, e^{-j2\\pi ft}\\, dt$$

The **Inverse Fourier Transform** reconstructs the original signal from its spectrum:

$$x(t) = \\int_{-\\infty}^{\\infty} X(f)\\, e^{\\,j2\\pi ft}\\, df$$

## Key Properties

| Property | Time Domain | Frequency Domain |
|---|---|---|
| Linearity | $ax(t) + by(t)$ | $aX(f) + bY(f)$ |
| Time shift | $x(t - t_0)$ | $X(f)\\,e^{-j2\\pi f t_0}$ |
| Frequency shift | $x(t)\\,e^{\\,j2\\pi f_0 t}$ | $X(f - f_0)$ |
| Convolution | $(x * h)(t)$ | $X(f) \\cdot H(f)$ |
| Differentiation | $\\frac{dx}{dt}$ | $j2\\pi f \\cdot X(f)$ |
| Parseval | $\\int_{-\\infty}^{\\infty} \\lvert x(t)\\rvert^2 dt$ | $\\int_{-\\infty}^{\\infty} \\lvert X(f)\\rvert^2 df$ |

**Parseval's theorem** guarantees that energy is conserved across both domains — the total power in $x(t)$ equals the total power in $X(f)$.`,
  },
  {
    role: 'user',
    content: 'How does the convolution theorem work in practice?',
  },
  {
    role: 'assistant',
    content: `The **Convolution Theorem** is what makes digital signal processing computationally feasible.

In the time domain, filtering a signal $x(t)$ with a system impulse response $h(t)$ requires computing the convolution integral:

$$(x * h)(t) = \\int_{-\\infty}^{\\infty} x(\\tau)\\, h(t - \\tau)\\, d\\tau$$

The theorem states that convolution in time is equivalent to multiplication in frequency:

$$\\boxed{\\mathcal{F}\\{\\,x(t) * h(t)\\,\\} = X(f) \\cdot H(f)}$$

**Why this matters:**

- Direct convolution of length-$N$ signal with length-$M$ filter: $O(NM)$ operations
- FFT-based filtering: $O\\!\\left((N+M)\\log(N+M)\\right)$ operations

For large $N$, that difference is enormous. Here's a Python implementation:

\`\`\`python
import numpy as np

def fft_filter(x: np.ndarray, h: np.ndarray) -> np.ndarray:
    """Filter signal x with impulse response h via FFT convolution."""
    n = len(x) + len(h) - 1          # linear convolution length
    X = np.fft.rfft(x, n=n)
    H = np.fft.rfft(h, n=n)
    return np.fft.irfft(X * H, n=n)  # multiply spectra, invert

# Example: low-pass FIR filter
t  = np.linspace(0, 1, 1000, endpoint=False)
x  = np.sin(2 * np.pi * 10 * t) + np.sin(2 * np.pi * 300 * t)  # 10 Hz + 300 Hz
h  = np.sinc(2 * 50 * (t - 0.5)) * np.blackman(len(t))          # 50 Hz LPF
y  = fft_filter(x, h)               # 300 Hz component removed
\`\`\`

The dual of the convolution theorem is equally useful: **multiplication in time** (e.g. windowing a signal) corresponds to **convolution in frequency**, which is why rectangular windowing causes spectral leakage.`,
  },
]

export default function App() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [activeSession, setActiveSession] = useState(1)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

async function handleSend(text) {
    setMessages(prev => [...prev, { role: 'user', content: text }])
    setLoading(true)
    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      })
      const data = await response.json()
      let content = data.response
      // Remove raw tool call tags from response
      content = content.replace(/<[^>]+>\{[^}]+\}<\/[^>]+>/g, '').trim()
      content = content.replace(/<function=[^>]+>.*?<\/function>/gs, '').trim()

      // Extract mermaid diagram if present in mixed response
      const mermaidFenced = content.match(/```mermaid\n([\s\S]*?)```/)
      const mermaidRaw = content.match(/(graph LR[\s\S]*?)(?:\n\n|$)/)
      
      if (mermaidFenced) {
        content = mermaidFenced[1].trim()
      } else if (mermaidRaw) {
        content = mermaidRaw[1].trim()
      }

      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: content }
      ])
    } catch (error) {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: "Error connecting to backend. Make sure the server is running!" }
      ])
    } finally {
      setLoading(false)
    }
  }

  function handleNewChat() {
    setMessages([])
    setActiveSession(null)
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
