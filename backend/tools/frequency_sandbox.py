"""
frequency_sandbox.py
SigmaTutor Frequency Sandbox Tool.
Receives LLM from agent.py — no LLM created here.
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import base64
import io
import json
from scipy import signal
from langchain_core.messages import HumanMessage

matplotlib.use('Agg')


# ── State ─────────────────────────────────────────────────────────────────────

class SignalState:
    def __init__(self):
        self.x           = None
        self.t           = None
        self.sample_rate = 1000.0
        self.history     = []
        self.last_filter_b = None
        self.last_filter_a = None

    def reset(self):
        self.__init__()

_state = SignalState()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _style_ax(ax):
    ax.set_facecolor('#070b14')
    ax.tick_params(colors='#94a3b8')
    ax.xaxis.label.set_color('#94a3b8')
    ax.yaxis.label.set_color('#94a3b8')
    ax.title.set_color('#00d4ff')
    for spine in ax.spines.values():
        spine.set_edgecolor('#1a2a45')
    ax.grid(True, color='#1a2a45')


def _plot_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img


def _plot_current_state(title: str) -> str:
    t           = _state.t
    x           = _state.x
    sample_rate = _state.sample_rate

    N         = len(t)
    fft_vals  = np.abs(np.fft.fftshift(np.fft.fft(x))) / N
    fft_freqs = np.fft.fftshift(np.fft.fftfreq(N, 1 / sample_rate))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
    fig.patch.set_facecolor('#0d1525')
    _style_ax(ax1)
    _style_ax(ax2)

    ax1.plot(t, x, color='#00d4ff', linewidth=1.5)
    ax1.set_title(f'Time Domain — {title}')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Amplitude')

    ax2.plot(fft_freqs, fft_vals, color='#7c3aed', linewidth=1.5)
    ax2.set_title('Frequency Domain (FFT)')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Magnitude')
    ax2.set_xlim(-sample_rate / 2, sample_rate / 2)

    plt.tight_layout()
    return _plot_to_base64(fig)


# ── Parse operations ──────────────────────────────────────────────────────────

def _parse_operations(instruction: str, llm) -> list:
    history_str = ", ".join(_state.history) if _state.history else "none yet"

    prompt = f"""Parse this signal instruction into a JSON array of operations.

Instruction: "{instruction}"
Current history: {history_str}

Return ONLY raw JSON array, no explanation, no markdown.

Operations:
{{"op":"create","signal_type":"sine","frequency":10.0,"amplitude":1.0,"duration":1.0,"sample_rate":1000.0}}
signal_type: sine | cosine | square | sawtooth | triangle | chirp

{{"op":"add_noise","noise_type":"gaussian","std":0.1}}
{{"op":"filter","filter_type":"lowpass","cutoff":20.0,"order":5}}
filter_type: lowpass | highpass | bandpass

{{"op":"am_modulate","carrier_freq":100.0,"modulation_index":1.0}}
{{"op":"fm_modulate","carrier_freq":100.0,"freq_deviation":10.0}}
{{"op":"am_demodulate"}}
{{"op":"fm_demodulate","carrier_freq":100.0}}
{{"op":"scale","factor":2.0}}
{{"op":"combine","signal_type":"sine","frequency":20.0,"amplitude":1.0,"combine_mode":"add"}}
{{"op":"convolve","signal_type":"rect","frequency":2.0,"amplitude":1.0}}
{{"op":"bode"}}
{{"op":"get_code","language":"matlab"}}
{{"op":"get_code","language":"python"}}
{{"op":"reset"}}

