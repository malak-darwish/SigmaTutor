import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import base64
import io
from scipy import signal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import json

load_dotenv()
matplotlib.use('Agg')

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=os.environ.get("GOOGLE_API_KEY"),
    temperature=0.0
)

# ── Sandbox State ─────────────────────────────────────────────────────────────
class SignalState:
    """Holds the current signal between student iterations"""
    def __init__(self):
        self.x = None
        self.t = None
        self.sample_rate = 1000.0
        self.history = []
        self.last_filter_b = None
        self.last_filter_a = None
        self.last_noise_std = None

    def reset(self):
        self.__init__()

_state = SignalState()

# ── Helpers ───────────────────────────────────────────────────────────────────
def _plot_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img

def _style_ax(ax):
    ax.set_facecolor('#070b14')
    ax.tick_params(colors='#94a3b8')
    ax.xaxis.label.set_color('#94a3b8')
    ax.yaxis.label.set_color('#94a3b8')
    ax.title.set_color('#00d4ff')
    for spine in ax.spines.values():
        spine.set_edgecolor('#1a2a45')
    ax.grid(True, color='#1a2a45')

def _compute_snr(clean: np.ndarray, noisy: np.ndarray) -> float:
    noise = noisy - clean
    signal_power = np.mean(clean ** 2)
    noise_power = np.mean(noise ** 2)
    if noise_power == 0:
        return float('inf')
    return 10 * np.log10(signal_power / noise_power)

def _plot_current_state(title: str, snr: float = None) -> str:
    t = _state.t
    x = _state.x
    sample_rate = _state.sample_rate

    N = len(t)
    fft_vals = np.abs(np.fft.fftshift(np.fft.fft(x))) / N
    fft_freqs = np.fft.fftshift(np.fft.fftfreq(N, 1 / sample_rate))

    snr_str = f" | SNR: {snr:.2f} dB" if snr is not None else ""

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
    fig.patch.set_facecolor('#0d1525')
    _style_ax(ax1)
    _style_ax(ax2)

    ax1.plot(t, x, color='#00d4ff', linewidth=1.5)
    ax1.set_title(f'Time Domain — {title}{snr_str}')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Amplitude')

    ax2.plot(fft_freqs, fft_vals, color='#7c3aed', linewidth=1.5)
    ax2.set_title('Frequency Domain (FFT)')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Magnitude')
    ax2.set_xlim(-sample_rate / 2, sample_rate / 2)

    plt.tight_layout()
    return _plot_to_base64(fig)

def _plot_bode(b, a, sample_rate: float, title: str) -> str:
    w, h = signal.freqz(b, a, worN=8000, fs=sample_rate)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
    fig.patch.set_facecolor('#0d1525')
    _style_ax(ax1)
    _style_ax(ax2)

    ax1.plot(w, 20 * np.log10(np.abs(h) + 1e-10), color='#00d4ff', linewidth=1.5)
    ax1.set_title(f'Bode Plot — {title}')
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('Magnitude (dB)')

    ax2.plot(w, np.angle(h, deg=True), color='#7c3aed', linewidth=1.5)
    ax2.set_title('Phase Response')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Phase (degrees)')

    plt.tight_layout()
    return _plot_to_base64(fig)

def _generate_code(language: str) -> str:
    """Use Gemini to generate code for the current signal history"""
    if not _state.history:
        return "No operations performed yet."

    history_str = " → ".join(_state.history)
    duration = _state.t[-1] if _state.t is not None else 1.0
    sample_rate = _state.sample_rate

    if language == "matlab":
        prompt = f"""
You are a signals and systems MATLAB expert.
Generate clean, well-commented MATLAB code that reproduces this signal processing chain:
{history_str}

Parameters:
- Sample rate: {sample_rate} Hz
- Duration: {duration} seconds

Rules:
- Structure code into sections: %% Parameters, %% Signal Generation, %% Processing, %% Plotting
- Every figure must have title, xlabel, ylabel, grid on
- Use Signal Processing Toolbox functions where appropriate
- Only return the MATLAB code, no explanation outside of comments
"""
    else:
        prompt = f"""
You are a signals and systems Python expert.
Generate clean, well-commented Python code using NumPy and SciPy that reproduces this signal processing chain:
{history_str}

Parameters:
- Sample rate: {sample_rate} Hz
- Duration: {duration} seconds

Rules:
- Use numpy, scipy.signal, and matplotlib
- Structure with clear comments for each step
- Include a plot at the end with title, xlabel, ylabel, grid
- Only return the Python code, no explanation outside of comments
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    code = response.content.strip()

    if code.startswith("```matlab") or code.startswith("```python"):
        code = code.split("\n", 1)[1]
    elif code.startswith("```"):
        code = code.split("\n", 1)[1]
    if code.endswith("```"):
        code = code.rsplit("```", 1)[0]

    return code.strip()

def _parse_operations(instruction: str) -> list:
    """Use Gemini to parse instruction into a LIST of operations"""
    history_str = ", ".join(_state.history) if _state.history else "none yet"

    prompt = f"""
