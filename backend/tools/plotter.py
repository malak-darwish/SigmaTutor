import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import base64
import io
import json
from scipy import signal
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()
matplotlib.use('Agg')

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
    api_key=os.getenv("GROQ_API_KEY")
)

def _parse_signals(description: str) -> dict:
    """Extract signal parameters from natural language"""
    prompt = f"""Extract signal parameters from: "{description}"
Respond ONLY with JSON, no explanation, no markdown.
Format: {{"operation":"plot","freq_min":null,"freq_max":null,"signals":[{{"signal_type":"sine","frequency":10.0,"amplitude":1.0,"t_start":-1.0,"t_end":1.0,"sample_rate":1000.0,"phase_deg":0.0}}]}}
Operations: plot, multiply, convolve, add
Signal types: sine, cosine, square, sawtooth, triangle, rect, impulse, step, comb"""

    response = llm.invoke([HumanMessage(content=prompt)])
    text = response.content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return json.loads(text.strip())

def _generate_signal(params: dict, t: np.ndarray) -> np.ndarray:
    """Generate a single signal array from parameters"""
    sig_type = params["signal_type"]
    freq = params.get("frequency", 1.0)
    amp = params.get("amplitude", 1.0)
    phase_rad = np.deg2rad(params.get("phase_deg", 0.0))
    sample_rate = params.get("sample_rate", 1000.0)

    if sig_type == "sine":
        return amp * np.sin(2 * np.pi * freq * t + phase_rad)
    elif sig_type == "cosine":
        return amp * np.cos(2 * np.pi * freq * t + phase_rad)
    elif sig_type == "square":
        return amp * signal.square(2 * np.pi * freq * t + phase_rad)
    elif sig_type == "sawtooth":
        return amp * signal.sawtooth(2 * np.pi * freq * t + phase_rad)
    elif sig_type == "triangle":
        return amp * signal.sawtooth(2 * np.pi * freq * t + phase_rad, width=0.5)
    elif sig_type == "rect":
        period = 1.0 / freq
        return amp * ((t % period) < (period / 2)).astype(float)
    elif sig_type == "impulse":
        x = np.zeros_like(t)
        idx = np.argmin(np.abs(t))
        x[idx] = amp
        return x
    elif sig_type == "step":
        return amp * np.heaviside(t, 1.0)
    elif sig_type == "comb":
        x = np.zeros_like(t)
        period_samples = int(sample_rate / freq)
        if period_samples > 0:
            x[::period_samples] = amp
        return x
    else:
        return amp * np.sin(2 * np.pi * freq * t + phase_rad)

def _plot_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_bytes = buf.read()
    buf.close()
    plt.close(fig)
    # If image is too large (e.g. > 1MB), return a warning string
    if len(img_bytes) > 1_000_000:
        return "Plot image too large. Please reduce the time range or sample rate and try again."
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    return img_base64

def _style_ax(ax):
    """Apply dark theme styling to an axis"""
    ax.set_facecolor('#070b14')
    ax.tick_params(colors='#94a3b8')
    ax.xaxis.label.set_color('#94a3b8')
    ax.yaxis.label.set_color('#94a3b8')
    ax.title.set_color('#00d4ff')
    for spine in ax.spines.values():
        spine.set_edgecolor('#1a2a45')
    ax.grid(True, color='#1a2a45')

def _make_label(params: dict) -> str:
    """Build a plot label from signal params safely"""
    sig_type = params["signal_type"]
    freq_str = f" {params['frequency']}Hz" if params.get("frequency") else ""
    phase_str = f" φ={params['phase_deg']}°" if params.get("phase_deg", 0) != 0 else ""
    return f"{sig_type}{freq_str}{phase_str}"

def _compute_fft(x: np.ndarray, t: np.ndarray, sample_rate: float):
    """Compute two-sided FFT centered at 0"""
    N = len(t)
    fft_vals = np.abs(np.fft.fftshift(np.fft.fft(x))) / N
    fft_freqs = np.fft.fftshift(np.fft.fftfreq(N, 1 / sample_rate))
    return fft_freqs, fft_vals

def _apply_freq_range(ax, fft_freqs, freq_min, freq_max, sample_rate):
    """Apply frequency axis range — symmetric by default"""
    f_min = freq_min if freq_min is not None else -sample_rate / 2
    f_max = freq_max if freq_max is not None else sample_rate / 2
    ax.set_xlim(f_min, f_max)

