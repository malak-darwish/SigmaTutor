import PlotDisplay    from '../components/PlotDisplay'
import CodeBlock      from '../components/CodeBlock'
import DiagramDisplay from '../components/DiagramDisplay'

export default function SandboxPage() {
  return (
    <div style={s.page}>
      <div style={s.inner}>

        <header style={s.header}>
          <h1 style={s.heading}>Component Sandbox</h1>
          <p style={s.sub}>Live preview of display components with mock Signals &amp; Systems data.</p>
        </header>

        <section style={s.section}>
          <SectionLabel>Signal Plot  —  time &amp; frequency domain</SectionLabel>
          <PlotDisplay />
        </section>

        <section style={s.section}>
          <SectionLabel>Syntax-highlighted code  —  Python &amp; MATLAB</SectionLabel>
          <CodeBlock language="python" filename="fourier_demo.py" />
          <div style={{ height: 12 }} />
          <CodeBlock language="matlab" filename="fourier_demo.m" collapsible />
        </section>

        <section style={s.section}>
          <SectionLabel>Mermaid diagram  —  flowchart &amp; sequence</SectionLabel>
          <DiagramDisplay />
        </section>

      </div>
    </div>
  )
}

function SectionLabel({ children }) {
  return <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase',
    letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: 8 }}>{children}</div>
}

const s = {
  page: {
    height: '100%',
    overflowY: 'auto',
    background: 'var(--bg-base)',
  },
  inner: {
    maxWidth: 820,
    margin: '0 auto',
    padding: '32px 24px 48px',
    display: 'flex',
    flexDirection: 'column',
    gap: 0,
  },
  header: {
    marginBottom: 28,
  },
  heading: {
    fontSize: 22,
    fontWeight: 700,
    color: 'var(--text-primary)',
    margin: '0 0 6px',
  },
  sub: {
    fontSize: 13,
    color: 'var(--text-muted)',
    margin: 0,
  },
  section: {
    marginBottom: 32,
  },
}
