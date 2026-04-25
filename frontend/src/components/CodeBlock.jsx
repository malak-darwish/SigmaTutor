import { useState } from 'react'
import { Check, Copy, ChevronDown, ChevronUp } from 'lucide-react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

// ─── Mock data ────────────────────────────────────────────────────────────────

const DEMO_CODE = `import numpy as np
import matplotlib.pyplot as plt

def fourier_transform_demo(f1=3, f2=8, fs=500, duration=1.0):
    """
    Demonstrates the Fourier Transform on a composite signal.
    x(t) = sin(2π·f1·t) + 0.45·sin(2π·f2·t)
    """
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    x = np.sin(2 * np.pi * f1 * t) + 0.45 * np.sin(2 * np.pi * f2 * t)

    # Compute FFT
    N   = len(t)
    X   = np.fft.rfft(x)            # one-sided spectrum
    f   = np.fft.rfftfreq(N, 1/fs)  # frequency axis in Hz
    mag = (2 / N) * np.abs(X)       # normalised magnitude

    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

    ax1.plot(t, x, color='#3b82f6', linewidth=0.8)
    ax1.set(title='Time Domain  x(t)', xlabel='Time (s)', ylabel='Amplitude')
    ax1.grid(alpha=0.3)

    ax2.stem(f, mag, linefmt='#8b5cf6', markerfmt='o', basefmt='gray')
    ax2.set(title='Frequency Domain  |X(f)|', xlabel='Frequency (Hz)',
            ylabel='Magnitude', xlim=[0, 20])
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('fourier_demo.svg', dpi=150, bbox_inches='tight')
    plt.show()
    return t, x, f, mag

if __name__ == '__main__':
    t, x, f, mag = fourier_transform_demo()
    peak_freqs = f[np.argsort(mag)[-3:][::-1]]
    print(f'Top 3 frequency components: {peak_freqs} Hz')
`

const DEMO_MATLAB = `% Fourier Transform Demo in MATLAB
fs = 500;           % Sampling frequency (Hz)
T  = 1;             % Duration (s)
t  = 0 : 1/fs : T - 1/fs;

% Composite signal: x(t) = sin(2π·3t) + 0.45·sin(2π·8t)
x = sin(2*pi*3*t) + 0.45*sin(2*pi*8*t);

% Single-sided FFT
N   = length(t);
X   = fft(x);
f   = (0 : N/2) * fs / N;
mag = (2/N) * abs(X(1 : N/2+1));
mag(1) = mag(1)/2;  % DC component correction

% Plot
figure;
subplot(2,1,1);
plot(t, x, 'Color', [0.23 0.51 0.96], 'LineWidth', 0.8);
title('Time Domain x(t)'); xlabel('Time (s)'); ylabel('Amplitude');
grid on;

subplot(2,1,2);
stem(f, mag, 'Color', [0.55 0.36 0.96], 'MarkerSize', 4, 'LineWidth', 1.2);
title('Frequency Domain |X(f)|'); xlabel('Frequency (Hz)'); ylabel('Magnitude');
xlim([0 20]); grid on;
`

// ─── Language config ──────────────────────────────────────────────────────────

const LANGUAGES = {
  python: { label: 'Python',  prism: 'python' },
  matlab: { label: 'MATLAB',  prism: 'matlab' },
  javascript: { label: 'JS', prism: 'javascript' },
  bash:   { label: 'Shell',   prism: 'bash'   },
}

