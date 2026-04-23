import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import { ChevronLeft, ChevronRight, Eye, EyeOff, CheckCircle2, Circle, BookOpen } from 'lucide-react'
import 'katex/dist/katex.min.css'

// ─── Mock problems ────────────────────────────────────────────────────────────

const PROBLEMS = [
  {
    id: 1,
    topic: 'Fourier Analysis',
    difficulty: 'Medium',
    title: 'Fourier Transform of a Rectangular Pulse',
    problem: `Find the Fourier transform of the rectangular pulse:

$$x(t) = \\operatorname{rect}\\!\\left(\\frac{t}{T}\\right) = \\begin{cases} 1 & |t| \\leq T/2 \\\\ 0 & |t| > T/2 \\end{cases}$$

where $T > 0$ is the pulse width.

Express your answer using the normalised sinc function $\\operatorname{sinc}(u) = \\dfrac{\\sin(\\pi u)}{\\pi u}$, and describe the location of the spectral nulls.`,

    solution: `Apply the Fourier transform definition directly — the limits collapse to a finite integral:

$$X(f) = \\int_{-\\infty}^{\\infty} x(t)\\,e^{-j2\\pi ft}\\,dt = \\int_{-T/2}^{T/2} e^{-j2\\pi ft}\\,dt$$

Evaluate the integral:

$$X(f) = \\left[\\frac{e^{-j2\\pi ft}}{-j2\\pi f}\\right]_{-T/2}^{T/2} = \\frac{e^{-j\\pi fT} - e^{\\,j\\pi fT}}{-j2\\pi f}$$

Use the identity $\\sin\\theta = \\dfrac{e^{\\,j\\theta}-e^{-j\\theta}}{2j}$:

$$X(f) = \\frac{2j\\sin(\\pi fT)}{j\\cdot 2\\pi f} = T\\cdot\\frac{\\sin(\\pi fT)}{\\pi fT}$$

$$\\boxed{X(f) = T\\operatorname{sinc}(fT)}$$

**Key observations:**
- Main lobe width: $2/T$ Hz (wider pulse → narrower spectrum)
- Spectral **nulls** at $f = n/T$ for $n = \\pm1, \\pm2, \\ldots$
- This transform pair encodes the **time–bandwidth uncertainty** principle`,
  },

  {
    id: 2,
    topic: 'Sampling Theory',
    difficulty: 'Medium',
    title: 'Aliasing and the Nyquist Criterion',
    problem: `A continuous-time signal $x(t)$ contains exactly three frequency components: **1 kHz**, **3.5 kHz**, and **6 kHz**.

**(a)** What is the minimum sampling rate required to reconstruct $x(t)$ without aliasing?

**(b)** The signal is instead sampled at $f_s = 8\\text{ kHz}$. Determine which components are preserved and which alias. For any aliased component, calculate the aliased frequency.

**(c)** Write the general aliasing formula and use it to verify your answer in (b).`,

    solution: `**(a)** The **Nyquist–Shannon theorem** requires $f_s > 2f_{\\max}$:

$$f_s > 2 \\times 6{,}000 = 12{,}000\\text{ Hz}$$

Minimum sampling rate: **12 kHz**.

---

**(b)** With $f_s = 8\\text{ kHz}$, the Nyquist limit is $f_N = f_s/2 = 4\\text{ kHz}$.

| Component | vs. $f_N$ | Outcome |
|---|---|---|
| 1 kHz | $1 < 4$ kHz | ✓ preserved at **1 kHz** |
| 3.5 kHz | $3.5 < 4$ kHz | ✓ preserved at **3.5 kHz** |
| 6 kHz | $6 > 4$ kHz | ✗ **aliases** |

---

**(c)** The aliasing formula maps $f$ to its alias:

$$f_{\\text{alias}} = \\left|\\,f - k\\,f_s\\,\\right|, \\qquad k \\in \\mathbb{Z}, \\quad f_{\\text{alias}} \\leq \\tfrac{f_s}{2}$$

For the 6 kHz component, choose $k = 1$:

$$f_{\\text{alias}} = |\\,6000 - 1 \\times 8000\\,| = 2000\\text{ Hz}$$

$$\\boxed{\\text{The 6 kHz tone aliases to 2 kHz}}$$

It is **indistinguishable** from a genuine 2 kHz component — anti-aliasing filters must remove it *before* sampling.`,
  },

  {
    id: 3,
    topic: 'LTI Systems',
    difficulty: 'Hard',
    title: 'Partial Fractions and Impulse Response',
    problem: `A causal LTI system has the transfer function:

$$H(s) = \\frac{3s + 7}{s^2 + 5s + 6}, \\qquad \\operatorname{Re}(s) > -2$$

**(a)** Factorise the denominator. State all poles and zeros.

**(b)** Expand $H(s)$ in partial fractions and hence find the impulse response $h(t)$.

**(c)** Determine whether the system is BIBO stable. Justify using the pole locations and the region of convergence.`,

    solution: `**(a)** Factorise the denominator:

$$s^2 + 5s + 6 = (s+2)(s+3)$$

- **Zero:** $3s + 7 = 0 \\Rightarrow s_z = -\\tfrac{7}{3} \\approx -2.33$
- **Poles:** $s_1 = -2$ and $s_2 = -3$

All critical frequencies are **real and negative**.

---

**(b)** Write the partial fraction expansion:

$$H(s) = \\frac{3s+7}{(s+2)(s+3)} = \\frac{A}{s+2} + \\frac{B}{s+3}$$

Apply the **Heaviside cover-up** method:

$$A = \\frac{3s+7}{s+3}\\Bigg|_{s=-2} = \\frac{-6+7}{1} = 1$$

$$B = \\frac{3s+7}{s+2}\\Bigg|_{s=-3} = \\frac{-9+7}{-1} = 2$$

Using $\\mathcal{L}^{-1}\\!\\left\\{\\dfrac{1}{s+a}\\right\\} = e^{-at}u(t)$ for each term:

$$\\boxed{h(t) = \\bigl(e^{-2t} + 2\\,e^{-3t}\\bigr)\\,u(t)}$$

---

**(c)** Both poles lie in the **open left half-plane** ($\\operatorname{Re}(s) < 0$) and the ROC $\\operatorname{Re}(s) > -2$ includes the $j\\omega$-axis.

$h(t)$ decays exponentially to zero, so $\\int_0^\\infty |h(t)|\\,dt < \\infty$.

The system is **BIBO stable**. ✓`,
  },
]

