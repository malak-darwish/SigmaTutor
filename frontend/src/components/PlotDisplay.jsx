import { useState, useRef } from 'react'
import { ZoomIn, ZoomOut, Download, Maximize2, X } from 'lucide-react'

// ─── SVG plot generators ──────────────────────────────────────────────────────

const W = 480, H = 120, CY = H / 2, AMP = CY * 0.75

const TIME_PATH = (() => {
  const pts = Array.from({ length: 241 }, (_, i) => {
    const t = i / 240
    const y = Math.sin(2 * Math.PI * 3 * t) + 0.45 * Math.sin(2 * Math.PI * 8 * t)
    const svgY = CY - (y / 1.5) * AMP
    return `${i === 0 ? 'M' : 'L'}${(i / 240 * W).toFixed(1)},${svgY.toFixed(1)}`
  })
  return pts.join(' ')
})()

// Pre-compute freq domain: main spike at f=3, harmonic at f=8, noise floor
const FREQ_BARS = (() => {
  const fMax = 12, bars = []
  // main components
  bars.push({ f: 3,  amp: 0.90, color: '#3b82f6' })
  bars.push({ f: 8,  amp: 0.40, color: '#8b5cf6' })
  // noise floor
  for (let f = 1; f <= fMax; f++) {
    if (f === 3 || f === 8) continue
    bars.push({ f, amp: 0.03 + Math.sin(f * 17.3) * 0.02, color: '#64748b' })
  }
  return bars.map(b => ({
    ...b,
    x: (b.f / fMax) * W,
    barH: b.amp * (H - 30),
  }))
})()

// ─── SVG components ───────────────────────────────────────────────────────────

function PlotSVG({ id, children }) {
  return (
    <svg
      id={id}
      viewBox={`0 0 ${W} ${H}`}
      width="100%"
      preserveAspectRatio="xMidYMid meet"
      style={{ display: 'block', background: '#0b0d18', borderRadius: 6 }}
    >
      {/* Grid */}
      {[0.25, 0.5, 0.75].map(t => (
        <line key={t} x1={0} y1={CY - AMP * t} x2={W} y2={CY - AMP * t}
          stroke="#1e2035" strokeWidth={1} strokeDasharray="4 4" />
      ))}
      {[0.25, 0.5, 0.75].map(t => (
        <line key={-t} x1={0} y1={CY + AMP * t} x2={W} y2={CY + AMP * t}
          stroke="#1e2035" strokeWidth={1} strokeDasharray="4 4" />
      ))}
      {/* Zero line */}
      <line x1={0} y1={CY} x2={W} y2={CY} stroke="#2d3154" strokeWidth={1} />
      {children}
    </svg>
  )
}

function TimeDomainSVG({ id }) {
  return (
    <PlotSVG id={id}>
      <defs>
        <filter id="glow">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>
      {/* Shadow */}
      <path d={TIME_PATH} fill="none" stroke="#3b82f6" strokeWidth={3} opacity={0.15} />
      {/* Signal */}
      <path d={TIME_PATH} fill="none" stroke="#3b82f6" strokeWidth={1.5}
        filter="url(#glow)" strokeLinejoin="round" strokeLinecap="round" />
      {/* X-axis labels */}
      {[0, 0.25, 0.5, 0.75, 1].map(t => (
        <text key={t} x={t * W} y={H - 3} fontSize={8}
          fill="#64748b" textAnchor="middle">{t.toFixed(2)}s</text>
      ))}
    </PlotSVG>
  )
}

function FreqDomainSVG({ id }) {
  const baseline = H - 18
  return (
    <PlotSVG id={id}>
      {FREQ_BARS.map(b => (
        <g key={b.f}>
          <rect x={b.x - 4} y={baseline - b.barH} width={8} height={b.barH}
            fill={b.color} opacity={b.amp > 0.1 ? 0.9 : 0.5} rx={2} />
          {b.amp > 0.1 && (
            <text x={b.x} y={baseline - b.barH - 4} fontSize={8}
              fill={b.color} textAnchor="middle" opacity={0.9}>{b.f}Hz</text>
          )}
        </g>
      ))}
      <line x1={0} y1={baseline} x2={W} y2={baseline} stroke="#2d3154" strokeWidth={1} />
      {[3, 6, 9, 12].map(f => (
        <text key={f} x={(f / 12) * W} y={H - 3} fontSize={8}
          fill="#64748b" textAnchor="middle">{f}Hz</text>
      ))}
    </PlotSVG>
  )
}

// ─── Download helper ──────────────────────────────────────────────────────────

function downloadSVG(svgId, filename) {
  const el = document.getElementById(svgId)
  if (!el) return
  const blob = new Blob([el.outerHTML], { type: 'image/svg+xml' })
  const url = URL.createObjectURL(blob)
  const a = Object.assign(document.createElement('a'), { href: url, download: filename })
  a.click()
  URL.revokeObjectURL(url)
}

// ─── Plot card ────────────────────────────────────────────────────────────────

