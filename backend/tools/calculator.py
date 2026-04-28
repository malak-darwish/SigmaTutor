"""
calculator.py

SigmaTutor Signal Calculator Tool.

This tool solves common numerical problems in Signals & Systems
and Communication Engineering.

Uses:
- Python formulas for exact calculations
- WolframAlpha for optional verification
- Gemini fallback for freeform calculation explanation
"""

import math
from typing import Dict, Any
from backend.tools.groq_client import ask_groq_json

from backend.tools.wolfram_client import wolfram_verification_block




BOLTZMANN_CONSTANT = 1.380649e-23


def _error(title: str, message: str) -> Dict[str, Any]:
    return {
        "type": "error",
        "title": title,
        "message": message
    }


def _to_float(value, field_name: str):
    try:
        return float(value), None
    except (TypeError, ValueError):
        return None, _error("Invalid Input", f"{field_name} must be a number.")


def nyquist_rate(max_frequency_hz: float, use_wolfram: bool = True) -> Dict[str, Any]:
    max_frequency_hz, err = _to_float(max_frequency_hz, "Maximum frequency")
    if err:
        return err

    if max_frequency_hz <= 0:
        return _error("Invalid Frequency", "Maximum frequency must be greater than 0.")

    fs = 2 * max_frequency_hz

    return {
        "type": "calculation",
        "title": "Nyquist Sampling Rate",
        "given": {"maximum_frequency_hz": max_frequency_hz},
        "formula_latex": "f_s \\geq 2f_{max}",
        "steps": [
            f"The highest frequency in the signal is fmax = {max_frequency_hz} Hz.",
            "According to the Nyquist sampling theorem, the sampling frequency must be at least twice the highest frequency.",
            f"fs >= 2 × {max_frequency_hz} = {fs} Hz."
        ],
        "final_answer": f"{fs} Hz",
        "wolfram_verification": wolfram_verification_block(f"2 * {max_frequency_hz}") if use_wolfram else None,
        "exam_tip": "For no aliasing, sample at least twice the highest frequency."
    }


def sampling_interval(sampling_frequency_hz: float, use_wolfram: bool = True) -> Dict[str, Any]:
    sampling_frequency_hz, err = _to_float(sampling_frequency_hz, "Sampling frequency")
    if err:
        return err

    if sampling_frequency_hz <= 0:
        return _error("Invalid Sampling Frequency", "Sampling frequency must be greater than 0.")

    ts = 1 / sampling_frequency_hz

    return {
        "type": "calculation",
        "title": "Sampling Interval",
        "given": {"sampling_frequency_hz": sampling_frequency_hz},
        "formula_latex": "T_s = \\frac{1}{f_s}",
        "steps": [
            f"Given sampling frequency fs = {sampling_frequency_hz} Hz.",
            "The sampling interval is the time between two consecutive samples.",
            f"Ts = 1 / {sampling_frequency_hz} = {ts:.8f} s."
        ],
        "final_answer": f"{ts:.8f} s",
        "wolfram_verification": wolfram_verification_block(f"1 / {sampling_frequency_hz}") if use_wolfram else None,
        "exam_tip": "Sampling frequency and sampling interval are inverses."
    }