You are a signals and systems expert. Parse this student instruction into a JSON array of operations.
The student may request one or multiple operations in a single message.

Student instruction: "{instruction}"
Current signal history: {history_str}

Respond ONLY with a JSON array, no explanation, no markdown, just raw JSON.
Operations must be in the correct order (e.g. create before modulate).

Possible operations:

1. Create a basic signal:
{{"op": "create", "signal_type": "sine", "frequency": 10.0, "amplitude": 1.0, "duration": 1.0, "sample_rate": 1000.0}}
signal_type options: sine, cosine, square, sawtooth, triangle, chirp

2. Add noise:
{{"op": "add_noise", "noise_type": "gaussian", "std": 0.1}}
noise_type options: gaussian, uniform

3. Apply a Butterworth filter:
{{"op": "filter", "filter_type": "lowpass", "cutoff": 20.0, "order": 5}}
filter_type options: lowpass, highpass, bandpass

4. AM modulation:
{{"op": "am_modulate", "carrier_freq": 100.0, "modulation_index": 1.0}}

5. FM modulation:
{{"op": "fm_modulate", "carrier_freq": 100.0, "freq_deviation": 10.0}}

6. AM demodulation:
{{"op": "am_demodulate"}}

7. FM demodulation:
{{"op": "fm_demodulate", "carrier_freq": 100.0}}

8. Scale amplitude:
{{"op": "scale", "factor": 2.0}}

9. Combine two signals:
{{"op": "combine", "signal_type": "sine", "frequency": 20.0, "amplitude": 1.0, "combine_mode": "add"}}
combine_mode options: add, multiply

10. Convolve with a signal:
{{"op": "convolve", "signal_type": "rect", "frequency": 2.0, "amplitude": 1.0}}

11. Show Bode plot of current filter:
{{"op": "bode"}}

12. Get MATLAB code for current signal chain:
{{"op": "get_code", "language": "matlab"}}

13. Get Python code for current signal chain:
{{"op": "get_code", "language": "python"}}

14. Reset sandbox:
{{"op": "reset"}}

Examples:
- "give me a 10Hz sine wave and AM modulate it" ->
  [{{"op": "create", "signal_type": "sine", "frequency": 10.0, "amplitude": 1.0, "duration": 1.0, "sample_rate": 1000.0}},
   {{"op": "am_modulate", "carrier_freq": 100.0, "modulation_index": 1.0}}]

- "create a square wave, add noise, then lowpass filter it" ->
  [{{"op": "create", "signal_type": "square", "frequency": 10.0, "amplitude": 1.0, "duration": 1.0, "sample_rate": 1000.0}},
   {{"op": "add_noise", "noise_type": "gaussian", "std": 0.1}},
   {{"op": "filter", "filter_type": "lowpass", "cutoff": 20.0, "order": 5}}]

- "give me the MATLAB code for this" ->
  [{{"op": "get_code", "language": "matlab"}}]

- "show me the Python code" ->
  [{{"op": "get_code", "language": "python"}}]

- "add a 20Hz cosine to the current signal" ->
  [{{"op": "combine", "signal_type": "cosine", "frequency": 20.0, "amplitude": 1.0, "combine_mode": "add"}}]

- "convolve with a rect pulse" ->
  [{{"op": "convolve", "signal_type": "rect", "frequency": 2.0, "amplitude": 1.0}}]

- "show bode plot" ->
  [{{"op": "bode"}}]

- "now add gaussian noise" ->
  [{{"op": "add_noise", "noise_type": "gaussian", "std": 0.1}}]
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    text = response.content.strip()

    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

    return json.loads(text.strip())

