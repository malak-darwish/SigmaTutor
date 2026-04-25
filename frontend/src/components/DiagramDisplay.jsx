import { useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'
import { Download, RefreshCw, AlertTriangle } from 'lucide-react'

// ─── Mermaid initialisation (once) ───────────────────────────────────────────

mermaid.initialize({
  startOnLoad: false,
  theme: 'base',
  darkMode: true,
  themeVariables: {
    background:       '#0f1117',
    primaryColor:     '#1a1b2e',
    primaryTextColor: '#e2e8f0',
    primaryBorderColor: '#3b82f6',
    lineColor:        '#64748b',
    secondaryColor:   '#242640',
    tertiaryColor:    '#0d0f1a',
    edgeLabelBackground: '#1a1b2e',
    clusterBkg:       '#1a1b2e',
    clusterBorder:    '#2d2f4a',
    titleColor:       '#e2e8f0',
    fontFamily:       'Inter, system-ui, sans-serif',
    fontSize:         '13px',
    nodeTextColor:    '#e2e8f0',
    labelTextColor:   '#e2e8f0',
  },
})

// ─── Mock diagrams ────────────────────────────────────────────────────────────

const DEMO_FLOWCHART = `flowchart LR
    A([x&#40;t&#41;\\nInput]) --> B[ADC\\nSampling @ fs]
    B --> C[Window\\nFunction]
    C --> D[FFT\\nN-point]
    D --> E[X&#40;f&#41;\\nSpectrum]
    E --> F{Filter\\nH&#40;f&#41;}
    F -->|Pass| G[Y&#40;f&#41;\\nFiltered]
    F -->|Reject| H([Discarded])
    G --> I[IFFT]
    I --> J([y&#40;t&#41;\\nOutput])

    style A fill:#1e2a4a,stroke:#3b82f6,color:#93c5fd
    style J fill:#1e3a2e,stroke:#10b981,color:#6ee7b7
    style H fill:#2a1e2e,stroke:#8b5cf6,color:#c4b5fd
    style F fill:#242640,stroke:#f59e0b,color:#fcd34d
`

const DEMO_SEQUENCE = `sequenceDiagram
    participant S as Student
    participant T as ΣTutor
    participant B as Backend
    participant V as Vector DB

    S->>T: "Explain Nyquist theorem"
    T->>B: POST /chat {query}
    B->>V: Semantic search
    V-->>B: Relevant context chunks
    B->>B: Augment prompt (RAG)
    B-->>T: Stream response tokens
    T-->>S: Rendered markdown + LaTeX
`

const DEMO_DIAGRAMS = {
  flowchart: { label: 'DSP Pipeline',       code: DEMO_FLOWCHART },
  sequence:  { label: 'RAG Chat Sequence',  code: DEMO_SEQUENCE  },
}

// ─── Component ────────────────────────────────────────────────────────────────

let _idCounter = 0

export default function DiagramDisplay({ diagram, title }) {
  const idRef     = useRef(`mermaid-${++_idCounter}`)
  const [activeKey, setActiveKey] = useState('flowchart')

  const resolvedCode  = diagram ?? DEMO_DIAGRAMS[activeKey].code
  const resolvedTitle = title   ?? DEMO_DIAGRAMS[activeKey].label

  const [svg,     setSvg]     = useState('')
  const [status,  setStatus]  = useState('idle') // idle | loading | error
  const [errMsg,  setErrMsg]  = useState('')

  useEffect(() => {
    let cancelled = false
    setStatus('loading')
    setSvg('')
    setErrMsg('')

    // mermaid.render needs a fresh unique id each call
    const renderId = `${idRef.current}-${Date.now()}`

    mermaid.render(renderId, resolvedCode)
      .then(({ svg: rendered }) => {
        if (!cancelled) {
          setSvg(rendered)
          setStatus('idle')
        }
      })
      .catch(err => {
        if (!cancelled) {
          setErrMsg(err.message ?? 'Diagram render failed')
          setStatus('error')
        }
      })

    return () => { cancelled = true }
  }, [resolvedCode])

  function downloadSVG() {
    if (!svg) return
    const blob = new Blob([svg], { type: 'image/svg+xml' })
    const url  = URL.createObjectURL(blob)
    const a    = Object.assign(document.createElement('a'), {
      href: url, download: `${resolvedTitle.replace(/\s+/g, '_')}.svg`,
    })
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div style={s.root}>

      {/* ── Header ── */}
      <div style={s.header}>
        <div style={s.headerLeft}>
          <span style={s.badge}>Mermaid</span>
          <span style={s.title}>{resolvedTitle}</span>
        </div>
        <div style={s.headerRight}>
          {/* Only show tab switcher when using built-in demos */}
          {!diagram && Object.entries(DEMO_DIAGRAMS).map(([key, d]) => (
            <button
              key={key}
              style={{ ...s.tab, ...(activeKey === key ? s.tabActive : {}) }}
              onClick={() => setActiveKey(key)}
            >
              {d.label}
            </button>
          ))}
          <button style={s.iconBtn} onClick={downloadSVG} title="Download SVG" disabled={!svg}>
            <Download size={13} />
          </button>
        </div>
      </div>

      {/* ── Body ── */}
      <div style={s.body}>
        {status === 'loading' && (
          <div style={s.state}>
            <RefreshCw size={18} color="var(--text-muted)"
              style={{ animation: 'spin 1s linear infinite' }} />
            <span style={s.stateText}>Rendering diagram…</span>
          </div>
        )}

        {status === 'error' && (
          <div style={s.state}>
            <AlertTriangle size={18} color="var(--accent-purple)" />
            <div>
              <div style={{ ...s.stateText, color: 'var(--accent-purple)' }}>
                Diagram syntax error
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4, fontFamily: 'var(--font-mono)' }}>
                {errMsg}
              </div>
            </div>
          </div>
        )}

        {status === 'idle' && svg && (
          <div
            style={s.svgWrap}
            dangerouslySetInnerHTML={{ __html: svg }}
          />
        )}
      </div>

      {/* ── Source toggle ── */}
      <SourcePanel code={resolvedCode} />

      <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
    </div>
  )
}

