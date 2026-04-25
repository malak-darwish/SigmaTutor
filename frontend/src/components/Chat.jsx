import { useRef, useEffect, useState } from 'react'
import { ArrowUp } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import 'katex/dist/katex.min.css'

// ─── Markdown renderer ────────────────────────────────────────────────────────

const MD_PLUGINS = { remark: [remarkMath], rehype: [rehypeKatex] }

function CodeBlock({ className, children }) {
  const lang = /language-(\w+)/.exec(className || '')?.[1]
  if (!lang) {
    return <code className="md-inline-code">{children}</code>
  }
  return (
    <SyntaxHighlighter
      language={lang}
      style={oneDark}
      PreTag="div"
      customStyle={{
        margin: '12px 0',
        borderRadius: 8,
        fontSize: 13,
        background: '#0d0f1a',
        border: '1px solid var(--border)',
      }}
      codeTagProps={{ style: { fontFamily: 'var(--font-mono)' } }}
    >
      {String(children).replace(/\n$/, '')}
    </SyntaxHighlighter>
  )
}

function MdImage({ src, alt }) {
  return (
    <img
      src={src}
      alt={alt || ''}
      style={{ maxWidth: '100%', borderRadius: 8, margin: '8px 0', display: 'block' }}
    />
  )
}

const MD_COMPONENTS = {
  code: CodeBlock,
  img: MdImage,
}

function MarkdownContent({ children }) {
  return (
    <div className="md">
      <ReactMarkdown
        remarkPlugins={MD_PLUGINS.remark}
        rehypePlugins={MD_PLUGINS.rehype}
        components={MD_COMPONENTS}
      >
        {children}
      </ReactMarkdown>
    </div>
  )
}

// ─── Avatars ──────────────────────────────────────────────────────────────────

function SigmaAvatar() {
  return (
    <div style={s.sigmaAvatar}>Σ</div>
  )
}

// ─── Messages ────────────────────────────────────────────────────────────────

function AIMessage({ content }) {
  return (
    <div style={s.aiRow}>
      <SigmaAvatar />
      <div style={s.aiContent}>
        <span style={s.aiName}>ΣTutor</span>
        <MarkdownContent>{content}</MarkdownContent>
      </div>
    </div>
  )
}

function UserMessage({ content }) {
  return (
    <div style={s.userRow}>
      <div style={s.userBubble}>{content}</div>
    </div>
  )
}

// ─── Typing dots ─────────────────────────────────────────────────────────────

function TypingDots() {
  return (
    <div style={s.aiRow}>
      <SigmaAvatar />
      <div style={s.typingDots}>
        <span style={{ '--i': 0 }} className="dot" />
        <span style={{ '--i': 1 }} className="dot" />
        <span style={{ '--i': 2 }} className="dot" />
      </div>
    </div>
  )
}

// ─── Empty state ─────────────────────────────────────────────────────────────

const PROMPTS = [
  'Explain the Fourier Transform',
  'What is the convolution theorem?',
  'Derive the Nyquist sampling theorem',
  'Sketch a Bode plot for a low-pass filter',
]

function EmptyState({ onPrompt }) {
  return (
    <div style={s.empty}>
      <div style={s.emptyAvatar}>Σ</div>
      <h2 style={s.emptyTitle}>What would you like to learn?</h2>
      <p style={s.emptySub}>Ask anything about Signals &amp; Systems, or try one of these:</p>
      <div style={s.prompts}>
        {PROMPTS.map(p => (
          <button key={p} style={s.promptChip} onClick={() => onPrompt(p)}>
            {p}
          </button>
        ))}
      </div>
    </div>
  )
}

// ─── Input bar ───────────────────────────────────────────────────────────────