def shannon_capacity(bandwidth_hz: float, snr_db: float, use_wolfram: bool = True) -> Dict[str, Any]:
    bandwidth_hz, err1 = _to_float(bandwidth_hz, "Bandwidth")
    snr_db, err2 = _to_float(snr_db, "SNR in dB")

    if err1:
        return err1
    if err2:
        return err2

    if bandwidth_hz <= 0:
        return _error("Invalid Bandwidth", "Bandwidth must be greater than 0.")

    snr_linear = 10 ** (snr_db / 10)
    capacity = bandwidth_hz * math.log2(1 + snr_linear)

    wolfram_query = f"{bandwidth_hz} * log2(1 + 10^({snr_db}/10))"

    return {
        "type": "calculation",
        "title": "Shannon Channel Capacity",
        "given": {
            "bandwidth_hz": bandwidth_hz,
            "snr_db": snr_db,
            "snr_linear": round(snr_linear, 6)
        },
        "formula_latex": "C = B \\log_2(1 + SNR)",
        "steps": [
            f"Given bandwidth B = {bandwidth_hz} Hz.",
            f"Given SNR = {snr_db} dB.",
            f"Convert SNR from dB to linear: SNR = 10^({snr_db}/10) = {snr_linear:.6f}.",
            f"Apply Shannon formula: C = {bandwidth_hz} log2(1 + {snr_linear:.6f}).",
            f"C = {capacity:.4f} bits/s."
        ],
        "final_answer": f"{capacity:.4f} bits/s",
        "wolfram_verification": wolfram_verification_block(wolfram_query) if use_wolfram else None,
        "exam_tip": "Always convert SNR from dB to linear before using Shannon capacity."
    }


def snr_db_to_linear(snr_db: float, use_wolfram: bool = True) -> Dict[str, Any]:
    snr_db, err = _to_float(snr_db, "SNR in dB")
    if err:
        return err

    snr_linear = 10 ** (snr_db / 10)

    return {
        "type": "calculation",
        "title": "SNR dB to Linear Conversion",
        "given": {"snr_db": snr_db},
        "formula_latex": "SNR_{linear} = 10^{SNR_{dB}/10}",
        "steps": [
            f"SNR_dB = {snr_db}.",
            f"SNR_linear = 10^({snr_db}/10).",
            f"SNR_linear = {snr_linear:.6f}."
        ],
        "final_answer": f"{snr_linear:.6f}",
        "wolfram_verification": wolfram_verification_block(f"10^({snr_db}/10)") if use_wolfram else None,
        "exam_tip": "Use 10^(dB/10) for power ratios such as SNR."
    }


def snr_linear_to_db(snr_linear: float, use_wolfram: bool = True) -> Dict[str, Any]:
    snr_linear, err = _to_float(snr_linear, "Linear SNR")
    if err:
        return err

    if snr_linear <= 0:
        return _error("Invalid SNR", "Linear SNR must be greater than 0.")

    snr_db = 10 * math.log10(snr_linear)

    return {
        "type": "calculation",
        "title": "SNR Linear to dB Conversion",
        "given": {"snr_linear": snr_linear},
        "formula_latex": "SNR_{dB} = 10\\log_{10}(SNR_{linear})",
        "steps": [
            f"SNR_linear = {snr_linear}.",
            f"SNR_dB = 10 log10({snr_linear}).",
            f"SNR_dB = {snr_db:.4f} dB."
        ],
        "final_answer": f"{snr_db:.4f} dB",
        "wolfram_verification": wolfram_verification_block(f"10 * log10({snr_linear})") if use_wolfram else None,
        "exam_tip": "Use 10log10(x) for power ratios."
    }


def period_from_frequency(frequency_hz: float, use_wolfram: bool = True) -> Dict[str, Any]:
    frequency_hz, err = _to_float(frequency_hz, "Frequency")
    if err:
        return err

    if frequency_hz <= 0:
        return _error("Invalid Frequency", "Frequency must be greater than 0.")

    period = 1 / frequency_hz

    return {
        "type": "calculation",
        "title": "Period from Frequency",
        "given": {"frequency_hz": frequency_hz},
        "formula_latex": "T = \\frac{1}{f}",
        "steps": [
            f"Given frequency f = {frequency_hz} Hz.",
            f"T = 1 / {frequency_hz}.",
            f"T = {period:.6f} seconds."
        ],
        "final_answer": f"{period:.6f} s",
        "wolfram_verification": wolfram_verification_block(f"1 / {frequency_hz}") if use_wolfram else None,
        "exam_tip": "Frequency and period are inverses."
    }