// ─── Difficulty config ────────────────────────────────────────────────────────

const DIFF = {
  Easy:   { color: '#10b981', bg: 'rgba(16,185,129,.12)',  border: 'rgba(16,185,129,.3)'  },
  Medium: { color: '#f59e0b', bg: 'rgba(245,158,11,.12)',  border: 'rgba(245,158,11,.3)'  },
  Hard:   { color: '#ef4444', bg: 'rgba(239,68,68,.12)',   border: 'rgba(239,68,68,.3)'   },
}

// ─── Markdown renderer (shared config) ───────────────────────────────────────

const MD_REMARK  = [remarkMath]
const MD_REHYPE  = [rehypeKatex]

function Md({ children }) {
  return (
    <div className="ep-md">
      <ReactMarkdown remarkPlugins={MD_REMARK} rehypePlugins={MD_REHYPE}>
        {children}
      </ReactMarkdown>
    </div>
  )
}

// ─── Progress stepper ─────────────────────────────────────────────────────────

function Stepper({ current, total, revealed }) {
  return (
    <div style={s.stepper}>
      {Array.from({ length: total }, (_, i) => {
        const done    = revealed.has(i)
        const active  = i === current
        const visited = i < current

        return (
          <div key={i} style={s.stepItem}>
            {/* connector line before */}
            {i > 0 && (
              <div style={{
                ...s.stepLine,
                background: (visited || done) ? 'var(--accent-green)' : 'var(--border)',
              }} />
            )}

            <div
              title={`Problem ${i + 1}`}
              style={{
                ...s.stepDot,
                ...(active  ? s.stepDotActive  : {}),
                ...(done    ? s.stepDotDone    : {}),
                ...(!active && !done ? s.stepDotIdle : {}),
              }}
            >
              {done
                ? <CheckCircle2 size={14} strokeWidth={2.5} />
                : <span style={{ fontSize: 11, fontWeight: 700 }}>{i + 1}</span>
              }
            </div>
          </div>
        )
      })}
    </div>
  )
}