def _generate_plot(parsed: dict) -> str:
    """Plot signals based on operation"""
    operation = parsed.get("operation", "plot")
    signals_params = parsed["signals"]
    freq_min = parsed.get("freq_min", None)
    freq_max = parsed.get("freq_max", None)

    t_start = signals_params[0].get("t_start", -1.0)
    t_end = signals_params[0].get("t_end", 1.0)
    sample_rate = signals_params[0].get("sample_rate", 1000.0)
    t = np.linspace(t_start, t_end, int(sample_rate * (t_end - t_start)))

    colors_time = ['#00d4ff', '#10b981', '#f59e0b', '#ec4899']
    colors_freq = ['#7c3aed', '#ef4444', '#f97316', '#6366f1']

    if operation == "plot":
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
        fig.patch.set_facecolor('#0d1525')
        _style_ax(ax1)
        _style_ax(ax2)

        for i, params in enumerate(signals_params):
            x = _generate_signal(params, t)
            label = _make_label(params)

            ax1.plot(t, x, color=colors_time[i % len(colors_time)],
                     linewidth=1.5, label=label)

            fft_freqs, fft_vals = _compute_fft(x, t, sample_rate)
            ax2.plot(fft_freqs, fft_vals, color=colors_freq[i % len(colors_freq)],
                     linewidth=1.5, label=label)

        if len(signals_params) > 1:
            ax1.legend(facecolor='#0d1525', edgecolor='#1a2a45', labelcolor='#94a3b8')
            ax2.legend(facecolor='#0d1525', edgecolor='#1a2a45', labelcolor='#94a3b8')

        ax1.set_title('Time Domain')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Amplitude')

        ax2.set_title('Frequency Domain (FFT)')
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Magnitude')
        _apply_freq_range(ax2, fft_freqs, freq_min, freq_max, sample_rate)

    elif operation in ["multiply", "add", "convolve"]:
        x1 = _generate_signal(signals_params[0], t)
        x2 = _generate_signal(signals_params[1], t)
        label1 = _make_label(signals_params[0])
        label2 = _make_label(signals_params[1])

        if operation == "multiply":
            result = x1 * x2
            result_label = f"{label1} × {label2}"
        elif operation == "add":
            result = x1 + x2
            result_label = f"{label1} + {label2}"
        elif operation == "convolve":
            conv_full = np.convolve(x1, x2) / sample_rate
            result = conv_full[:len(t)]
            result_label = f"{label1} ∗ {label2}"

        fig, axes = plt.subplots(3, 2, figsize=(12, 9))
        fig.patch.set_facecolor('#0d1525')

        pairs = [(x1, label1), (x2, label2), (result, result_label)]
        row_colors_t = ['#00d4ff', '#10b981', '#f59e0b']
        row_colors_f = ['#7c3aed', '#ef4444', '#f97316']

        for i, (x, label) in enumerate(pairs):
            ax_t = axes[i][0]
            ax_f = axes[i][1]
            _style_ax(ax_t)
            _style_ax(ax_f)

            ax_t.plot(t, x, color=row_colors_t[i], linewidth=1.5)
            ax_t.set_title(f'Time Domain — {label}')
            ax_t.set_xlabel('Time (s)')
            ax_t.set_ylabel('Amplitude')

            fft_freqs, fft_vals = _compute_fft(x, t, sample_rate)
            ax_f.plot(fft_freqs, fft_vals, color=row_colors_f[i], linewidth=1.5)
            ax_f.set_title(f'Frequency Domain — {label}')
            ax_f.set_xlabel('Frequency (Hz)')
            ax_f.set_ylabel('Magnitude')
            _apply_freq_range(ax_f, fft_freqs, freq_min, freq_max, sample_rate)

    plt.tight_layout()
    return _plot_to_base64(fig)


def plot_signal(description: str) -> str:
    """
    Plots signals from a natural language description. Supports sine, cosine, square,
    sawtooth, triangle, rect, impulse, step, and comb signals.
    Supports phase shifts, custom time and frequency ranges, plotting multiple signals,
    and operations like multiply, add, and convolve between two signals.
    The frequency domain is two-sided by default (negative to positive frequencies).
    Args:
        description (str): Natural language description, e.g.
                          'plot a 10Hz sine wave',
                          'plot a sine from -2 to 2 seconds',
                          'plot a 10Hz sine, show frequencies up to 50Hz',
                          'plot sine and cosine at 5Hz together',
                          'multiply a rect pulse with a sine wave',
                          'convolve a rect pulse with an impulse',
                          'add a 5Hz sine and a 10Hz sine'
    Returns:
        str: Base64 encoded PNG image of the plot
    """
    parsed = _parse_signals(description)
    return _generate_plot(parsed)