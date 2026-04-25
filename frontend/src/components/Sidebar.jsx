import { NavLink } from 'react-router-dom'
import {
  MessageSquare, Waves, GraduationCap,
  Plus, PanelLeftClose, PanelLeftOpen,
  Clock, MessageCircle,
} from 'lucide-react'

const EXPANDED_W = 260
const COLLAPSED_W = 56

const NAV = [
  { to: '/',         end: true,  icon: MessageSquare, label: 'Chat',               color: 'var(--accent-blue)'   },
  { to: '/sandbox',  end: false, icon: Waves,         label: 'Frequency Sandbox',  color: 'var(--accent-green)'  },
  { to: '/exam',     end: false, icon: GraduationCap, label: 'Exam Mode',          color: 'var(--accent-purple)' },
]

const MOCK_SESSIONS = [
  { id: 1, title: 'Bode Plot Analysis',          group: 'Today'     },
  { id: 2, title: 'Laplace Transform basics',    group: 'Today'     },
  { id: 3, title: 'Nyquist stability criterion', group: 'Yesterday' },
  { id: 4, title: 'Z-Transform exercises',       group: 'Yesterday' },
  { id: 5, title: 'Fourier Series intro',        group: 'Earlier'   },
  { id: 6, title: 'Convolution theorem',         group: 'Earlier'   },
]

const GROUPS = ['Today', 'Yesterday', 'Earlier']

export default function Sidebar({ collapsed, onToggleCollapse, activeSession, onNewChat, onSelectSession }) {
  const w = collapsed ? COLLAPSED_W : EXPANDED_W

  return (
    <aside style={{ ...s.sidebar, width: w, minWidth: w }}>

      {/* ── Header ─────────────────────────────────── */}
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
        <button
          style={s.toggleBtn}
          onClick={onToggleCollapse}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed
            ? <PanelLeftOpen  size={15} color="var(--text-muted)" />
            : <PanelLeftClose size={15} color="var(--text-muted)" />}
        </button>
      </div>

      {/* ── New Chat ───────────────────────────────── */}
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

      {/* ── Nav ────────────────────────────────────── */}
      <nav style={{ ...s.nav, padding: collapsed ? '0 8px' : '0 8px 4px' }}>
        {NAV.map(({ to, end, icon: Icon, label, color }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
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

      {/* ── Conversation history ────────────────────── */}
      {!collapsed && (
        <>
          <div style={s.divider} />
          <div style={s.historyHeader}>
            <Clock size={11} color="var(--text-muted)" />
            <span style={s.historyLabel}>History</span>
          </div>
          <div style={s.sessionList}>
            {GROUPS.map(group => {
              const items = MOCK_SESSIONS.filter(s => s.group === group)
              if (!items.length) return null
              return (
                <div key={group}>
                  <div style={s.groupLabel}>{group}</div>
                  {items.map(session => (
                    <button
                      key={session.id}
                      style={{
                        ...s.sessionItem,
                        ...(activeSession === session.id ? s.sessionItemActive : {}),
                      }}
                      onClick={() => onSelectSession?.(session.id)}
                    >
                      <MessageCircle size={12} style={{ flexShrink: 0, opacity: 0.5 }} />
                      <span style={s.sessionTitle}>{session.title}</span>
                    </button>
                  ))}
                </div>
              )
            })}
          </div>
        </>
      )}

      {/* ── Collapsed history hint ──────────────────── */}
      {collapsed && (
        <div style={s.collapsedHistory}>
          <Clock size={15} color="var(--text-muted)" title="Conversation history" />
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

  /* header */
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
  },

  /* new chat */
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

  /* nav */
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

  /* history */
  divider: {
    height: 1,
    background: 'var(--border)',
    margin: '2px 0',
  },
  historyHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: 5,
    padding: '8px 14px 4px',
  },
  historyLabel: {
    fontSize: 10,
    fontWeight: 700,
    textTransform: 'uppercase',
    letterSpacing: '0.1em',
    color: 'var(--text-muted)',
  },
  sessionList: {
    flex: 1,
    overflowY: 'auto',
    padding: '0 8px 12px',
  },
  groupLabel: {
    fontSize: 10,
    fontWeight: 600,
    color: 'var(--text-muted)',
    padding: '6px 8px 3px',
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
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
    fontSize: 12.5,
    fontWeight: 400,
    cursor: 'pointer',
    textAlign: 'left',
    transition: 'background 0.12s, color 0.12s',
    border: 'none',
  },
  sessionItemActive: {
    background: 'var(--bg-surface)',
    color: 'var(--text-primary)',
  },
  sessionTitle: {
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    flex: 1,
  },

  /* collapsed history hint */
  collapsedHistory: {
    flex: 1,
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'center',
    paddingTop: 12,
  },
}