// ─── Source panel (collapsible code view) ────────────────────────────────────

function SourcePanel({ code }) {
  const [open, setOpen] = useState(false)
  return (
    <div style={s.sourceRoot}>
      <button style={s.sourceToggle} onClick={() => setOpen(v => !v)}>
        <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)' }}>
          {open ? '▾ Hide source' : '▸ Show source'}
        </span>
      </button>
      {open && (
        <pre style={s.source}>{code.trim()}</pre>
      )}
    </div>
  )
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const s = {
  root: {
    background: 'var(--bg-panel)',
    border: '1px solid var(--border)',
    borderRadius: 10,
    overflow: 'hidden',
    width: '100%',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '8px 12px',
    borderBottom: '1px solid var(--border)',
    gap: 10,
    flexWrap: 'wrap',
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  },
  badge: {
    fontSize: 10,
    fontWeight: 700,
    color: 'var(--accent-green)',
    background: 'rgba(16,185,129,0.1)',
    border: '1px solid rgba(16,185,129,0.25)',
    padding: '2px 7px',
    borderRadius: 4,
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
    fontFamily: 'var(--font-mono)',
  },
  title: {
    fontSize: 13,
    fontWeight: 600,
    color: 'var(--text-primary)',
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: 4,
  },
  tab: {
    padding: '3px 10px',
    borderRadius: 5,
    border: '1px solid var(--border)',
    background: 'none',
    color: 'var(--text-muted)',
    fontSize: 11,
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'background 0.12s, color 0.12s',
  },
  tabActive: {
    background: 'var(--bg-surface)',
    color: 'var(--text-primary)',
    borderColor: 'var(--accent-blue)',
  },
  iconBtn: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: 26,
    height: 26,
    borderRadius: 5,
    border: 'none',
    background: 'none',
    color: 'var(--text-muted)',
    cursor: 'pointer',
    transition: 'background 0.12s, color 0.12s',
  },

  body: {
    minHeight: 140,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#0b0d18',
    padding: '16px',
  },
  svgWrap: {
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
    // Mermaid SVG inherits dark variables
  },

  state: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    color: 'var(--text-muted)',
  },
  stateText: {
    fontSize: 13,
    color: 'var(--text-secondary)',
  },

  sourceRoot: {
    borderTop: '1px solid var(--border)',
  },
  sourceToggle: {
    width: '100%',
    padding: '6px 14px',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    textAlign: 'left',
    display: 'flex',
    alignItems: 'center',
  },
  source: {
    margin: 0,
    padding: '10px 16px 12px',
    fontSize: 11.5,
    fontFamily: 'var(--font-mono)',
    color: 'var(--text-muted)',
    background: '#09090f',
    borderTop: '1px solid var(--border)',
    overflowX: 'auto',
    lineHeight: 1.7,
    whiteSpace: 'pre',
  },
}