function InputBar({ value, onChange, onSubmit, disabled }) {
  const ref = useRef(null)

  function handleChange(e) {
    onChange(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px'
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSubmit()
    }
  }

  const active = value.trim().length > 0 && !disabled

  return (
    <div style={s.inputWrap}>
      <div style={s.inputBox}>
        <textarea
          ref={ref}
          style={s.textarea}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKey}
          placeholder="Message ΣTutor…"
          rows={1}
          disabled={disabled}
        />
        <button
          style={{ ...s.sendBtn, background: active ? 'var(--accent-blue)' : 'var(--bg-hover)' }}
          onClick={onSubmit}
          disabled={!active}
          title="Send (Enter)"
        >
          <ArrowUp size={16} color={active ? '#fff' : 'var(--text-muted)'} strokeWidth={2.5} />
        </button>
      </div>
      <p style={s.hint}>Enter to send &nbsp;·&nbsp; Shift+Enter for new line</p>
    </div>
  )
}

// ─── Chat root ────────────────────────────────────────────────────────────────

export default function Chat({ messages = [], onSend, loading = false }) {
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  function submit() {
    const text = input.trim()
    if (!text || loading) return
    onSend?.(text)
    setInput('')
  }

  function handlePrompt(text) {
    onSend?.(text)
  }

  return (
    <div style={s.root}>
      <div style={s.scrollArea}>
        <div style={s.messageList}>
          {messages.length === 0 && !loading
            ? <EmptyState onPrompt={handlePrompt} />
            : messages.map((m, i) =>
                m.role === 'user'
                  ? <UserMessage key={i} content={m.content} />
                  : <AIMessage   key={i} content={m.content} />
              )
          }
          {loading && <TypingDots />}
          <div ref={bottomRef} />
        </div>
      </div>

      <InputBar
        value={input}
        onChange={setInput}
        onSubmit={submit}
        disabled={loading}
      />

      <style>{INJECTED_CSS}</style>
    </div>
  )
}

// ─── Injected CSS (markdown + dots) ──────────────────────────────────────────

