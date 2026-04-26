"""
knowledge_router.py

Unified router for SigmaTutor Person C Knowledge Tools.

Person A can integrate this file into agent.py or main.py.

Main function:
route_knowledge_tool(...)
"""

from typing import Dict, Any
from backend.tools.concept_explainer import explain_concept
from backend.tools.exam_gen import generate_exam
from backend.tools.prover import prove_formula
from backend.tools.calculator import (
    nyquist_rate,
    sampling_interval,
    shannon_capacity,
    snr_db_to_linear,
    snr_linear_to_db,
    period_from_frequency,
    frequency_from_period,
    frequency_from_angular_frequency,
    angular_frequency_from_frequency,
    wavelength,
    am_modulation_index,
    am_bandwidth,
    dsb_sc_bandwidth,
    ssb_bandwidth,
    bit_rate,
    noise_power_watts,
    thermal_noise_dbm,
    signal_power_from_vrms,
    rc_lowpass_cutoff,
    first_order_lpf_magnitude,
    freeform_calculation_explainer
)


def route_knowledge_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    if not tool_name:
        return {
            "type": "error",
            "message": "tool_name is required."
        }

    tool_name = tool_name.lower().strip()

    if tool_name == "concept":
        return explain_concept(
            topic=kwargs.get("topic"),
            level=kwargs.get("level", "beginner"),
            course_context=kwargs.get("course_context")
        )

    if tool_name == "exam":
        return generate_exam(
            topic=kwargs.get("topic"),
            difficulty=kwargs.get("difficulty", "medium"),
            num_questions=kwargs.get("num_questions", 5),
            question_type=kwargs.get("question_type", "mixed"),
            course_context=kwargs.get("course_context")
        )

    if tool_name == "proof":
        return prove_formula(
            formula_or_theorem=kwargs.get("formula_or_theorem"),
            level=kwargs.get("level", "intermediate"),
            course_context=kwargs.get("course_context"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "nyquist_rate":
        return nyquist_rate(
            max_frequency_hz=kwargs.get("max_frequency_hz"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "sampling_interval":
        return sampling_interval(
            sampling_frequency_hz=kwargs.get("sampling_frequency_hz"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "shannon_capacity":
        return shannon_capacity(
            bandwidth_hz=kwargs.get("bandwidth_hz"),
            snr_db=kwargs.get("snr_db"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "snr_db_to_linear":
        return snr_db_to_linear(
            snr_db=kwargs.get("snr_db"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "snr_linear_to_db":
        return snr_linear_to_db(
            snr_linear=kwargs.get("snr_linear"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "period":
        return period_from_frequency(
            frequency_hz=kwargs.get("frequency_hz"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "frequency_from_period":
        return frequency_from_period(
            period_seconds=kwargs.get("period_seconds"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "frequency_from_angular_frequency":
        return frequency_from_angular_frequency(
            omega_rad_per_sec=kwargs.get("omega_rad_per_sec"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "angular_frequency_from_frequency":
        return angular_frequency_from_frequency(
            frequency_hz=kwargs.get("frequency_hz"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "wavelength":
        return wavelength(
            speed_m_per_s=kwargs.get("speed_m_per_s"),
            frequency_hz=kwargs.get("frequency_hz"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "am_modulation_index":
        return am_modulation_index(
            message_amplitude=kwargs.get("message_amplitude"),
            carrier_amplitude=kwargs.get("carrier_amplitude"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "am_bandwidth":
        return am_bandwidth(
            max_message_frequency_hz=kwargs.get("max_message_frequency_hz"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "dsb_sc_bandwidth":
        return dsb_sc_bandwidth(
            max_message_frequency_hz=kwargs.get("max_message_frequency_hz"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "ssb_bandwidth":
        return ssb_bandwidth(
            max_message_frequency_hz=kwargs.get("max_message_frequency_hz"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "bit_rate":
        return bit_rate(
            bits_per_symbol=kwargs.get("bits_per_symbol"),
            symbol_rate_baud=kwargs.get("symbol_rate_baud"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "noise_power_watts":
        return noise_power_watts(
            bandwidth_hz=kwargs.get("bandwidth_hz"),
            temperature_k=kwargs.get("temperature_k", 290),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "thermal_noise_dbm":
        return thermal_noise_dbm(
            bandwidth_hz=kwargs.get("bandwidth_hz"),
            noise_figure_db=kwargs.get("noise_figure_db", 0),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "signal_power_from_vrms":
        return signal_power_from_vrms(
            vrms=kwargs.get("vrms"),
            resistance_ohms=kwargs.get("resistance_ohms"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "rc_lowpass_cutoff":
        return rc_lowpass_cutoff(
            resistance_ohms=kwargs.get("resistance_ohms"),
            capacitance_farads=kwargs.get("capacitance_farads"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "first_order_lpf_magnitude":
        return first_order_lpf_magnitude(
            frequency_hz=kwargs.get("frequency_hz"),
            cutoff_hz=kwargs.get("cutoff_hz"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    if tool_name == "freeform_calculation":
        return freeform_calculation_explainer(
            problem_text=kwargs.get("problem_text"),
            use_wolfram=kwargs.get("use_wolfram", True)
        )

    return {
        "type": "error",
        "message": f"Unknown knowledge tool: {tool_name}"
    }


if __name__ == "__main__":
    print(route_knowledge_tool("shannon_capacity", bandwidth_hz=3000, snr_db=20))