def frequency_from_period(period_seconds: float, use_wolfram: bool = True) -> Dict[str, Any]:
    period_seconds, err = _to_float(period_seconds, "Period")
    if err:
        return err

    if period_seconds <= 0:
        return _error("Invalid Period", "Period must be greater than 0.")

    frequency = 1 / period_seconds

    return {
        "type": "calculation",
        "title": "Frequency from Period",
        "given": {"period_seconds": period_seconds},
        "formula_latex": "f = \\frac{1}{T}",
        "steps": [
            f"Given period T = {period_seconds} s.",
            f"f = 1 / {period_seconds}.",
            f"f = {frequency:.6f} Hz."
        ],
        "final_answer": f"{frequency:.6f} Hz",
        "wolfram_verification": wolfram_verification_block(f"1 / {period_seconds}") if use_wolfram else None,
        "exam_tip": "Period and frequency are inverses."
    }


def frequency_from_angular_frequency(omega_rad_per_sec: float, use_wolfram: bool = True) -> Dict[str, Any]:
    omega_rad_per_sec, err = _to_float(omega_rad_per_sec, "Angular frequency")
    if err:
        return err

    frequency = omega_rad_per_sec / (2 * math.pi)

    return {
        "type": "calculation",
        "title": "Frequency from Angular Frequency",
        "given": {"omega_rad_per_sec": omega_rad_per_sec},
        "formula_latex": "f = \\frac{\\omega}{2\\pi}",
        "steps": [
            f"Given angular frequency ω = {omega_rad_per_sec} rad/s.",
            "Use f = ω / (2π).",
            f"f = {omega_rad_per_sec} / (2π) = {frequency:.6f} Hz."
        ],
        "final_answer": f"{frequency:.6f} Hz",
        "wolfram_verification": wolfram_verification_block(f"{omega_rad_per_sec} / (2*pi)") if use_wolfram else None,
        "exam_tip": "If the signal is cos(ωt), the frequency is ω/(2π)."
    }


def angular_frequency_from_frequency(frequency_hz: float, use_wolfram: bool = True) -> Dict[str, Any]:
    frequency_hz, err = _to_float(frequency_hz, "Frequency")
    if err:
        return err

    omega = 2 * math.pi * frequency_hz

    return {
        "type": "calculation",
        "title": "Angular Frequency from Frequency",
        "given": {"frequency_hz": frequency_hz},
        "formula_latex": "\\omega = 2\\pi f",
        "steps": [
            f"Given frequency f = {frequency_hz} Hz.",
            "Use ω = 2πf.",
            f"ω = 2π × {frequency_hz} = {omega:.6f} rad/s."
        ],
        "final_answer": f"{omega:.6f} rad/s",
        "wolfram_verification": wolfram_verification_block(f"2*pi*{frequency_hz}") if use_wolfram else None,
        "exam_tip": "For cos(2πft), the angular frequency is 2πf."
    }


def wavelength(speed_m_per_s: float, frequency_hz: float, use_wolfram: bool = True) -> Dict[str, Any]:
    speed_m_per_s, err1 = _to_float(speed_m_per_s, "Propagation speed")
    frequency_hz, err2 = _to_float(frequency_hz, "Frequency")

    if err1:
        return err1
    if err2:
        return err2

    if frequency_hz <= 0:
        return _error("Invalid Frequency", "Frequency must be greater than 0.")

    lam = speed_m_per_s / frequency_hz

    return {
        "type": "calculation",
        "title": "Wavelength",
        "given": {
            "speed_m_per_s": speed_m_per_s,
            "frequency_hz": frequency_hz
        },
        "formula_latex": "\\lambda = \\frac{v}{f}",
        "steps": [
            f"Given propagation speed v = {speed_m_per_s} m/s.",
            f"Given frequency f = {frequency_hz} Hz.",
            f"λ = v/f = {speed_m_per_s}/{frequency_hz}.",
            f"λ = {lam:.6f} m."
        ],
        "final_answer": f"{lam:.6f} m",
        "wolfram_verification": wolfram_verification_block(f"{speed_m_per_s} / {frequency_hz}") if use_wolfram else None,
        "exam_tip": "For electromagnetic waves in free space, v is approximately 3 × 10^8 m/s."
    }


