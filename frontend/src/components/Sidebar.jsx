import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import {
  MessageSquare, Waves, GraduationCap,
  Plus, PanelLeftClose, PanelLeftOpen,
  Clock, MessageCircle, Zap, BarChart2, CheckCircle2, Circle,
} from 'lucide-react'

const EXPANDED_W = 260
const COLLAPSED_W = 56

const NAV = [
  { to: '/',        end: true,  icon: MessageSquare, label: 'Chat',              color: 'var(--accent-blue)'   },
  { to: '/sandbox', end: false, icon: Waves,         label: 'Frequency Sandbox', color: 'var(--accent-green)'  },
  { to: '/exam',    end: false, icon: GraduationCap, label: 'Exam Mode',         color: 'var(--accent-purple)' },
]

const QUICK_ACTIONS = [
  { label: ' Plot sine wave',      msg: 'Plot a 10Hz sine wave' },
  { label: ' Prove Parseval',      msg: 'Prove the Parseval theorem' },
  { label: ' Generate exam',       msg: 'Generate 5 medium exam questions about Fourier Transform' },
  { label: ' Write MATLAB code',   msg: 'Write MATLAB code for a low-pass filter' },
  { label: ' Draw block diagram',  msg: 'Draw a block diagram of a superheterodyne receiver' },
  { label: ' Explain convolution', msg: 'Explain convolution in detail' },
]

const TOPIC_SECTIONS = [
  {
    label: '📡 Signals & Systems',
    color: 'var(--accent-blue)',
    bg: 'rgba(59,130,246,0.1)',
    border: 'rgba(59,130,246,0.25)',
    topics: [
      'Fourier Transform', 'Laplace Transform', 'Z-Transform',
      'Convolution', 'Sampling & Aliasing', 'AM Modulation',
      'FM Modulation', 'Filter Design', 'Shannon Capacity', 'LTI Systems',
    ]
  },
  {
    label: '🧠 AI & LLMs',
    color: '#a78bfa',
    bg: 'rgba(167,139,250,0.1)',
    border: 'rgba(167,139,250,0.25)',
    topics: [
      'How do LLMs work?',
      'What is RAG?',
      'Explain Transformers',
      'What is attention mechanism?',
      'How is GPT trained?',
    ]
  },
  {
    label: '⚙️ Computer Architecture',
    color: '#fb923c',
    bg: 'rgba(251,146,60,0.1)',
    border: 'rgba(251,146,60,0.25)',
    topics: [
      'Explain CPU pipelining',
      'What is cache memory?',
      'How does RISC differ from CISC?',
      'Explain virtual memory',
      'What is branch prediction?',
    ]
  },
  {
    label: '🔩 Assembly & Low Level',
    color: '#34d399',
    bg: 'rgba(52,211,153,0.1)',
    border: 'rgba(52,211,153,0.25)',
    topics: [
      'What are CPU registers?',
      'Explain stack and heap',
      'How does an interrupt work?',
      'What is memory mapped I/O?',
      'Explain calling conventions',
    ]
  },
]

const PROGRESS_TOPICS = [
  'Fourier Transform', 'Laplace Transform', 'Z-Transform',
  'Convolution', 'Sampling', 'AM Modulation',
  'FM Modulation', 'Filter', 'Shannon', 'LTI',
]

function formatTime(seconds) {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) return `${h}h ${m}m`
  if (m > 0) return `${m}m ${s}s`
  return `${s}s`
}