const INJECTED_CSS = `
  /* markdown content */
  .md { font-size: 14px; line-height: 1.75; color: var(--text-primary); }
  .md > *:first-child { margin-top: 0 !important; }
  .md > *:last-child  { margin-bottom: 0 !important; }

  .md p  { margin: 0 0 10px; }
  .md h1 { font-size: 20px; font-weight: 700; margin: 20px 0 10px; color: var(--text-primary); }
  .md h2 { font-size: 17px; font-weight: 700; margin: 18px 0 8px;  color: var(--text-primary); }
  .md h3 { font-size: 15px; font-weight: 600; margin: 14px 0 6px;  color: var(--text-primary); }

  .md ul, .md ol { margin: 6px 0 10px 20px; padding: 0; }
  .md li         { margin: 3px 0; }

  .md blockquote {
    margin: 10px 0;
    padding: 8px 14px;
    border-left: 3px solid var(--accent-blue);
    background: rgba(59,130,246,.07);
    border-radius: 0 6px 6px 0;
    color: var(--text-secondary);
  }

  .md table {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 13px;
  }
  .md th {
    background: var(--bg-surface);
    color: var(--text-primary);
    font-weight: 600;
    padding: 7px 12px;
    text-align: left;
    border: 1px solid var(--border);
  }
  .md td {
    padding: 6px 12px;
    border: 1px solid var(--border);
    color: var(--text-secondary);
  }
  .md tr:nth-child(even) td { background: rgba(255,255,255,.02); }

  .md-inline-code {
    font-family: var(--font-mono);
    font-size: 12.5px;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    padding: 1px 5px;
    border-radius: 4px;
    color: var(--accent-green);
  }

  .md a { color: var(--accent-blue); text-decoration: underline; text-underline-offset: 2px; }
  .md hr { border: none; border-top: 1px solid var(--border); margin: 14px 0; }
  .md strong { font-weight: 700; color: var(--text-primary); }

  /* katex display block spacing */
  .md .katex-display { margin: 14px 0; overflow-x: auto; }

  /* typing dots */
  @keyframes bounce {
    0%, 80%, 100% { transform: translateY(0);    opacity: .4; }
    40%           { transform: translateY(-5px);  opacity: 1;  }
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

// ─── Inline styles ────────────────────────────────────────────────────────────

const s = {
  root: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    overflow: 'hidden',
  },

  scrollArea: {
    flex: 1,
    overflowY: 'auto',
    display: 'flex',
    flexDirection: 'column',
  },

  messageList: {
    width: '100%',
    maxWidth: 780,
    margin: '0 auto',
    padding: '32px 24px 16px',
    display: 'flex',
    flexDirection: 'column',
    gap: 24,
    flex: 1,
  },

  /* AI row */
  aiRow: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: 12,
    width: '100%',
  },
  sigmaAvatar: {
    width: 32,
    height: 32,
    borderRadius: 8,
    background: 'linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 15,
    fontWeight: 800,
    color: '#fff',
    flexShrink: 0,
    letterSpacing: '-1px',
    marginTop: 2,
  },
  aiContent: {
    flex: 1,
    minWidth: 0,
    display: 'flex',
    flexDirection: 'column',
    gap: 4,
  },
  aiName: {
    fontSize: 12,
    fontWeight: 700,
    color: 'var(--accent-blue)',
    letterSpacing: '0.02em',
  },

  /* user row */
  userRow: {
    display: 'flex',
    justifyContent: 'flex-end',
    width: '100%',
  },
  userBubble: {
    maxWidth: '72%',
    padding: '10px 14px',
    borderRadius: 16,
    borderBottomRightRadius: 4,
    background: 'var(--accent-blue)',
    color: '#fff',
    fontSize: 14,
    lineHeight: 1.6,
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
  },

  /* typing */
  typingDots: {
    display: 'flex',
    alignItems: 'center',
    gap: 5,
    padding: '10px 0 6px',
    height: 32,
  },

  /* empty state */
  empty: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
    paddingBottom: 80,
    textAlign: 'center',
  },
  emptyAvatar: {
    width: 64,
    height: 64,
    borderRadius: 18,
    background: 'linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 32,
    fontWeight: 800,
    color: '#fff',
    marginBottom: 4,
    boxShadow: '0 4px 24px rgba(59,130,246,.35)',
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 700,
    color: 'var(--text-primary)',
    margin: 0,
  },
  emptySub: {
    fontSize: 13,
    color: 'var(--text-muted)',
    margin: 0,
  },
  prompts: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 8,
    justifyContent: 'center',
    marginTop: 4,
    maxWidth: 520,
  },
  promptChip: {
    padding: '7px 14px',
    borderRadius: 20,
    border: '1px solid var(--border)',
    background: 'var(--bg-panel)',
    color: 'var(--text-secondary)',
    fontSize: 13,
    cursor: 'pointer',
    transition: 'border-color 0.15s, color 0.15s',
  },

  /* input */
  inputWrap: {
    padding: '12px 24px 16px',
    background: 'var(--bg-base)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 6,
  },
  inputBox: {
    width: '100%',
    maxWidth: 780,
    display: 'flex',
    alignItems: 'flex-end',
    gap: 8,
    background: 'var(--bg-panel)',
    border: '1px solid var(--border)',
    borderRadius: 14,
    padding: '6px 8px 6px 14px',
  },
  textarea: {
    flex: 1,
    resize: 'none',
    background: 'transparent',
    border: 'none',
    outline: 'none',
    padding: '6px 0',
    lineHeight: 1.6,
    fontSize: 14,
    color: 'var(--text-primary)',
    maxHeight: 160,
    overflowY: 'auto',
    fontFamily: 'var(--font-ui)',
  },
  sendBtn: {
    width: 34,
    height: 34,
    borderRadius: 9,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
    transition: 'background 0.15s',
    cursor: 'pointer',
    border: 'none',
  },
  hint: {
    fontSize: 11,
    color: 'var(--text-muted)',
    margin: 0,
  },
}