Examples:
"10Hz sine wave" → [{{"op":"create","signal_type":"sine","frequency":10.0,"amplitude":1.0,"duration":1.0,"sample_rate":1000.0}}]
"create sine and AM modulate" → [{{"op":"create","signal_type":"sine","frequency":10.0,"amplitude":1.0,"duration":1.0,"sample_rate":1000.0}},{{"op":"am_modulate","carrier_freq":100.0,"modulation_index":1.0}}]
"reset" → [{{"op":"reset"}}]"""

    print(f"DEBUG SANDBOX: parsing '{instruction}'")
    response = llm.invoke([HumanMessage(content=prompt)])
    text     = response.content.strip()

    # Strip markdown
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

    print(f"DEBUG SANDBOX: parsed → {text[:100]}")
    return json.loads(text.strip())


# ── Apply operation ───────────────────────────────────────────────────────────

def _apply_operation(op_dict: dict, llm) -> str:
    op = op_dict.get("op", "")
    print(f"DEBUG SANDBOX: applying op='{op}'")

    if op == "reset":
        _state.reset()
        return "Sandbox reset. Start with a new signal."

    elif op == "create":
        fs       = float(op_dict.get("sample_rate", 1000.0))
        duration = float(op_dict.get("duration", 1.0))
        freq     = float(op_dict.get("frequency", 10.0))
        amp      = float(op_dict.get("amplitude", 1.0))
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
        else:
            _state.x = amp * np.sin(2 * np.pi * freq * t)

        _state.history.append(f"created {sig_type} {freq}Hz")
        return None

    elif op == "add_noise":
        if _state.x is None:
            return "No signal yet. Create a signal first."
        noise_type = op_dict.get("noise_type", "gaussian")
        std        = float(op_dict.get("std", 0.1))
        if noise_type == "gaussian":
            noise = np.random.normal(0, std, len(_state.x))
        else:
            noise = np.random.uniform(-std, std, len(_state.x))
        _state.x = _state.x + noise
        _state.history.append(f"added {noise_type} noise")
        return None

    elif op == "filter":
        if _state.x is None:
            return "No signal yet. Create a signal first."
        filter_type = op_dict.get("filter_type", "lowpass")
        cutoff      = op_dict.get("cutoff", 20.0)
        order       = int(op_dict.get("order", 5))
        nyq         = _state.sample_rate / 2

        if filter_type == "bandpass":
            cutoff_list = cutoff if isinstance(cutoff, list) else [cutoff * 0.5, cutoff]
            norm = [c / nyq for c in cutoff_list]
        else:
            norm = float(cutoff) / nyq

        b, a = signal.butter(order, norm, btype=filter_type)
        _state.last_filter_b = b
        _state.last_filter_a = a
        _state.x = signal.filtfilt(b, a, _state.x)
        _state.history.append(f"applied {filter_type} filter at {cutoff}Hz")
        return None

    elif op == "am_modulate":
        if _state.x is None:
            return "No signal yet."
        fc      = float(op_dict.get("carrier_freq", 100.0))
        mi      = float(op_dict.get("modulation_index", 1.0))
        carrier = np.cos(2 * np.pi * fc * _state.t)
        _state.x = (1 + mi * _state.x) * carrier
        _state.history.append(f"AM modulated {fc}Hz carrier")
        return None

    elif op == "fm_modulate":
        if _state.x is None:
            return "No signal yet."
        fc       = float(op_dict.get("carrier_freq", 100.0))
        fd       = float(op_dict.get("freq_deviation", 10.0))
        integral = np.cumsum(_state.x) / _state.sample_rate
        _state.x = np.cos(2 * np.pi * fc * _state.t + 2 * np.pi * fd * integral)
        _state.history.append(f"FM modulated {fc}Hz carrier")
        return None

    elif op == "am_demodulate":
        if _state.x is None:
            return "No signal yet."
        analytic = signal.hilbert(_state.x)
        envelope = np.abs(analytic) - np.mean(np.abs(analytic))
        _state.x = envelope
        _state.history.append("AM demodulated")
        return None

    elif op == "fm_demodulate":
        if _state.x is None:
            return "No signal yet."
        analytic    = signal.hilbert(_state.x)
        phase       = np.unwrap(np.angle(analytic))
        demodulated = np.diff(phase) * _state.sample_rate / (2 * np.pi)
        _state.x    = np.append(demodulated, demodulated[-1])
        _state.history.append("FM demodulated")
        return None

    elif op == "scale":
        if _state.x is None:
            return "No signal yet."
        factor   = float(op_dict.get("factor", 2.0))
        _state.x = _state.x * factor
        _state.history.append(f"scaled by {factor}")
        return None

    elif op == "combine":
        if _state.x is None:
            return "No signal yet."
        sig_type     = op_dict.get("signal_type", "sine")
        freq         = float(op_dict.get("frequency", 10.0))
        amp          = float(op_dict.get("amplitude", 1.0))
        combine_mode = op_dict.get("combine_mode", "add")

        if sig_type == "sine":
            x2 = amp * np.sin(2 * np.pi * freq * _state.t)
        elif sig_type == "cosine":
            x2 = amp * np.cos(2 * np.pi * freq * _state.t)
        elif sig_type == "square":
            x2 = amp * signal.square(2 * np.pi * freq * _state.t)
        else:
            x2 = amp * np.sin(2 * np.pi * freq * _state.t)

        if combine_mode == "multiply":
            _state.x = _state.x * x2
            _state.history.append(f"multiplied by {sig_type} {freq}Hz")
        else:
            _state.x = _state.x + x2
            _state.history.append(f"added {sig_type} {freq}Hz")
        return None

    elif op == "convolve":
        if _state.x is None:
            return "No signal yet."
        sig_type = op_dict.get("signal_type", "rect")
        freq     = float(op_dict.get("frequency", 2.0))
        amp      = float(op_dict.get("amplitude", 1.0))

        if sig_type == "rect":
            period = 1.0 / freq
            x2 = amp * ((_state.t % period) < (period / 2)).astype(float)
        elif sig_type == "impulse":
            x2    = np.zeros_like(_state.t)
            x2[0] = amp
        else:
            x2 = amp * np.sin(2 * np.pi * freq * _state.t)

        conv_full = np.convolve(_state.x, x2) / _state.sample_rate
        _state.x  = conv_full[:len(_state.t)]
        _state.history.append(f"convolved with {sig_type}")
        return None

    elif op == "bode":
        if _state.last_filter_b is None:
            return "No filter applied yet."
        from frequency_sandbox import _plot_bode
        return _plot_bode(
            _state.last_filter_b,
            _state.last_filter_a,
            _state.sample_rate,
            "Last Applied Filter"
        )

    elif op == "get_code":
        language    = op_dict.get("language", "python")
        history_str = " → ".join(_state.history)
        duration    = float(_state.t[-1]) if _state.t is not None else 1.0

        prompt = f"""Generate {'MATLAB' if language == 'matlab' else 'Python'} code for this signal chain:
{history_str}
Sample rate: {_state.sample_rate} Hz, Duration: {duration}s
Return ONLY the code."""

        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()

    else:
        return f"Unknown operation: {op}"


# ── Main entry ────────────────────────────────────────────────────────────────

def frequency_sandbox(instruction: str, llm) -> str:
    print(f"DEBUG SANDBOX: instruction='{instruction}'")

    try:
        ops = _parse_operations(instruction, llm)
    except Exception as e:
        return f"Could not parse instruction: {str(e)}"

    for i, op_dict in enumerate(ops):
        is_last = (i == len(ops) - 1)
        result  = _apply_operation(op_dict, llm)

        if op_dict.get("op") in ("bode", "get_code") and result:
            return result

        if result and not is_last:
            return result

    if _state.x is None:
        return "Sandbox was reset. Start with a new signal."

    title = " → ".join(_state.history[-3:]) if _state.history else "Signal"
    return _plot_current_state(title)


def run_sandbox(instruction: str, llm=None) -> str:
    return frequency_sandbox(instruction, llm)