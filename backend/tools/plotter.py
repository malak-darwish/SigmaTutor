import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import base64
import io
import json
from scipy import signal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()
matplotlib.use('Agg')

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    api_key=os.environ.get("GOOGLE_API_KEY"),
    temperature=0.0
)

def _parse_signals(description: str) -> dict:
    """Use Gemini to extract signal parameters and operation from natural language"""
    prompt = f"""
You are a signals and systems expert. Extract signal parameters from this description:
"{description}"

Respond ONLY with a JSON object, no explanation, no markdown, just raw JSON.

Format:
{{
    "operation": "plot",
    "freq_min": null,
    "freq_max": null,
    "signals": [
        {{
            "signal_type": "sine",
            "frequency": 10.0,
            "amplitude": 1.0,
            "t_start": -1.0,
            "t_end": 1.0,
            "sample_rate": 1000.0,
            "phase_deg": 0.0
        }}
    ]
}}

operation options:
- "plot"         : plot the signals individually or together
- "multiply"     : multiply the signals together (signal1 * signal2)
- "convolve"     : convolve the signals together
- "add"          : add the signals together

signal_type options:
- sine           : A * sin(2*pi*f*t + phase)
- cosine         : A * cos(2*pi*f*t + phase)
- square         : square wave at frequency f
- sawtooth       : sawtooth wave at frequency f
- triangle       : triangle wave at frequency f
- rect           : rectangular pulse
- impulse        : delta function spike at t=0
- step           : unit step u(t)
- comb           : impulse train at interval 1/f

Rules:
- t_start: start of time axis (default -1.0)
- t_end: end of time axis (default 1.0)
- freq_min: start of frequency axis in Hz (default null = auto -sample_rate/2)
- freq_max: end of frequency axis in Hz (default null = auto sample_rate/2)
- If user specifies a time range like "from -2 to 2" use those values
- If user specifies a frequency range like "show frequencies up to 50Hz" set freq_max=50
- If user specifies "show frequencies from -20 to 20" set freq_min=-20, freq_max=20
- phase_deg is phase shift in degrees (default 0)
- sample_rate default 1000.0 Hz
- frequency is not needed for impulse and step signals, omit it
- For multiply/convolve/add always return exactly 2 signals
- For plot return as many signals as described

Examples:
- "plot a 10Hz sine wave" ->
{{"operation": "plot", "freq_min": null, "freq_max": null, "signals": [{{"signal_type": "sine", "frequency": 10.0, "amplitude": 1.0, "t_start": -1.0, "t_end": 1.0, "sample_rate": 1000.0, "phase_deg": 0.0}}]}}

- "plot a step signal from -1 to 1" ->
{{"operation": "plot", "freq_min": null, "freq_max": null, "signals": [{{"signal_type": "step", "amplitude": 1.0, "t_start": -1.0, "t_end": 1.0, "sample_rate": 1000.0, "phase_deg": 0.0}}]}}

- "plot a 10Hz sine from -2 to 2, show frequencies up to 50Hz" ->
{{"operation": "plot", "freq_min": null, "freq_max": 50.0, "signals": [{{"signal_type": "sine", "frequency": 10.0, "amplitude": 1.0, "t_start": -2.0, "t_end": 2.0, "sample_rate": 1000.0, "phase_deg": 0.0}}]}}

- "plot sine and cosine at 5Hz from -2 to 2" ->
{{"operation": "plot", "freq_min": null, "freq_max": null, "signals": [
    {{"signal_type": "sine", "frequency": 5.0, "amplitude": 1.0, "t_start": -2.0, "t_end": 2.0, "sample_rate": 1000.0, "phase_deg": 0.0}},
    {{"signal_type": "cosine", "frequency": 5.0, "amplitude": 1.0, "t_start": -2.0, "t_end": 2.0, "sample_rate": 1000.0, "phase_deg": 0.0}}
]}}

- "multiply a rect pulse with a 10Hz sine wave" ->
{{"operation": "multiply", "freq_min": null, "freq_max": null, "signals": [
    {{"signal_type": "rect", "frequency": 2.0, "amplitude": 1.0, "t_start": -1.0, "t_end": 1.0, "sample_rate": 1000.0, "phase_deg": 0.0}},
    {{"signal_type": "sine", "frequency": 10.0, "amplitude": 1.0, "t_start": -1.0, "t_end": 1.0, "sample_rate": 1000.0, "phase_deg": 0.0}}
]}}
"""
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
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
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