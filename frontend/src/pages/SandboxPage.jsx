import { useState, useRef } from 'react'
import PlotDisplay from '../components/PlotDisplay'
import DiagramDisplay from '../components/DiagramDisplay'
import { Send, RotateCcw } from 'lucide-react'

const SUGGESTIONS = [
  'Plot a 10Hz sine wave',
  'Create a square wave and add noise',
  'AM modulate a 5Hz sine with 100Hz carrier',
  'Plot a sine and cosine at 5Hz together',
  'Convolve a rect pulse with an impulse',
  'Apply a lowpass filter at 30Hz',
  'Show me the MATLAB code for this',
  'Get Python code for current signal',
]

export default function SandboxPage() {
  const [input, setInput]       = useState('')
  const [history, setHistory]   = useState([])
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')
  const bottomRef               = useRef(null)


  async function handleSend() {
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    setLoading(true)
    setError('')

    setHistory(prev => [...prev, { role: 'user', content: text }])

    try {
      const res = await fetch('http://localhost:8000/sandbox', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      })
      const data = await res.json()
      if (data.success) {
        setHistory(prev => [...prev, {
          role: 'assistant',
          content: data.response,
          isPlot: isBase64(data.response)
        }])
      } else {
        setError(data.response || 'Error from backend')
      }
    } catch (e) {
      setError('Cannot connect to backend!')
    } finally {
      setLoading(false)
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), 100)
    }
  }

  function isBase64(str) {
    return str && str.length > 500 && /^[A-Za-z0-9+/=]+$/.test(str.trim())
  }

  async function handleReset() {
    setHistory([])
    setError('')
    setInput('')
    
    // ← Add this: reset backend state too
    try {
        await fetch('http://localhost:8000/sandbox', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: 'reset' })
        })
    } catch (e) {
        console.log('Could not reset sandbox state')
    }
}



  return (
    <div style={s.page}>
      <div style={s.inner}>

        {/* Header */}
        <header style={s.header}>
          <div style={s.headerLeft}>
            <h1 style={s.heading}>🌊 Frequency Sandbox</h1>
            <p style={s.sub}>
              Build and modify signals interactively. Describe what you want in plain English.
            </p>
          </div>
          <button style={s.resetBtn} onClick={handleReset} title="Reset sandbox">
            <RotateCcw size={14} />
            Reset
          </button>
        </header>

        {/* Suggestions */}
        <div style={s.chips}>
          {SUGGESTIONS.map(s => (
            <button
              key={s}
              style={style.chip}
              onClick={() => setInput(s)}
            >
              {s}
            </button>
          ))}
        </div>

        {/* History */}
        <div style={s.history}>
          {history.length === 0 && (
            <div style={s.empty}>
              <span style={{ fontSize: 40 }}>🌊</span>
              <p style={{ color: 'var(--text-muted)', fontSize: 13, margin: 0 }}>
                Describe a signal to get started. Try "Plot a 10Hz sine wave"
              </p>
            </div>
          )}

          {history.map((msg, i) => (
            <div key={i} style={msg.role === 'user' ? s.userMsg : s.assistantMsg}>
              {msg.role === 'user' ? (
                <div style={s.userBubble}>{msg.content}</div>
              ) : msg.isPlot ? (
                <PlotDisplay imageBase64={msg.content} title="Signal Plot" />
              ) : (
                <div style={s.assistantBubble}>
                  <pre style={s.code}>{msg.content}</pre>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div style={s.assistantMsg}>
              <div style={s.assistantBubble}>
                <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>
                  Processing signal...
                </span>
              </div>
            </div>
          )}

          {error && (
            <div style={s.errorBox}>{error}</div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div style={s.inputWrap}>
          <div style={s.inputBox}>
            <input
              style={s.input}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
              placeholder="Describe a signal operation... e.g. 'add a 20Hz cosine'"
              disabled={loading}
            />
            <button
              style={{
                ...s.sendBtn,
                opacity: !input.trim() || loading ? 0.5 : 1
              }}
              onClick={handleSend}
              disabled={!input.trim() || loading}
            >
              <Send size={15} color="#fff" />
            </button>
          </div>
          <p style={s.hint}>Press Enter to send · Build signals step by step</p>
        </div>

      </div>
    </div>
  )
}

const style = {
  chip: {
    padding: '5px 12px',
    borderRadius: 20,
    border: '1px solid var(--border)',
    background: 'var(--bg-panel)',
    color: 'var(--text-secondary)',
    fontSize: 12,
    cursor: 'pointer',
    transition: 'all 0.15s',
    whiteSpace: 'nowrap',
  }
}

const s = {
  page: {
    height: '100%',
    overflowY: 'auto',
    background: 'var(--bg-base)',
    display: 'flex',
    flexDirection: 'column',
  },
  inner: {
    maxWidth: 820,
    margin: '0 auto',
    padding: '24px 24px 16px',
    display: 'flex',
    flexDirection: 'column',
    gap: 16,
    flex: 1,
    width: '100%',
    boxSizing: 'border-box',
  },
  header: {
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: 12,
  },
  headerLeft: {
    display: 'flex',
    flexDirection: 'column',
    gap: 4,
  },
  heading: {
    fontSize: 20,
    fontWeight: 700,
    color: 'var(--text-primary)',
    margin: 0,
  },
  sub: {
    fontSize: 13,
    color: 'var(--text-muted)',
    margin: 0,
  },
  resetBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '6px 14px',
    borderRadius: 8,
    border: '1px solid var(--border)',
    background: 'var(--bg-panel)',
    color: 'var(--text-secondary)',
    fontSize: 12,
    fontWeight: 600,
    cursor: 'pointer',
    flexShrink: 0,
  },
  chips: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 6,
  },
  history: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: 16,
    minHeight: 200,
  },
  empty: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
    padding: '48px 0',
    textAlign: 'center',
  },
  userMsg: {
    display: 'flex',
    justifyContent: 'flex-end',
  },
  userBubble: {
    maxWidth: '70%',
    padding: '9px 14px',
    borderRadius: 14,
    borderBottomRightRadius: 3,
    background: 'var(--accent-blue)',
    color: '#fff',
    fontSize: 13,
    lineHeight: 1.5,
  },
  assistantMsg: {
    display: 'flex',
    justifyContent: 'flex-start',
  },
  assistantBubble: {
    maxWidth: '100%',
    width: '100%',
    padding: '12px 14px',
    borderRadius: 14,
    borderBottomLeftRadius: 3,
    background: 'var(--bg-panel)',
    border: '1px solid var(--border)',
  },
  code: {
    margin: 0,
    fontSize: 12,
    fontFamily: 'var(--font-mono)',
    color: 'var(--text-secondary)',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
  },
  errorBox: {
    padding: '10px 14px',
    borderRadius: 8,
    background: 'rgba(239,68,68,0.1)',
    border: '1px solid rgba(239,68,68,0.3)',
    color: '#ef4444',
    fontSize: 13,
  },
  inputWrap: {
    display: 'flex',
    flexDirection: 'column',
    gap: 6,
    paddingTop: 8,
    borderTop: '1px solid var(--border)',
  },
  inputBox: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    background: 'var(--bg-panel)',
    border: '1px solid var(--border)',
    borderRadius: 12,
    padding: '6px 8px 6px 14px',
  },
  input: {
    flex: 1,
    background: 'transparent',
    border: 'none',
    outline: 'none',
    fontSize: 13,
    color: 'var(--text-primary)',
    fontFamily: 'var(--font-ui)',
  },
  sendBtn: {
    width: 32,
    height: 32,
    borderRadius: 8,
    background: 'var(--accent-blue)',
    border: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    flexShrink: 0,
    transition: 'opacity 0.15s',
  },
  hint: {
    fontSize: 11,
    color: 'var(--text-muted)',
    margin: 0,
    textAlign: 'center',
  },
}