def am_modulation_index(message_amplitude: float, carrier_amplitude: float, use_wolfram: bool = True) -> Dict[str, Any]:
    message_amplitude, err1 = _to_float(message_amplitude, "Message amplitude")
    carrier_amplitude, err2 = _to_float(carrier_amplitude, "Carrier amplitude")

    if err1:
        return err1
    if err2:
        return err2

    if carrier_amplitude == 0:
        return _error("Invalid Carrier Amplitude", "Carrier amplitude cannot be zero.")

    mu = message_amplitude / carrier_amplitude

    if mu < 1:
        condition = "Undermodulation / normal AM"
    elif mu == 1:
        condition = "Critical modulation"
    else:
        condition = "Overmodulation; distortion may occur"

    return {
        "type": "calculation",
        "title": "AM Modulation Index",
        "given": {
            "message_amplitude": message_amplitude,
            "carrier_amplitude": carrier_amplitude
        },
        "formula_latex": "\\mu = \\frac{A_m}{A_c}",
        "steps": [
            f"Given message amplitude Am = {message_amplitude}.",
            f"Given carrier amplitude Ac = {carrier_amplitude}.",
            f"μ = Am/Ac = {message_amplitude}/{carrier_amplitude}.",
            f"μ = {mu:.4f}."
        ],
        "final_answer": f"μ = {mu:.4f}",
        "interpretation": condition,
        "wolfram_verification": wolfram_verification_block(f"{message_amplitude} / {carrier_amplitude}") if use_wolfram else None,
        "exam_tip": "For standard AM, μ should usually be less than or equal to 1."
    }


def am_bandwidth(max_message_frequency_hz: float, use_wolfram: bool = True) -> Dict[str, Any]:
    max_message_frequency_hz, err = _to_float(max_message_frequency_hz, "Maximum message frequency")
    if err:
        return err

    if max_message_frequency_hz <= 0:
        return _error("Invalid Frequency", "Maximum message frequency must be greater than 0.")

    bw = 2 * max_message_frequency_hz

    return {
        "type": "calculation",
        "title": "AM Bandwidth",
        "given": {"maximum_message_frequency_hz": max_message_frequency_hz},
        "formula_latex": "BW_{AM} = 2f_m",
        "steps": [
            f"Given maximum message frequency fm = {max_message_frequency_hz} Hz.",
            "For standard AM, the bandwidth equals twice the maximum message frequency.",
            f"BW = 2 × {max_message_frequency_hz} = {bw} Hz."
        ],
        "final_answer": f"{bw} Hz",
        "wolfram_verification": wolfram_verification_block(f"2 * {max_message_frequency_hz}") if use_wolfram else None,
        "exam_tip": "Standard AM and DSB-SC both require bandwidth equal to 2fm."
    }


def dsb_sc_bandwidth(max_message_frequency_hz: float, use_wolfram: bool = True) -> Dict[str, Any]:
    result = am_bandwidth(max_message_frequency_hz, use_wolfram)
    if result.get("type") == "calculation":
        result["title"] = "DSB-SC Bandwidth"
        result["formula_latex"] = "BW_{DSB-SC} = 2f_m"
        result["exam_tip"] = "DSB-SC suppresses the carrier, but the bandwidth is still 2fm."
    return result