export default function Sidebar({
  collapsed,
  onToggleCollapse,
  onNewChat,
  todayQuestions = [],
  toolsUsed = new Set(),
  coveredTopics = new Set(),
  sessionSeconds = 0,
  onSelectQuestion,
  onSend,
}) {
  const [activeTab, setActiveTab] = useState('history')
  const w = collapsed ? COLLAPSED_W : EXPANDED_W

  const progressCount = PROGRESS_TOPICS.filter(t =>
    [...coveredTopics].some(c => c.toLowerCase().includes(t.toLowerCase()))
  ).length

  return (
    <aside style={{ ...s.sidebar, width: w, minWidth: w }}>

      {/* ── Header ── */}
      <div style={s.header}>
        <div style={s.logoRow}>
          <div style={s.logoMark}>Σ</div>
          {!collapsed && (
            <div style={s.logoText}>
              <span style={s.logoName}>ΣTutor</span>
              <span style={s.logoTag}>Signals &amp; Systems AI</span>
            </div>
          )}
        </div>
        <button style={s.toggleBtn} onClick={onToggleCollapse}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}>
          {collapsed
            ? <PanelLeftOpen  size={15} color="var(--text-muted)" />
            : <PanelLeftClose size={15} color="var(--text-muted)" />}
        </button>
      </div>

      {/* ── New Chat ── */}
      <div style={{ padding: collapsed ? '10px 0' : '10px 10px', display: 'flex', justifyContent: 'center' }}>
        {collapsed ? (
          <button style={s.newChatIcon} onClick={onNewChat} title="New chat">
            <Plus size={16} color="var(--accent-blue)" />
          </button>
        ) : (
          <button style={s.newChatBtn} onClick={onNewChat}>
            <Plus size={15} strokeWidth={2.5} />
            New Chat
          </button>
        )}
      </div>

      {/* ── Nav ── */}
      <nav style={{ ...s.nav, padding: collapsed ? '0 8px' : '0 8px 4px' }}>
        {NAV.map(({ to, end, icon: Icon, label, color }) => (
          <NavLink
            key={to} to={to} end={end}
            title={collapsed ? label : undefined}
            style={({ isActive }) => ({
              ...s.navItem,
              justifyContent: collapsed ? 'center' : 'flex-start',
              ...(isActive ? s.navItemActive : {}),
            })}
          >
            <Icon size={16} color={color} strokeWidth={2} style={{ flexShrink: 0 }} />
            {!collapsed && <span style={s.navLabel}>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* ── Stats bar ── */}
      {!collapsed && (
        <div style={s.statsBar}>
          <div style={s.statItem}>
            <MessageCircle size={11} color="var(--accent-blue)" />
            <span style={s.statText}>{todayQuestions.length} asked</span>
          </div>
          <div style={s.statDivider} />
          <div style={s.statItem}>
            <Zap size={11} color="var(--accent-green)" />
            <span style={s.statText}>{toolsUsed.size} tools</span>
          </div>
          <div style={s.statDivider} />
          <div style={s.statItem}>
            <Clock size={11} color="var(--accent-purple)" />
            <span style={s.statText}>{formatTime(sessionSeconds)}</span>
          </div>
        </div>
      )}

      {/* ── Progress bar ── */}
      {!collapsed && (
        <div style={s.progressWrap}>
          <div style={s.progressHeader}>
            <span style={s.progressLabel}>Session Progress</span>
            <span style={s.progressCount}>{progressCount}/{PROGRESS_TOPICS.length} topics</span>
          </div>
          <div style={s.progressTrack}>
            <div style={{
              ...s.progressFill,
              width: `${(progressCount / PROGRESS_TOPICS.length) * 100}%`
            }} />
          </div>
        </div>
      )}

      {/* ── Tab switcher ── */}
      {!collapsed && (
        <>
          <div style={s.divider} />
          <div style={s.tabRow}>
            {[
              { key: 'history',  label: 'History'  },
              { key: 'tools',    label: 'Quick'    },
              { key: 'topics',   label: 'Topics'   },
              { key: 'progress', label: 'Progress' },
            ].map(tab => (
              <button
                key={tab.key}
                style={{ ...s.tab, ...(activeTab === tab.key ? s.tabActive : {}) }}
                onClick={() => setActiveTab(tab.key)}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* ── History tab ── */}
          {activeTab === 'history' && (
            <div style={s.sessionList}>
              {todayQuestions.length === 0 ? (
                <div style={s.emptyHistory}>No questions yet — start chatting!</div>
              ) : (
                todayQuestions.map((q, i) => (
                  <button
                    key={i}
                    style={s.sessionItem}
                    onClick={() => onSelectQuestion?.(q)}
                    title={q}
                  >
                    <MessageCircle size={12} style={{ flexShrink: 0, opacity: 0.5 }} />
                    <span style={s.sessionTitle}>{q}</span>
                  </button>
                ))
              )}
            </div>
          )}

          {/* ── Quick Actions tab ── */}
          {activeTab === 'tools' && (
            <div style={s.sessionList}>
              {QUICK_ACTIONS.map((action, i) => (
                <button
                  key={i}
                  style={s.quickBtn}
                  onClick={() => onSend?.(action.msg)}
                >
                  <span style={s.sessionTitle}>{action.label}</span>
                </button>
              ))}
              {toolsUsed.size > 0 && (
                <>
                  <div style={s.sectionLabel}>Used this session</div>
                  {[...toolsUsed].map((tool, i) => (
                    <div key={i} style={s.toolUsedItem}>
                      <Zap size={11} color="var(--accent-green)" />
                      <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{tool}</span>
                    </div>
                  ))}
                </>
              )}
            </div>
          )}

          {/* ── Topics tab ── */}
          {activeTab === 'topics' && (
            <div style={s.sessionList}>

              <div style={s.beyondHeader}>
                <span style={s.beyondTitle}>🚀 Explore Topics</span>
                <span style={s.beyondSub}>ΣTutor knows more than signals!</span>
              </div>

              {TOPIC_SECTIONS.map((section, si) => (
                <div key={si} style={{ marginBottom: 14 }}>
                  <div style={{
                    ...s.sectionChipLabel,
                    color: section.color,
                    borderColor: section.border,
                    background: section.bg,
                  }}>
                    {section.label}
                  </div>
                  <div style={s.topicGrid}>
                    {section.topics.map((topic, i) => {
                      const done = [...coveredTopics].some(c =>
                        c.toLowerCase().includes(topic.toLowerCase())
                      )
                      return (
                        <button
                          key={i}
                          style={{
                            ...s.topicChip,
                            ...(done ? {
                              borderColor: section.border,
                              background: section.bg,
                              color: section.color,
                            } : {})
                          }}
                          onClick={() => onSend?.(
                            topic.includes('?') ||
                            topic.startsWith('What') ||
                            topic.startsWith('How') ||
                            topic.startsWith('Explain')
                              ? topic
                              : `Explain ${topic} in detail`
                          )}
                        >
                          {done && '✓ '}{topic}
                        </button>
                      )
                    })}
                  </div>
                </div>
              ))}

            </div>
          )}

          {/* ── Progress tab ── */}
          {activeTab === 'progress' && (
            <div style={s.sessionList}>
              <div style={s.sectionLabel}>Topics covered today</div>
              {PROGRESS_TOPICS.map((topic, i) => {
                const done = [...coveredTopics].some(c =>
                  c.toLowerCase().includes(topic.toLowerCase())
                )
                return (
                  <div key={i} style={s.progressItem}>
                    {done
                      ? <CheckCircle2 size={14} color="var(--accent-green)" />
                      : <Circle size={14} color="var(--border)" />
                    }
                    <span style={{
                      ...s.progressItemLabel,
                      color: done ? 'var(--text-primary)' : 'var(--text-muted)',
                      fontWeight: done ? 600 : 400,
                    }}>
                      {topic}
                    </span>
                    {done && <span style={s.doneBadge}>✓</span>}
                  </div>
                )
              })}
              {coveredTopics.size === 0 && (
                <div style={s.emptyHistory}>
                  Start asking questions to track your progress!
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* ── Collapsed hint ── */}
      {collapsed && (
        <div style={s.collapsedHistory}>
          <Clock size={15} color="var(--text-muted)" title="Session timer" />
          {todayQuestions.length > 0 && (
            <span style={s.collapsedCount}>{todayQuestions.length}</span>
          )}
        </div>
      )}

    </aside>
  )
}

const s = {
  sidebar: {
    height: '100%',
    background: 'var(--bg-panel)',
    borderRight: '1px solid var(--border)',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    transition: 'width 0.2s ease, min-width 0.2s ease',
    flexShrink: 0,
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '14px 10px 10px',
    borderBottom: '1px solid var(--border)',
    gap: 6,
    minHeight: 56,
  },
  logoRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 9,
    minWidth: 0,
    flex: 1,
  },
  logoMark: {
    width: 32,
    height: 32,
    borderRadius: 9,
    background: 'linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 17,
    fontWeight: 800,
    color: '#fff',
    flexShrink: 0,
    letterSpacing: '-1px',
    boxShadow: '0 2px 8px rgba(59,130,246,0.35)',
  },
  logoText: {
    display: 'flex',
    flexDirection: 'column',
    minWidth: 0,
    overflow: 'hidden',
  },
  logoName: {
    fontSize: 14,
    fontWeight: 700,
    color: 'var(--text-primary)',
    letterSpacing: '-0.4px',
    whiteSpace: 'nowrap',
  },
  logoTag: {
    fontSize: 10,
    color: 'var(--text-muted)',
    whiteSpace: 'nowrap',
    letterSpacing: '0.02em',
  },
  toggleBtn: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: 26,
    height: 26,
    borderRadius: 6,
    flexShrink: 0,
    cursor: 'pointer',
    transition: 'background 0.15s',
    border: 'none',
    background: 'none',
  },
  newChatBtn: {
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    gap: 7,
    padding: '7px 12px',
    borderRadius: 8,
    background: 'rgba(59,130,246,0.12)',
    border: '1px solid rgba(59,130,246,0.25)',
    color: 'var(--accent-blue)',
    fontSize: 13,
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'background 0.15s, border-color 0.15s',
  },
  newChatIcon: {
    width: 36,
    height: 36,
    borderRadius: 8,
    background: 'rgba(59,130,246,0.1)',
    border: '1px solid rgba(59,130,246,0.2)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    transition: 'background 0.15s',
  },
  nav: {
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
  },
  navItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 9,
    padding: '8px 10px',
    borderRadius: 7,
    color: 'var(--text-secondary)',
    fontSize: 13,
    fontWeight: 500,
    textDecoration: 'none',
    transition: 'background 0.15s, color 0.15s',
  },
  navItemActive: {
    background: 'var(--bg-surface)',
    color: 'var(--text-primary)',
  },
  navLabel: {
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
  statsBar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-around',
    padding: '8px 12px',
    background: 'var(--bg-base)',
    borderTop: '1px solid var(--border)',
    borderBottom: '1px solid var(--border)',
  },
  statItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 4,
  },
  statText: {
    fontSize: 10,
    color: 'var(--text-muted)',
    fontWeight: 500,
  },
  statDivider: {
    width: 1,
    height: 12,
    background: 'var(--border)',
  },
  progressWrap: {
    padding: '8px 14px',
    borderBottom: '1px solid var(--border)',
  },
  progressHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  progressLabel: {
    fontSize: 10,
    fontWeight: 700,
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    color: 'var(--text-muted)',
  },
  progressCount: {
    fontSize: 10,
    color: 'var(--accent-green)',
    fontWeight: 600,
  },
  progressTrack: {
    height: 4,
    borderRadius: 2,
    background: 'var(--bg-surface)',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 2,
    background: 'linear-gradient(90deg, var(--accent-blue), var(--accent-green))',
    transition: 'width 0.5s ease',
  },
  divider: {
    height: 1,
    background: 'var(--border)',
    margin: '2px 0',
  },
  tabRow: {
    display: 'flex',
    gap: 3,
    padding: '8px 8px 4px',
  },
  tab: {
    flex: 1,
    padding: '5px 0',
    borderRadius: 6,
    border: '1px solid var(--border)',
    background: 'none',
    color: 'var(--text-muted)',
    fontSize: 10,
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'all 0.15s',
  },
  tabActive: {
    background: 'var(--bg-surface)',
    color: 'var(--text-primary)',
    borderColor: 'var(--accent-blue)',
  },
  sessionList: {
    flex: 1,
    overflowY: 'auto',
    padding: '4px 8px 12px',
  },
  emptyHistory: {
    fontSize: 11,
    color: 'var(--text-muted)',
    padding: '8px',
    fontStyle: 'italic',
  },
  sessionItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 7,
    width: '100%',
    padding: '6px 8px',
    borderRadius: 6,
    background: 'none',
    color: 'var(--text-secondary)',
    fontSize: 12,
    fontWeight: 400,
    cursor: 'pointer',
    textAlign: 'left',
    transition: 'background 0.12s, color 0.12s',
    border: 'none',
  },
  quickBtn: {
    display: 'flex',
    alignItems: 'center',
    width: '100%',
    padding: '7px 10px',
    borderRadius: 7,
    background: 'var(--bg-base)',
    border: '1px solid var(--border)',
    color: 'var(--text-secondary)',
    fontSize: 12,
    fontWeight: 500,
    cursor: 'pointer',
    textAlign: 'left',
    marginBottom: 4,
    transition: 'background 0.12s, border-color 0.12s',
  },
  sessionTitle: {
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    flex: 1,
  },
  sectionLabel: {
    fontSize: 10,
    fontWeight: 700,
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    color: 'var(--text-muted)',
    padding: '8px 4px 4px',
  },
  toolUsedItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '4px 8px',
  },
  beyondHeader: {
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
    padding: '8px 4px 12px',
    borderBottom: '1px solid var(--border)',
    marginBottom: 10,
  },
  beyondTitle: {
    fontSize: 13,
    fontWeight: 700,
    color: 'var(--text-primary)',
  },
  beyondSub: {
    fontSize: 10,
    color: 'var(--text-muted)',
    fontStyle: 'italic',
  },
  sectionChipLabel: {
    display: 'inline-flex',
    alignItems: 'center',
    fontSize: 10,
    fontWeight: 700,
    padding: '3px 10px',
    borderRadius: 20,
    border: '1px solid',
    marginBottom: 6,
    letterSpacing: '0.04em',
  },
  topicGrid: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 6,
    padding: '4px 0',
  },
  topicChip: {
    padding: '4px 10px',
    borderRadius: 20,
    border: '1px solid var(--border)',
    background: 'var(--bg-base)',
    color: 'var(--text-secondary)',
    fontSize: 11,
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'all 0.15s',
  },
  progressItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    padding: '5px 4px',
    borderRadius: 6,
  },
  progressItemLabel: {
    fontSize: 12,
    flex: 1,
    transition: 'color 0.2s',
  },
  doneBadge: {
    fontSize: 10,
    color: 'var(--accent-green)',
    fontWeight: 700,
  },
  collapsedHistory: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    paddingTop: 12,
    gap: 4,
  },
  collapsedCount: {
    fontSize: 9,
    fontWeight: 700,
    color: 'var(--accent-blue)',
    background: 'rgba(59,130,246,0.15)',
    border: '1px solid rgba(59,130,246,0.25)',
    padding: '1px 4px',
    borderRadius: 8,
  },
}