const HIGHLIGHTER_STYLE = {
  ...oneDark,
  'pre[class*="language-"]': {
    ...oneDark['pre[class*="language-"]'],
    margin: 0,
    padding: '14px 16px',
    background: '#0d0f1a',
    fontSize: 13,
    lineHeight: 1.65,
    fontFamily: 'var(--font-mono)',
    borderRadius: 0,
  },
  'code[class*="language-"]': {
    ...oneDark['code[class*="language-"]'],
    fontFamily: 'var(--font-mono)',
  },
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function CodeBlock({
  code,
  language = 'python',
  filename,
  showLineNumbers: initialLineNums = true,
  collapsible = false,
}) {
  const [copied, setCopied]         = useState(false)
  const [showLineNums, setLineNums] = useState(initialLineNums)
  const [collapsed, setCollapsed]   = useState(false)

  const resolvedCode = code ?? (language === 'matlab' ? DEMO_MATLAB : DEMO_CODE)
  const langCfg = LANGUAGES[language] ?? { label: language, prism: language }

  function handleCopy() {
    navigator.clipboard.writeText(resolvedCode).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  const lineCount = resolvedCode.split('\n').length

  return (
    <div style={s.root}>

      {/* ── Header ─── */}
      <div style={s.header}>
        <div style={s.headerLeft}>
          <span style={s.langBadge}>{langCfg.label}</span>
          {filename && <span style={s.filename}>{filename}</span>}
          <span style={s.lineCount}>{lineCount} lines</span>
        </div>

        <div style={s.headerRight}>
          {/* Line numbers toggle */}
          <button
            style={{ ...s.headerBtn, color: showLineNums ? 'var(--accent-blue)' : 'var(--text-muted)' }}
            onClick={() => setLineNums(v => !v)}
            title="Toggle line numbers"
          >
            <span style={{ fontSize: 11, fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
              #
            </span>
          </button>

          {/* Copy */}
          <button
            style={{ ...s.headerBtn, color: copied ? 'var(--accent-green)' : 'var(--text-muted)' }}
            onClick={handleCopy}
            title={copied ? 'Copied!' : 'Copy code'}
          >
            {copied ? <Check size={13} /> : <Copy size={13} />}
            <span style={s.btnLabel}>{copied ? 'Copied!' : 'Copy'}</span>
          </button>

          {/* Collapse */}
          {collapsible && (
            <button
              style={s.headerBtn}
              onClick={() => setCollapsed(v => !v)}
              title={collapsed ? 'Expand' : 'Collapse'}
            >
              {collapsed ? <ChevronDown size={13} /> : <ChevronUp size={13} />}
            </button>
          )}
        </div>
      </div>

      {/* ── Code body ─── */}
      {!collapsed && (
        <div style={s.body}>
          <SyntaxHighlighter
            language={langCfg.prism}
            style={HIGHLIGHTER_STYLE}
            showLineNumbers={showLineNums}
            lineNumberStyle={s.lineNumber}
            wrapLongLines={false}
            customStyle={{ margin: 0, borderRadius: 0 }}
          >
            {resolvedCode}
          </SyntaxHighlighter>
        </div>
      )}

      {collapsed && (
        <div style={s.collapsedBar} onClick={() => setCollapsed(false)}>
          <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>
            {lineCount} lines hidden — click to expand
          </span>
        </div>
      )}

    </div>
  )
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const s = {
  root: {
    background: '#0d0f1a',
    border: '1px solid var(--border)',
    borderRadius: 10,
    overflow: 'hidden',
    fontSize: 13,
    width: '100%',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '7px 12px',
    background: 'var(--bg-panel)',
    borderBottom: '1px solid var(--border)',
    gap: 8,
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  },
  langBadge: {
    fontSize: 11,
    fontWeight: 700,
    color: 'var(--accent-blue)',
    background: 'rgba(59,130,246,0.1)',
    border: '1px solid rgba(59,130,246,0.25)',
    padding: '2px 8px',
    borderRadius: 4,
    fontFamily: 'var(--font-mono)',
    letterSpacing: '0.02em',
  },
  filename: {
    fontSize: 12,
    fontFamily: 'var(--font-mono)',
    color: 'var(--text-secondary)',
  },
  lineCount: {
    fontSize: 11,
    color: 'var(--text-muted)',
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: 2,
  },
  headerBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: 4,
    padding: '3px 8px',
    borderRadius: 5,
    border: 'none',
    background: 'none',
    cursor: 'pointer',
    transition: 'background 0.12s, color 0.12s',
    color: 'var(--text-muted)',
  },
  btnLabel: {
    fontSize: 11,
    fontWeight: 500,
  },
  body: {
    overflow: 'auto',
    maxHeight: 480,
  },
  lineNumber: {
    color: '#3a3f5c',
    minWidth: '2.5em',
    paddingRight: '1em',
    userSelect: 'none',
  },
  collapsedBar: {
    padding: '8px 16px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderTop: '1px solid var(--border)',
    background: 'var(--bg-panel)',
  },
}