// ─── Main component ───────────────────────────────────────────────────────────

export default function ExamPanel() {
  const [index,        setIndex]        = useState(0)
  const [showSolution, setShowSolution] = useState(false)
  const [revealed,     setRevealed]     = useState(new Set())

  const problem = PROBLEMS[index]
  const total   = PROBLEMS.length
  const diff    = DIFF[problem.difficulty]

  function goTo(i) {
    setIndex(i)
    setShowSolution(false)
  }

  function handleReveal() {
    setShowSolution(true)
    setRevealed(prev => new Set([...prev, index]))
  }

  const isFirst = index === 0
  const isLast  = index === total - 1

  return (
    <div style={s.page}>
      <div style={s.card}>

        {/* ── Top bar ── */}
        <div style={s.topBar}>
          <div style={s.topLeft}>
            <BookOpen size={15} color="var(--accent-blue)" />
            <span style={s.topTitle}>Exam Mode</span>
          </div>
          <span style={s.counter}>
            Problem <strong style={{ color: 'var(--text-primary)' }}>{index + 1}</strong> of {total}
          </span>
        </div>

        {/* ── Stepper ── */}
        <div style={s.stepperWrap}>
          <Stepper current={index} total={total} revealed={revealed} />
        </div>

        {/* ── Problem body ── */}
        <div style={s.body}>

          {/* Badges */}
          <div style={s.badges}>
            <span style={s.topicBadge}>{problem.topic}</span>
            <span style={{
              ...s.diffBadge,
              color: diff.color,
              background: diff.bg,
              borderColor: diff.border,
            }}>
              {problem.difficulty}
            </span>
          </div>

          {/* Title */}
          <h2 style={s.problemTitle}>
            <span style={s.problemNum}>Q{problem.id}.</span>
            {' '}{problem.title}
          </h2>

          {/* Problem statement */}
          <div style={s.problemBox}>
            <Md>{problem.problem}</Md>
          </div>

          {/* Solution toggle */}
          <div style={s.solutionToggleRow}>
            <button
              style={{
                ...s.solutionBtn,
                ...(showSolution ? s.solutionBtnActive : {}),
              }}
              onClick={showSolution ? () => setShowSolution(false) : handleReveal}
            >
              {showSolution
                ? <><EyeOff size={14} /><span>Hide Solution</span></>
                : <><Eye     size={14} /><span>Show Solution</span></>}
            </button>

            {revealed.has(index) && !showSolution && (
              <span style={s.revealedHint}>Solution previously shown</span>
            )}
          </div>

          {/* Solution */}
          {showSolution && (
            <div style={s.solutionBox} className="ep-solution-reveal">
              <div style={s.solutionHeader}>
                <CheckCircle2 size={14} color="var(--accent-green)" />
                <span style={s.solutionLabel}>Solution</span>
              </div>
              <Md>{problem.solution}</Md>
            </div>
          )}

        </div>

        {/* ── Footer nav ── */}
        <div style={s.footer}>
          <button
            style={{ ...s.navBtn, opacity: isFirst ? 0.35 : 1 }}
            onClick={() => !isFirst && goTo(index - 1)}
            disabled={isFirst}
          >
            <ChevronLeft size={16} />
            Previous
          </button>

          <div style={s.dotRow}>
            {PROBLEMS.map((_, i) => (
              <button
                key={i}
                style={{
                  ...s.dot,
                  background: i === index
                    ? 'var(--accent-blue)'
                    : revealed.has(i) ? 'var(--accent-green)'
                    : 'var(--bg-hover)',
                  transform: i === index ? 'scale(1.3)' : 'scale(1)',
                }}
                onClick={() => goTo(i)}
                title={`Go to problem ${i + 1}`}
              />
            ))}
          </div>

          <button
            style={{ ...s.navBtn, ...(isLast ? s.navBtnFinish : {}) }}
            onClick={() => !isLast && goTo(index + 1)}
          >
            {isLast ? 'Finish' : 'Next'}
            {!isLast && <ChevronRight size={16} />}
          </button>
        </div>

      </div>

      <style>{INJECTED_CSS}</style>
    </div>
  )
}