def ssb_bandwidth(max_message_frequency_hz: float, use_wolfram: bool = True) -> Dict[str, Any]:
    max_message_frequency_hz, err = _to_float(max_message_frequency_hz, "Maximum message frequency")
    if err:
        return err

    if max_message_frequency_hz <= 0:
        return _error("Invalid Frequency", "Maximum message frequency must be greater than 0.")

    bw = max_message_frequency_hz

    return {
        "type": "calculation",
        "title": "SSB Bandwidth",
        "given": {"maximum_message_frequency_hz": max_message_frequency_hz},
        "formula_latex": "BW_{SSB} = f_m",
        "steps": [
            f"Given maximum message frequency fm = {max_message_frequency_hz} Hz.",
            "In single-sideband modulation, only one sideband is transmitted.",
            f"Therefore, BW = fm = {bw} Hz."
        ],
        "final_answer": f"{bw} Hz",
        "wolfram_verification": wolfram_verification_block(f"{max_message_frequency_hz}") if use_wolfram else None,
        "exam_tip": "SSB uses half the bandwidth of standard AM or DSB-SC."
    }


def bit_rate(bits_per_symbol: float, symbol_rate_baud: float, use_wolfram: bool = True) -> Dict[str, Any]:
    bits_per_symbol, err1 = _to_float(bits_per_symbol, "Bits per symbol")
    symbol_rate_baud, err2 = _to_float(symbol_rate_baud, "Symbol rate")

    if err1:
        return err1
    if err2:
        return err2

    if bits_per_symbol <= 0 or symbol_rate_baud <= 0:
        return _error("Invalid Input", "Bits per symbol and symbol rate must be greater than 0.")

    rb = bits_per_symbol * symbol_rate_baud

    return {
        "type": "calculation",
        "title": "Bit Rate",
        "given": {
            "bits_per_symbol": bits_per_symbol,
            "symbol_rate_baud": symbol_rate_baud
        },
        "formula_latex": "R_b = kR_s",
        "steps": [
            f"Given bits per symbol k = {bits_per_symbol}.",
            f"Given symbol rate Rs = {symbol_rate_baud} baud.",
            f"Rb = k × Rs = {bits_per_symbol} × {symbol_rate_baud} = {rb} bits/s."
        ],
        "final_answer": f"{rb} bits/s",
        "wolfram_verification": wolfram_verification_block(f"{bits_per_symbol} * {symbol_rate_baud}") if use_wolfram else None,
        "exam_tip": "For M-ary modulation, bits per symbol is log2(M)."
    }


def noise_power_watts(bandwidth_hz: float, temperature_k: float = 290, use_wolfram: bool = True) -> Dict[str, Any]:
    bandwidth_hz, err1 = _to_float(bandwidth_hz, "Bandwidth")
    temperature_k, err2 = _to_float(temperature_k, "Temperature")

    if err1:
        return err1
    if err2:
        return err2

    if bandwidth_hz <= 0 or temperature_k <= 0:
        return _error("Invalid Input", "Bandwidth and temperature must be greater than 0.")

    noise = BOLTZMANN_CONSTANT * temperature_k * bandwidth_hz

    wolfram_query = f"{BOLTZMANN_CONSTANT} * {temperature_k} * {bandwidth_hz}"

    return {
        "type": "calculation",
        "title": "Thermal Noise Power",
        "given": {
            "boltzmann_constant": BOLTZMANN_CONSTANT,
            "temperature_k": temperature_k,
            "bandwidth_hz": bandwidth_hz
        },
        "formula_latex": "N = kTB",
        "steps": [
            f"Boltzmann constant k = {BOLTZMANN_CONSTANT} J/K.",
            f"Temperature T = {temperature_k} K.",
            f"Bandwidth B = {bandwidth_hz} Hz.",
            f"N = kTB = {BOLTZMANN_CONSTANT} × {temperature_k} × {bandwidth_hz}.",
            f"N = {noise:.12e} W."
        ],
        "final_answer": f"{noise:.12e} W",
        "wolfram_verification": wolfram_verification_block(wolfram_query) if use_wolfram else None,
        "exam_tip": "Thermal noise increases with bandwidth and temperature."
    }


