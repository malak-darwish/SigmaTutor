import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import { Eye, EyeOff, BookOpen, Send } from 'lucide-react'
import 'katex/dist/katex.min.css'

const MD_REMARK = [remarkMath]
const MD_REHYPE = [rehypeKatex]

function Md({ children }) {
  return (
    <div className="ep-md">
      <ReactMarkdown remarkPlugins={MD_REMARK} rehypePlugins={MD_REHYPE}>
        {children}
      </ReactMarkdown>
    </div>
  )
}

const TOPIC_SUGGESTIONS = [
  'Fourier Transform',
  'Sampling & Aliasing',
  'LTI Systems & Convolution',
  'Laplace Transform',
  'AM & FM Modulation',
  'Shannon Capacity & SNR',
  'Z-Transform',
  'Filter Design',
]

const DIFFICULTIES = ['easy', 'medium', 'hard']

export default function ExamPanel() {
  const [topic, setTopic]           = useState('')
  const [difficulty, setDifficulty] = useState('medium')
  const [numQuestions, setNum]      = useState(5)
  const [response, setResponse]     = useState('')
  const [loading, setLoading]       = useState(false)
  const [error, setError]           = useState('')
  const [showSolution, setShow]     = useState(false)
  const [generated, setGenerated]   = useState(false)

  async function handleGenerate() {
    const t = topic.trim()
    if (!t) return
    setLoading(true)
    setError('')
    setResponse('')
    setShow(false)
    setGenerated(false)

    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: `Generate ${numQuestions} ${difficulty} exam questions about ${t} for Signals & Systems. Include step-by-step solutions.`
        })
      })
      const data = await res.json()
      if (data.success) {
        setResponse(data.response)
        setGenerated(true)
      } else {
        setError(data.response || 'Failed to generate exam.')
      }
    } catch (e) {
      setError('Cannot connect to backend. Make sure the server is running!')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={s.page}>
      <div style={s.card}>

        {/* ── Header ── */}
        <div style={s.topBar}>
          <div style={s.topLeft}>
            <BookOpen size={15} color="var(--accent-blue)" />
            <span style={s.topTitle}>Exam Generator</span>
          </div>
          <span style={s.badge}>AI-Powered</span>
        </div>

        {/* ── Controls ── */}
        <div style={s.controls}>

          {/* Topic input */}
          <div style={s.field}>
            <label style={s.label}>Topic</label>
            <input
              style={s.input}
              value={topic}
              onChange={e => setTopic(e.target.value)}
              placeholder="e.g. Fourier Transform, AM Modulation..."
              onKeyDown={e => e.key === 'Enter' && handleGenerate()}
            />
          </div>

          {/* Topic suggestions */}
          <div style={s.chips}>
            {TOPIC_SUGGESTIONS.map(t => (
              <button
                key={t}
                style={{
                  ...s.chip,
                  ...(topic === t ? s.chipActive : {})
                }}
                onClick={() => setTopic(t)}
              >
                {t}
              </button>
            ))}
          </div>

          {/* Difficulty + Num Questions */}
          <div style={s.row}>
            <div style={s.field}>
              <label style={s.label}>Difficulty</label>
              <div style={s.diffRow}>
                {DIFFICULTIES.map(d => (
                  <button
                    key={d}
                    style={{
                      ...s.diffBtn,
                      ...(difficulty === d ? s.diffBtnActive(d) : {})
                    }}
                    onClick={() => setDifficulty(d)}
                  >
                    {d.charAt(0).toUpperCase() + d.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            <div style={s.field}>
              <label style={s.label}>Questions: <strong style={{ color: 'var(--text-primary)' }}>{numQuestions}</strong></label>
              <input
                type="range"
                min={1}
                max={10}
                value={numQuestions}
                onChange={e => setNum(Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--accent-blue)' }}
              />
            </div>
          </div>

          {/* Generate button */}
          <button
            style={{
              ...s.generateBtn,
              opacity: loading || !topic.trim() ? 0.6 : 1
            }}
            onClick={handleGenerate}
            disabled={loading || !topic.trim()}
          >
            <Send size={14} />
            {loading ? 'Generating...' : 'Generate Exam'}
          </button>
        </div>

        {/* ── Error ── */}
        {error && (
          <div style={s.error}>{error}</div>
        )}

        {/* ── Loading ── */}
        {loading && (
          <div style={s.loadingBox}>
            <div style={s.dots}>
              <span className="dot" style={{ '--i': 0 }} />
              <span className="dot" style={{ '--i': 1 }} />
              <span className="dot" style={{ '--i': 2 }} />
            </div>
            <span style={s.loadingText}>Generating your exam...</span>
          </div>
        )}

        {/* ── Result ── */}
        {generated && response && (
          <div style={s.result}>

            <div style={s.resultHeader}>
              <span style={s.resultTitle}>
                📝 {numQuestions} {difficulty} questions on "{topic}"
              </span>
              <button
                style={{
                  ...s.solutionBtn,
                  ...(showSolution ? s.solutionBtnActive : {})
                }}
                onClick={() => setShow(v => !v)}
              >
                {showSolution
                  ? <><EyeOff size={13} /><span>Hide Solutions</span></>
                  : <><Eye size={13} /><span>Show Solutions</span></>
                }
              </button>
            </div>

            <div style={s.examContent}>
              <Md>{response}</Md>
            </div>

          </div>
        )}

      </div>

      <style>{INJECTED_CSS}</style>
    </div>
  )
}

const DIFF_COLORS = {
  easy:   { color: '#10b981', bg: 'rgba(16,185,129,.15)', border: 'rgba(16,185,129,.3)'  },
  medium: { color: '#f59e0b', bg: 'rgba(245,158,11,.15)', border: 'rgba(245,158,11,.3)'  },
  hard:   { color: '#ef4444', bg: 'rgba(239,68,68,.15)',  border: 'rgba(239,68,68,.3)'   },
}

const INJECTED_CSS = `
  .ep-md { font-size: 14px; line-height: 1.8; color: var(--text-primary); }
  .ep-md > *:first-child { margin-top: 0 !important; }
  .ep-md > *:last-child  { margin-bottom: 0 !important; }
  .ep-md p  { margin: 0 0 10px; }
  .ep-md h1 { font-size: 18px; font-weight: 700; margin: 18px 0 8px; }
  .ep-md h2 { font-size: 15px; font-weight: 700; margin: 16px 0 6px; }
  .ep-md h3 { font-size: 14px; font-weight: 600; margin: 12px 0 4px; }
  .ep-md ul, .ep-md ol { margin: 6px 0 10px 20px; }
  .ep-md li { margin: 3px 0; }
  .ep-md strong { font-weight: 700; color: var(--text-primary); }
  .ep-md table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 13px; }
  .ep-md th { background: var(--bg-surface); color: var(--text-primary); font-weight: 600; padding: 7px 12px; text-align: left; border: 1px solid var(--border); }
  .ep-md td { padding: 6px 12px; border: 1px solid var(--border); color: var(--text-secondary); }
  .ep-md tr:nth-child(even) td { background: rgba(255,255,255,.02); }
  .ep-md code { font-family: var(--font-mono); font-size: 12.5px; background: var(--bg-surface); border: 1px solid var(--border); padding: 1px 5px; border-radius: 4px; color: var(--accent-green); }
  .ep-md hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }
  .ep-md .katex-display { margin: 16px 0; overflow-x: auto; }

  @keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); opacity: .4; }
    40%           { transform: translateY(-5px); opacity: 1; }
  }
  .dot {
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--text-muted);
    animation: bounce 1.2s ease-in-out infinite;
    animation-delay: calc(var(--i) * 0.2s);
  }
`

const s = {
  page: {
    height: '100%',
    overflowY: 'auto',
    background: 'var(--bg-base)',
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'center',
    padding: '32px 16px 48px',
  },
  card: {
    width: '100%',
    maxWidth: 740,
    background: 'var(--bg-panel)',
    border: '1px solid var(--border)',
    borderRadius: 14,
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
  },
  topBar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '12px 20px',
    borderBottom: '1px solid var(--border)',
    background: 'var(--bg-surface)',
  },
  topLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: 7,
  },
  topTitle: {
    fontSize: 13,
    fontWeight: 700,
    color: 'var(--text-primary)',
  },
  badge: {
    fontSize: 10,
    fontWeight: 700,
    color: 'var(--accent-blue)',
    background: 'rgba(59,130,246,0.1)',
    border: '1px solid rgba(59,130,246,0.25)',
    padding: '2px 8px',
    borderRadius: 20,
    letterSpacing: '0.05em',
  },
  controls: {
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: 14,
    borderBottom: '1px solid var(--border)',
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: 6,
    flex: 1,
  },
  label: {
    fontSize: 12,
    fontWeight: 600,
    color: 'var(--text-secondary)',
  },
  input: {
    padding: '8px 12px',
    borderRadius: 8,
    border: '1px solid var(--border)',
    background: 'var(--bg-base)',
    color: 'var(--text-primary)',
    fontSize: 13,
    outline: 'none',
    width: '100%',
    boxSizing: 'border-box',
  },
  chips: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 6,
  },
  chip: {
    padding: '4px 12px',
    borderRadius: 20,
    border: '1px solid var(--border)',
    background: 'var(--bg-base)',
    color: 'var(--text-secondary)',
    fontSize: 12,
    cursor: 'pointer',
    transition: 'all 0.15s',
  },
  chipActive: {
    background: 'rgba(59,130,246,0.15)',
    color: 'var(--accent-blue)',
    borderColor: 'rgba(59,130,246,0.4)',
  },
  row: {
    display: 'flex',
    gap: 16,
    flexWrap: 'wrap',
  },
  diffRow: {
    display: 'flex',
    gap: 6,
  },
  diffBtn: {
    padding: '5px 14px',
    borderRadius: 8,
    border: '1px solid var(--border)',
    background: 'var(--bg-base)',
    color: 'var(--text-secondary)',
    fontSize: 12,
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'all 0.15s',
  },
  diffBtnActive: (d) => ({
    background: DIFF_COLORS[d].bg,
    color: DIFF_COLORS[d].color,
    borderColor: DIFF_COLORS[d].border,
  }),
  generateBtn: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    padding: '10px 20px',
    borderRadius: 9,
    border: 'none',
    background: 'var(--accent-blue)',
    color: '#fff',
    fontSize: 14,
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'opacity 0.15s',
  },
  error: {
    margin: '16px 20px',
    padding: '10px 14px',
    borderRadius: 8,
    background: 'rgba(239,68,68,0.1)',
    border: '1px solid rgba(239,68,68,0.3)',
    color: '#ef4444',
    fontSize: 13,
  },
  loadingBox: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    padding: '24px 20px',
  },
  dots: {
    display: 'flex',
    gap: 5,
  },
  loadingText: {
    fontSize: 13,
    color: 'var(--text-muted)',
  },
  result: {
    display: 'flex',
    flexDirection: 'column',
  },
  resultHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '14px 20px',
    borderTop: '1px solid var(--border)',
    background: 'var(--bg-surface)',
    flexWrap: 'wrap',
    gap: 8,
  },
  resultTitle: {
    fontSize: 13,
    fontWeight: 600,
    color: 'var(--text-primary)',
  },
  solutionBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '6px 14px',
    borderRadius: 7,
    border: '1px solid var(--border)',
    background: 'var(--bg-base)',
    color: 'var(--text-secondary)',
    fontSize: 12,
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'all 0.15s',
  },
  solutionBtnActive: {
    background: 'rgba(16,185,129,0.1)',
    color: 'var(--accent-green)',
    borderColor: 'rgba(16,185,129,0.3)',
  },
  examContent: {
    padding: '20px',
  },
}