// ─── Injected CSS ─────────────────────────────────────────────────────────────

const INJECTED_CSS = `
  .ep-md { font-size: 14px; line-height: 1.8; color: var(--text-primary); }
  .ep-md > *:first-child { margin-top: 0 !important; }
  .ep-md > *:last-child  { margin-bottom: 0 !important; }

  .ep-md p  { margin: 0 0 10px; }
  .ep-md h1 { font-size: 18px; font-weight: 700; margin: 18px 0 8px;  }
  .ep-md h2 { font-size: 15px; font-weight: 700; margin: 16px 0 6px;  }
  .ep-md h3 { font-size: 14px; font-weight: 600; margin: 12px 0 4px;  }

  .ep-md ul, .ep-md ol { margin: 6px 0 10px 20px; }
  .ep-md li { margin: 3px 0; }

  .ep-md strong { font-weight: 700; color: var(--text-primary); }

  .ep-md table {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 13px;
  }
  .ep-md th {
    background: var(--bg-surface);
    color: var(--text-primary);
    font-weight: 600;
    padding: 7px 12px;
    text-align: left;
    border: 1px solid var(--border);
  }
  .ep-md td {
    padding: 6px 12px;
    border: 1px solid var(--border);
    color: var(--text-secondary);
  }
  .ep-md tr:nth-child(even) td { background: rgba(255,255,255,.02); }

  .ep-md code {
    font-family: var(--font-mono);
    font-size: 12.5px;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    padding: 1px 5px;
    border-radius: 4px;
    color: var(--accent-green);
  }

  .ep-md hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }

  .ep-md .katex-display { margin: 16px 0; overflow-x: auto; }

  /* solution reveal animation */
  @keyframes ep-reveal {
    from { opacity: 0; transform: translateY(-6px); }
    to   { opacity: 1; transform: translateY(0);    }
  }
  .ep-solution-reveal {
    animation: ep-reveal 0.25s ease;
  }
`