def thermal_noise_dbm(bandwidth_hz: float, noise_figure_db: float = 0, use_wolfram: bool = True) -> Dict[str, Any]:
    bandwidth_hz, err1 = _to_float(bandwidth_hz, "Bandwidth")
    noise_figure_db, err2 = _to_float(noise_figure_db, "Noise figure")

    if err1:
        return err1
    if err2:
        return err2

    if bandwidth_hz <= 0:
        return _error("Invalid Bandwidth", "Bandwidth must be greater than 0.")

    noise_dbm = -174 + 10 * math.log10(bandwidth_hz) + noise_figure_db

    wolfram_query = f"-174 + 10*log10({bandwidth_hz}) + {noise_figure_db}"

    return {
        "type": "calculation",
        "title": "Thermal Noise in dBm",
        "given": {
            "bandwidth_hz": bandwidth_hz,
            "noise_figure_db": noise_figure_db
        },
        "formula_latex": "N_{dBm} = -174 + 10\\log_{10}(B) + NF",
        "steps": [
            "At room temperature, thermal noise density is approximately -174 dBm/Hz.",
            f"Bandwidth B = {bandwidth_hz} Hz.",
            f"Noise figure NF = {noise_figure_db} dB.",
            f"N = -174 + 10log10({bandwidth_hz}) + {noise_figure_db}.",
            f"N = {noise_dbm:.4f} dBm."
        ],
        "final_answer": f"{noise_dbm:.4f} dBm",
        "wolfram_verification": wolfram_verification_block(wolfram_query) if use_wolfram else None,
        "exam_tip": "This shortcut is very common in communication systems."
    }


def signal_power_from_vrms(vrms: float, resistance_ohms: float, use_wolfram: bool = True) -> Dict[str, Any]:
    vrms, err1 = _to_float(vrms, "RMS voltage")
    resistance_ohms, err2 = _to_float(resistance_ohms, "Resistance")

    if err1:
        return err1
    if err2:
        return err2

    if resistance_ohms <= 0:
        return _error("Invalid Resistance", "Resistance must be greater than 0.")

    power_watts = (vrms ** 2) / resistance_ohms
    power_dbm = 10 * math.log10(power_watts / 1e-3) if power_watts > 0 else float("-inf")

    wolfram_query = f"({vrms}^2) / {resistance_ohms}"

    return {
        "type": "calculation",
        "title": "Signal Power from RMS Voltage",
        "given": {
            "vrms": vrms,
            "resistance_ohms": resistance_ohms
        },
        "formula_latex": "P = \\frac{V_{rms}^2}{R}",
        "steps": [
            f"Given Vrms = {vrms} V.",
            f"Given resistance R = {resistance_ohms} Ω.",
            f"P = Vrms²/R = {vrms}²/{resistance_ohms}.",
            f"P = {power_watts:.8f} W.",
            f"In dBm: P(dBm) = 10log10(P/1mW) = {power_dbm:.4f} dBm."
        ],
        "final_answer": f"{power_watts:.8f} W = {power_dbm:.4f} dBm",
        "wolfram_verification": wolfram_verification_block(wolfram_query) if use_wolfram else None,
        "exam_tip": "Use RMS voltage, not peak voltage, when calculating average power."
    }


def rc_lowpass_cutoff(resistance_ohms: float, capacitance_farads: float, use_wolfram: bool = True) -> Dict[str, Any]:
    resistance_ohms, err1 = _to_float(resistance_ohms, "Resistance")
    capacitance_farads, err2 = _to_float(capacitance_farads, "Capacitance")

    if err1:
        return err1
    if err2:
        return err2

    if resistance_ohms <= 0 or capacitance_farads <= 0:
        return _error("Invalid Input", "Resistance and capacitance must be greater than 0.")

    fc = 1 / (2 * math.pi * resistance_ohms * capacitance_farads)

    wolfram_query = f"1 / (2*pi*{resistance_ohms}*{capacitance_farads})"

    return {
        "type": "calculation",
        "title": "RC Low-Pass Cutoff Frequency",
        "given": {
            "resistance_ohms": resistance_ohms,
            "capacitance_farads": capacitance_farads
        },
        "formula_latex": "f_c = \\frac{1}{2\\pi RC}",
        "steps": [
            f"Given R = {resistance_ohms} Ω.",
            f"Given C = {capacitance_farads} F.",
            f"fc = 1/(2πRC) = 1/(2π × {resistance_ohms} × {capacitance_farads}).",
            f"fc = {fc:.4f} Hz."
        ],
        "final_answer": f"{fc:.4f} Hz",
        "wolfram_verification": wolfram_verification_block(wolfram_query) if use_wolfram else None,
        "exam_tip": "At cutoff frequency, the magnitude drops to 1/√2 of the passband value, or -3 dB."
    }