def _apply_operation(op_dict: dict):
    """Apply a single operation to the current signal state"""
    op = op_dict["op"]

    if op == "reset":
        _state.reset()
        return "Sandbox reset. Start with a new signal."

    elif op == "create":
        fs = op_dict.get("sample_rate", 1000.0)
        duration = op_dict.get("duration", 1.0)
        freq = op_dict.get("frequency", 10.0)
        amp = op_dict.get("amplitude", 1.0)
        sig_type = op_dict.get("signal_type", "sine")

        _state.sample_rate = fs
        _state.t = np.linspace(0, duration, int(fs * duration))
        t = _state.t

        if sig_type == "sine":
            _state.x = amp * np.sin(2 * np.pi * freq * t)
        elif sig_type == "cosine":
            _state.x = amp * np.cos(2 * np.pi * freq * t)
        elif sig_type == "square":
            _state.x = amp * signal.square(2 * np.pi * freq * t)
        elif sig_type == "sawtooth":
            _state.x = amp * signal.sawtooth(2 * np.pi * freq * t)
        elif sig_type == "triangle":
            _state.x = amp * signal.sawtooth(2 * np.pi * freq * t, width=0.5)
        elif sig_type == "chirp":
            _state.x = amp * signal.chirp(t, f0=freq, f1=freq * 5, t1=duration)

        _state.history.append(f"created {sig_type} {freq}Hz")
        return None

    elif op == "add_noise":
        if _state.x is None:
            return "No signal yet. Create a signal first."
        noise_type = op_dict.get("noise_type", "gaussian")
        std = op_dict.get("std", 0.1)

        clean = _state.x.copy()
        if noise_type == "gaussian":
            noise = np.random.normal(0, std, len(_state.x))
        else:
            noise = np.random.uniform(-std, std, len(_state.x))

        _state.x = _state.x + noise
        snr = _compute_snr(clean, _state.x)
        _state.last_noise_std = std
        _state.history.append(f"added {noise_type} noise (SNR={snr:.1f}dB)")
        return None

    elif op == "filter":
        if _state.x is None:
            return "No signal yet. Create a signal first."
        filter_type = op_dict.get("filter_type", "lowpass")
        cutoff = op_dict.get("cutoff", 20.0)
        order = op_dict.get("order", 5)
        nyq = _state.sample_rate / 2

        if filter_type == "bandpass":
            cutoff_list = op_dict.get("cutoff", [10.0, 30.0])
            norm = [c / nyq for c in cutoff_list]
        else:
            norm = cutoff / nyq

        b, a = signal.butter(order, norm, btype=filter_type)
        _state.last_filter_b = b
        _state.last_filter_a = a
        _state.x = signal.filtfilt(b, a, _state.x)
        _state.history.append(f"applied {filter_type} filter at {cutoff}Hz")
        return None

    elif op == "am_modulate":
        if _state.x is None:
            return "No signal yet. Create a signal first."
        fc = op_dict.get("carrier_freq", 100.0)
        mi = op_dict.get("modulation_index", 1.0)
        carrier = np.cos(2 * np.pi * fc * _state.t)
        _state.x = (1 + mi * _state.x) * carrier
        _state.history.append(f"AM modulated with {fc}Hz carrier")
        return None

    elif op == "am_demodulate":
        if _state.x is None:
            return "No signal yet. Create a signal first."
        analytic = signal.hilbert(_state.x)
        envelope = np.abs(analytic)
        envelope = envelope - np.mean(envelope)
        _state.x = envelope
        _state.history.append("AM demodulated")
        return None

    elif op == "fm_modulate":
        if _state.x is None:
            return "No signal yet. Create a signal first."
        fc = op_dict.get("carrier_freq", 100.0)
        fd = op_dict.get("freq_deviation", 10.0)
        integral = np.cumsum(_state.x) / _state.sample_rate
        _state.x = np.cos(2 * np.pi * fc * _state.t + 2 * np.pi * fd * integral)
        _state.history.append(f"FM modulated with {fc}Hz carrier")
        return None

    elif op == "fm_demodulate":
        if _state.x is None:
            return "No signal yet. Create a signal first."
        analytic = signal.hilbert(_state.x)
        phase = np.unwrap(np.angle(analytic))
        demodulated = np.diff(phase) * _state.sample_rate / (2 * np.pi)
        _state.x = np.append(demodulated, demodulated[-1])
        _state.history.append("FM demodulated")
        return None

    elif op == "scale":
        if _state.x is None:
            return "No signal yet. Create a signal first."
        factor = op_dict.get("factor", 2.0)
        _state.x = _state.x * factor
        _state.history.append(f"scaled by {factor}")
        return None

    elif op == "combine":
        if _state.x is None:
            return "No signal yet. Create a signal first."
        sig_type = op_dict.get("signal_type", "sine")
        freq = op_dict.get("frequency", 10.0)
        amp = op_dict.get("amplitude", 1.0)
        combine_mode = op_dict.get("combine_mode", "add")

        if sig_type == "sine":
            x2 = amp * np.sin(2 * np.pi * freq * _state.t)
        elif sig_type == "cosine":
            x2 = amp * np.cos(2 * np.pi * freq * _state.t)
        elif sig_type == "square":
            x2 = amp * signal.square(2 * np.pi * freq * _state.t)
        elif sig_type == "sawtooth":
            x2 = amp * signal.sawtooth(2 * np.pi * freq * _state.t)
        elif sig_type == "triangle":
            x2 = amp * signal.sawtooth(2 * np.pi * freq * _state.t, width=0.5)
        else:
            x2 = amp * np.sin(2 * np.pi * freq * _state.t)

        if combine_mode == "add":
            _state.x = _state.x + x2
            _state.history.append(f"added {sig_type} {freq}Hz")
        elif combine_mode == "multiply":
            _state.x = _state.x * x2
            _state.history.append(f"multiplied by {sig_type} {freq}Hz")
        return None

    elif op == "convolve":
        if _state.x is None:
            return "No signal yet. Create a signal first."
        sig_type = op_dict.get("signal_type", "rect")
        freq = op_dict.get("frequency", 2.0)
        amp = op_dict.get("amplitude", 1.0)

        if sig_type == "rect":
            period = 1.0 / freq
            x2 = amp * ((_state.t % period) < (period / 2)).astype(float)
        elif sig_type == "sine":
            x2 = amp * np.sin(2 * np.pi * freq * _state.t)
        elif sig_type == "impulse":
            x2 = np.zeros_like(_state.t)
            x2[0] = amp
        else:
            x2 = amp * np.sin(2 * np.pi * freq * _state.t)

        conv_full = np.convolve(_state.x, x2) / _state.sample_rate
        _state.x = conv_full[:len(_state.t)]
        _state.history.append(f"convolved with {sig_type}")
        return None

    elif op == "bode":
        if _state.last_filter_b is None:
            return "No filter applied yet. Apply a filter first."
        return _plot_bode(_state.last_filter_b, _state.last_filter_a,
                          _state.sample_rate, "Last Applied Filter")

    elif op == "get_code":
        language = op_dict.get("language", "python")
        return _generate_code(language)

    else:
        return "Operation not recognized."