function PlotCard({ title, label, svgId, SvgComponent, onMaximize }) {
  const [scale, setScale] = useState(1)

  return (
    <div style={s.card}>
      <div style={s.cardHeader}>
        <span style={s.cardLabel}>{label}</span>
        <div style={s.toolbar}>
          <ToolBtn title="Zoom in"   onClick={() => setScale(v => Math.min(v + 0.25, 3))}>
            <ZoomIn size={13} />
          </ToolBtn>
          <ToolBtn title="Zoom out"  onClick={() => setScale(v => Math.max(v - 0.25, 0.5))}>
            <ZoomOut size={13} />
          </ToolBtn>
          <ToolBtn title="Download"  onClick={() => downloadSVG(svgId, `${label.replace(/\s+/g,'_')}.svg`)}>
            <Download size={13} />
          </ToolBtn>
          <ToolBtn title="Fullscreen" onClick={onMaximize}>
            <Maximize2 size={13} />
          </ToolBtn>
        </div>
      </div>
      <div style={{ ...s.plotWrap, transform: `scale(${scale})`, transformOrigin: 'top left',
        width: `${100 / scale}%`, height: scale !== 1 ? 130 * scale : undefined }}>
        <SvgComponent id={svgId} />
      </div>
    </div>
  )
}

function ToolBtn({ children, onClick, title }) {
  return (
    <button style={s.toolBtn} onClick={onClick} title={title}>
      {children}
    </button>
  )
}

// ─── Lightbox ────────────────────────────────────────────────────────────────

function Lightbox({ title, svgId, SvgComponent, onClose }) {
  return (
    <div style={s.overlay} onClick={onClose}>
      <div style={s.lightbox} onClick={e => e.stopPropagation()}>
        <div style={s.lightboxHeader}>
          <span style={s.lightboxTitle}>{title}</span>
          <div style={s.toolbar}>
            <ToolBtn title="Download" onClick={() => downloadSVG(svgId + '-lg', `${title}.svg`)}>
              <Download size={14} />
            </ToolBtn>
            <ToolBtn title="Close" onClick={onClose}>
              <X size={14} />
            </ToolBtn>
          </div>
        </div>
        <SvgComponent id={svgId + '-lg'} />
      </div>
    </div>
  )
}

// ─── Main export ──────────────────────────────────────────────────────────────

const DEMO_PLOTS = [
  { id: 'plot-time', label: 'Time Domain  x(t)',  Component: TimeDomainSVG  },
  { id: 'plot-freq', label: 'Frequency Domain  X(f)', Component: FreqDomainSVG },
]

export default function PlotDisplay({ title = 'Signal Analysis', plots = DEMO_PLOTS, mode = 'dual', imageBase64 = null }) {
  const [maximized, setMaximized] = useState(null)

  // If we have a real base64 image from backend, show it directly
  if (imageBase64) {
    return (
      <div style={s.root}>
        <div style={s.header}>
          <span style={s.title}>{title}</span>
          <span style={s.badge}>Signal Plot</span>
        </div>
        <div style={{ padding: '12px', background: '#0b0d18' }}>
          <img
            src={`data:image/png;base64,${imageBase64}`}
            alt="Signal Plot"
            style={{
              width: '100%',
              borderRadius: 8,
              display: 'block'
            }}
          />
        </div>
      </div>
    )
  }

  // Otherwise show demo plots
  return (
    <div style={s.root}>
      <div style={s.header}>
        <span style={s.title}>{title}</span>
        <span style={s.badge}>{mode === 'dual' ? 'Time · Frequency' : 'Plot'}</span>
      </div>

      <div style={{ ...s.grid, gridTemplateColumns: mode === 'dual' ? '1fr 1fr' : '1fr' }}>
        {plots.map(p => (
          <PlotCard
            key={p.id}
            label={p.label}
            svgId={p.id}
            SvgComponent={p.Component}
            onMaximize={() => setMaximized(p)}
          />
        ))}
      </div>

      {maximized && (
        <Lightbox
          title={maximized.label}
          svgId={maximized.id}
          SvgComponent={maximized.Component}
          onClose={() => setMaximized(null)}
        />
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
    padding: '10px 14px 8px',
    borderBottom: '1px solid var(--border)',
  },
  title: {
    fontSize: 13,
    fontWeight: 600,
    color: 'var(--text-primary)',
  },
  badge: {
    fontSize: 11,
    color: 'var(--text-muted)',
    background: 'var(--bg-surface)',
    border: '1px solid var(--border)',
    padding: '2px 8px',
    borderRadius: 20,
  },
  grid: {
    display: 'grid',
    gap: 1,
    background: 'var(--border)',
  },
  card: {
    background: 'var(--bg-panel)',
    overflow: 'hidden',
  },
  cardHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '6px 10px',
    borderBottom: '1px solid var(--border)',
  },
  cardLabel: {
    fontSize: 11,
    fontWeight: 600,
    color: 'var(--text-muted)',
    fontFamily: 'var(--font-mono)',
    letterSpacing: '0.03em',
  },
  toolbar: {
    display: 'flex',
    gap: 2,
  },
  toolBtn: {
    width: 24,
    height: 24,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 4,
    cursor: 'pointer',
    color: 'var(--text-muted)',
    border: 'none',
    background: 'none',
    transition: 'background 0.12s, color 0.12s',
  },
  plotWrap: {
    padding: '8px 10px 4px',
    overflow: 'hidden',
    transition: 'transform 0.2s',
  },

  // lightbox
  overlay: {
    position: 'fixed',
    inset: 0,
    background: 'rgba(0,0,0,0.75)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 200,
    backdropFilter: 'blur(4px)',
  },
  lightbox: {
    background: 'var(--bg-panel)',
    border: '1px solid var(--border)',
    borderRadius: 12,
    overflow: 'hidden',
    width: 'min(860px, 92vw)',
    boxShadow: '0 24px 80px rgba(0,0,0,0.6)',
  },
  lightboxHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '10px 14px',
    borderBottom: '1px solid var(--border)',
  },
  lightboxTitle: {
    fontSize: 13,
    fontWeight: 600,
    color: 'var(--text-primary)',
    fontFamily: 'var(--font-mono)',
  },
}