def first_order_lpf_magnitude(frequency_hz: float, cutoff_hz: float, use_wolfram: bool = True) -> Dict[str, Any]:
    frequency_hz, err1 = _to_float(frequency_hz, "Frequency")
    cutoff_hz, err2 = _to_float(cutoff_hz, "Cutoff frequency")

    if err1:
        return err1
    if err2:
        return err2

    if frequency_hz < 0 or cutoff_hz <= 0:
        return _error("Invalid Input", "Frequency must be non-negative and cutoff frequency must be greater than 0.")

    magnitude = 1 / math.sqrt(1 + (frequency_hz / cutoff_hz) ** 2)
    magnitude_db = 20 * math.log10(magnitude) if magnitude > 0 else float("-inf")

    wolfram_query = f"1 / sqrt(1 + ({frequency_hz}/{cutoff_hz})^2)"

    return {
        "type": "calculation",
        "title": "First-Order Low-Pass Filter Magnitude",
        "given": {
            "frequency_hz": frequency_hz,
            "cutoff_hz": cutoff_hz
        },
        "formula_latex": "|H(f)| = \\frac{1}{\\sqrt{1 + (f/f_c)^2}}",
        "steps": [
            f"Given frequency f = {frequency_hz} Hz.",
            f"Given cutoff frequency fc = {cutoff_hz} Hz.",
            f"|H(f)| = 1/sqrt(1 + ({frequency_hz}/{cutoff_hz})²).",
            f"|H(f)| = {magnitude:.6f}.",
            f"Magnitude in dB = 20log10({magnitude:.6f}) = {magnitude_db:.4f} dB."
        ],
        "final_answer": f"|H(f)| = {magnitude:.6f}, {magnitude_db:.4f} dB",
        "wolfram_verification": wolfram_verification_block(wolfram_query) if use_wolfram else None,
        "exam_tip": "For a first-order low-pass filter, at f = fc, the magnitude is 0.707 or -3 dB."
    }


def freeform_calculation_explainer(problem_text: str, use_wolfram: bool = True) -> Dict[str, Any]:
    if not problem_text:
        return {
            "type": "error",
            "message": "Problem text is required."
        }

    wolfram_check = wolfram_verification_block(problem_text) if use_wolfram else None

    prompt = f"""
Solve this Signals & Systems / Communication Engineering numerical problem:

{problem_text}

WolframAlpha verification/context:
{wolfram_check if wolfram_check else "No WolframAlpha verification available."}

Return ONLY valid JSON with this exact structure:

{{
  "type": "calculation",
  "title": "...",
  "given": {{}},
  "formula_latex": "...",
  "steps": ["...", "...", "..."],
  "final_answer": "...",
  "wolfram_verification_summary": "...",
  "exam_tip": "..."
}}

Important:
- Show formulas clearly.
- Show substitutions.
- If information is missing, say what is missing.
- Do not invent missing values.
- Use WolframAlpha only as support if it is relevant.
"""

    result = ask_gemini_json(prompt, temperature=0.4)
    result["wolfram_verification"] = wolfram_check

    return result


if __name__ == "__main__":
    print(shannon_capacity(3000, 20))
    print(am_bandwidth(5000))
    print(rc_lowpass_cutoff(1000, 1e-6))