import math


SUPPLY = 1.8
LENGTH_UM = .18
WIDTH_N_UM = .36
DIFFUSION_LENGTH_UM = .45
EPSILON_0 = 8.8541878128e-12

# Typical XT018 values transcribed from the model excerpts supplied by the user.
# Units: oxide thickness (m), overlap (F/m), bottom junction (F/m^2),
# STI/gate-edge junctions (F/m), built-in voltages (V), grading exponents (1).
MODEL = {
    "n": {
        "toxe": 4.1e-9, "overlap": 2.284e-10,
        "cj": 1.273e-3, "cjsw": 3.453e-10, "cjswg": 4.764e-10,
        "pb": 1.030, "pbsw": .7386, "pbswg": .5794,
        "mj": .4816, "mjsw": .2456, "mjswg": .211,
    },
    "p": {
        "toxe": 3.9e-9, "overlap": 1.674e-10,
        "cj": 9.831e-4, "cjsw": 2.124e-10, "cjswg": 7.971e-10,
        "pb": .9294, "pbsw": 1.121, "pbswg": .7990,
        "mj": .4277, "mjsw": .08658, "mjswg": .4054,
    },
}


def positive(value, name):
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")


def junction_factor(potential, grading, low=SUPPLY / 2, high=SUPPLY):
    """Charge-equivalent average of (1+V/PB)^(-M) over a reverse-bias interval."""
    positive(potential, "junction potential")
    if not (math.isfinite(grading) and math.isfinite(low) and math.isfinite(high)
            and 0 <= low < high):
        raise ValueError("Invalid reverse-bias interval or grading exponent")
    if grading == 1:
        integral = potential * math.log((potential + high) / (potential + low))
    else:
        power = 1 - grading
        integral = potential / power * (
            (1 + high / potential)**power - (1 + low / potential)**power
        )
    return integral / (high - low)


def capacitances(kind, width_um):
    """Drawn-geometry, first-order capacitances; all returned capacitances in F."""
    positive(width_um, "drawn width")
    model = MODEL[kind]
    width = width_um * 1e-6
    length = LENGTH_UM * 1e-6
    area = width * DIFFUSION_LENGTH_UM * 1e-6
    perimeter = 2 * (width + DIFFUSION_LENGTH_UM * 1e-6)
    gate_edge = width
    sti_edge = perimeter - gate_edge
    cox = EPSILON_0 * 3.9 / model["toxe"]
    channel = width * length * cox
    overlap = width * model["overlap"]
    bottom = area * model["cj"] * junction_factor(model["pb"], model["mj"])
    side = sti_edge * model["cjsw"] * junction_factor(model["pbsw"], model["mjsw"])
    gate_junction = gate_edge * model["cjswg"] * junction_factor(
        model["pbswg"], model["mjswg"]
    )
    junction = bottom + side + gate_junction
    return {
        "width_um": width_um, "area_m2": area, "perimeter_m": perimeter,
        "cox_F_m2": cox, "channel_F": channel, "overlap_each_F": overlap,
        "gate_input_F": channel + 2 * overlap,
        "junction_bottom_F": bottom, "junction_sti_F": side,
        "junction_gate_edge_F": gate_junction, "junction_F": junction,
        "intrinsic_output_F": junction + 2 * overlap,
    }


def inverter_capacitances(ratio):
    positive(ratio, "PMOS/NMOS width ratio")
    n = capacitances("n", WIDTH_N_UM)
    p = capacitances("p", WIDTH_N_UM * ratio)
    gate = n["gate_input_F"] + p["gate_input_F"]
    intrinsic = n["intrinsic_output_F"] + p["intrinsic_output_F"]
    return {"n": n, "p": p, "gate_F": gate, "intrinsic_F": intrinsic,
            "fo1_load_F": gate + intrinsic}


def delay_resistances(row):
    ratio = row["ratio_used"]
    caps = inverter_capacitances(ratio)
    delta_hl = row["tphl4"] - row["tphl3"]
    delta_lh = row["tplh4"] - row["tplh3"]
    positive(delta_hl, "FO4-FO3 falling delay")
    positive(delta_lh, "FO4-FO3 rising delay")
    for key in ("tphl3", "tphl4", "tplh3", "tplh4",
                "tin_r", "tin_f", "tr3", "tf3", "tr4", "tf4"):
        positive(row[key], key)
    rn = delta_hl / (math.log(2) * caps["gate_F"])
    rp_actual = delta_lh / (math.log(2) * caps["gate_F"])
    rp_ref = ratio * rp_actual
    next_ratio = rp_ref / rn
    next_caps = inverter_capacitances(next_ratio)
    return {
        "ratio": ratio, "gate_F": caps["gate_F"],
        "intrinsic_F": caps["intrinsic_F"],
        "Rn_RC_ohm": rn, "Rp_RC_actual_ohm": rp_actual,
        "Rp_RC_ref_ohm": rp_ref,
        "Rn_Weste_ohm": math.log(2) * rn,
        "Rp_Weste_ref_ohm": math.log(2) * rp_ref,
        "proposed_ratio": next_ratio, "proposed_wp_um": next_ratio * WIDTH_N_UM,
        "predicted_tphl_at_measured_ratio_s": math.log(2) * rn * caps["fo1_load_F"],
        "predicted_tplh_at_measured_ratio_s": math.log(2) * rp_actual * caps["fo1_load_F"],
        "predicted_symmetric_delay_s": math.log(2) * rn * next_caps["fo1_load_F"],
        "input_rise_s": row["tin_r"], "input_fall_s": row["tin_f"],
        "fo3_rise_s": row["tr3"], "fo3_fall_s": row["tf3"],
        "fo4_rise_s": row["tr4"], "fo4_fall_s": row["tf4"],
        "fo3_fall_to_input_rise": row["tf3"] / row["tin_r"],
        "fo3_rise_to_input_fall": row["tr3"] / row["tin_f"],
        "fo4_fall_to_input_rise": row["tf4"] / row["tin_r"],
        "fo4_rise_to_input_fall": row["tr4"] / row["tin_f"],
    }