# ── Tool ──────────────────────────────────────────────────────────────────────
def frequency_sandbox(instruction: str) -> str:
    """
    Interactive frequency sandbox. Student describes a signal in English and can
    iteratively build and modify it. Supports multiple operations in one instruction.
    Maintains signal state between calls.
    Supports: create, noise, Butterworth filter, AM/FM modulate, AM/FM demodulate,
    combine signals, convolve, scale, Bode plot, get MATLAB/Python code, reset.
    Args:
        instruction (str): Natural language instruction, e.g.
                          'give me a 10Hz sine wave and AM modulate it',
                          'add a 20Hz cosine to the current signal',
                          'apply a lowpass filter at 30Hz',
                          'demodulate the AM signal',
                          'show bode plot',
                          'convolve with a rect pulse',
                          'give me the MATLAB code for this',
                          'show me the Python code'
    Returns:
        str: Base64 encoded PNG image, or code string if code was requested
    """
    ops = _parse_operations(instruction)

    for i, op_dict in enumerate(ops):
        is_last = (i == len(ops) - 1)
        result = _apply_operation(op_dict)

        # Return directly for special outputs
        if op_dict.get("op") in ["bode", "get_code"] and result:
            return result

        # If error occurred mid-chain return immediately
        if result and not is_last:
            return result

    if _state.x is None:
        return "Sandbox was reset. Start with a new signal."

    title = " → ".join(_state.history[-3:])
    return _plot_current_state(title)