// ─── Styles ───────────────────────────────────────────────────────────────────

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

  /* top bar */
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
    letterSpacing: '-0.2px',
  },
  counter: {
    fontSize: 12,
    color: 'var(--text-muted)',
  },

  /* stepper */
  stepperWrap: {
    padding: '14px 20px 12px',
    borderBottom: '1px solid var(--border)',
    background: 'var(--bg-surface)',
  },
  stepper: {
    display: 'flex',
    alignItems: 'center',
    gap: 0,
  },
  stepItem: {
    display: 'flex',
    alignItems: 'center',
    flex: 1,
  },
  stepLine: {
    flex: 1,
    height: 2,
    borderRadius: 1,
    transition: 'background 0.3s',
  },
  stepDot: {
    width: 32,
    height: 32,
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
    transition: 'background 0.2s, border-color 0.2s',
    cursor: 'default',
  },
  stepDotActive: {
    background: 'var(--accent-blue)',
    color: '#fff',
    boxShadow: '0 0 0 3px rgba(59,130,246,.25)',
  },
  stepDotDone: {
    background: 'var(--accent-green)',
    color: '#fff',
  },
  stepDotIdle: {
    background: 'var(--bg-hover)',
    color: 'var(--text-muted)',
    border: '2px solid var(--border)',
  },

  /* body */
  body: {
    padding: '24px 28px 20px',
    display: 'flex',
    flexDirection: 'column',
    gap: 18,
  },

  badges: {
    display: 'flex',
    gap: 8,
    alignItems: 'center',
  },
  topicBadge: {
    fontSize: 11,
    fontWeight: 600,
    color: 'var(--accent-blue)',
    background: 'rgba(59,130,246,.1)',
    border: '1px solid rgba(59,130,246,.25)',
    padding: '3px 10px',
    borderRadius: 20,
    letterSpacing: '0.02em',
  },
  diffBadge: {
    fontSize: 11,
    fontWeight: 600,
    padding: '3px 10px',
    borderRadius: 20,
    border: '1px solid',
    letterSpacing: '0.02em',
  },

  problemTitle: {
    fontSize: 17,
    fontWeight: 700,
    color: 'var(--text-primary)',
    lineHeight: 1.35,
    margin: 0,
    letterSpacing: '-0.3px',
  },
  problemNum: {
    color: 'var(--accent-blue)',
    fontVariantNumeric: 'tabular-nums',
  },

  problemBox: {
    background: 'var(--bg-base)',
    border: '1px solid var(--border)',
    borderRadius: 10,
    padding: '16px 18px',
  },

  /* solution toggle */
  solutionToggleRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
  },
  solutionBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: 7,
    padding: '8px 16px',
    borderRadius: 8,
    fontSize: 13,
    fontWeight: 600,
    cursor: 'pointer',
    border: '1px solid var(--border)',
    background: 'var(--bg-surface)',
    color: 'var(--text-secondary)',
    transition: 'background 0.15s, color 0.15s, border-color 0.15s',
  },
  solutionBtnActive: {
    background: 'rgba(16,185,129,.1)',
    color: 'var(--accent-green)',
    borderColor: 'rgba(16,185,129,.3)',
  },
  revealedHint: {
    fontSize: 11,
    color: 'var(--text-muted)',
    fontStyle: 'italic',
  },

  /* solution box */
  solutionBox: {
    background: 'rgba(16,185,129,.05)',
    border: '1px solid rgba(16,185,129,.2)',
    borderRadius: 10,
    padding: '16px 18px',
    display: 'flex',
    flexDirection: 'column',
    gap: 10,
  },
  solutionHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    paddingBottom: 10,
    borderBottom: '1px solid rgba(16,185,129,.15)',
  },
  solutionLabel: {
    fontSize: 12,
    fontWeight: 700,
    color: 'var(--accent-green)',
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
  },

  /* footer */
  footer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '14px 20px',
    borderTop: '1px solid var(--border)',
    background: 'var(--bg-surface)',
  },
  navBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: 5,
    padding: '8px 16px',
    borderRadius: 8,
    fontSize: 13,
    fontWeight: 600,
    color: 'var(--text-secondary)',
    background: 'var(--bg-hover)',
    border: '1px solid var(--border)',
    cursor: 'pointer',
    transition: 'background 0.15s, color 0.15s',
  },
  navBtnFinish: {
    color: 'var(--accent-green)',
    background: 'rgba(16,185,129,.1)',
    borderColor: 'rgba(16,185,129,.3)',
  },
  dotRow: {
    display: 'flex',
    gap: 6,
    alignItems: 'center',
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: '50%',
    border: 'none',
    cursor: 'pointer',
    transition: 'background 0.2s, transform 0.2s',
    padding: 0,
  },
}
