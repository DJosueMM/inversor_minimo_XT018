import argparse
import csv
import io
import math
import re
from html import escape
from pathlib import Path
from statistics import fmean

from first_order_model import (
    critical_voltage, crossings, current_per_width, fo1_sizing,
    on_resistance, read_hspice_2013_transient, switching_voltage, vtc, waveform_window,
)

ROOT = Path(__file__).resolve().parents[1]


def measurements(path):
    lines = path.read_text().splitlines()
    reader = csv.DictReader(
        io.StringIO("\n".join(line for line in lines if not line.startswith(("$", ".TITLE"))))
    )
    rows = [{key: float(value) for key, value in row.items()} for row in reader]
    if not rows or any(not math.isfinite(value) for row in rows for value in row.values()):
        raise ValueError(f"Missing or non-finite measurements: {path}")
    return rows


def print_tables(path, axis):
    lines = path.read_text().splitlines()
    tables = []
    for i, line in enumerate(lines):
        if not line.split() or line.split()[0] != axis:
            continue
        columns = lines[i + 1].split()
        data = []
        terminated = False
        for row in lines[i + 2:]:
            if row.strip() == "y":
                terminated = True
                break
            fields = row.split()
            if len(fields) != len(columns) + 1:
                raise ValueError(f"Unexpected print table row in {path}: {row}")
            data.append([float(value) for value in fields])
        if not data or not terminated:
            raise ValueError(f"Empty or truncated print table in {path}")
        if any(not math.isfinite(value) for row in data for value in row):
            raise ValueError(f"Non-finite print table in {path}")
        tables.append((columns, data))
    if not tables:
        raise ValueError(f"No {axis} print tables found in {path}")
    return tables


def svg_plot(path, title, xlabel, ylabel, series):
    width, height = 780, 450
    left, top, plot_width, plot_height = 85, 55, 460, 315
    points = [point for _, values in series for point in values]
    xmin, xmax = min(x for x, _ in points), max(x for x, _ in points)
    ymin, ymax = min(y for _, y in points), max(y for _, y in points)
    if xmax <= xmin or ymax <= ymin:
        raise ValueError(f"Degenerate plot range: {path}")
    pad = (ymax - ymin) * 0.04
    ymin, ymax = ymin - pad, ymax + pad

    def position(x, y):
        return (
            left + (x - xmin) / (xmax - xmin) * plot_width,
            top + (ymax - y) / (ymax - ymin) * plot_height,
        )

    content = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">',
        f"<title>{escape(title)}</title>",
        '<rect width="100%" height="100%" fill="white"/>',
        '<g font-family="sans-serif" font-size="12" fill="#222">',
        f'<text x="{width / 2}" y="25" text-anchor="middle" font-size="17">{escape(title)}</text>',
    ]
    for i in range(6):
        xval = xmin + (xmax - xmin) * i / 5
        yval = ymin + (ymax - ymin) * i / 5
        x, _ = position(xval, ymin)
        _, y = position(xmin, yval)
        content.extend([
            f'<path d="M{x},{top}v{plot_height}" stroke="#ddd"/>',
            f'<path d="M{left},{y}h{plot_width}" stroke="#ddd"/>',
            f'<text x="{x}" y="{top + plot_height + 22}" text-anchor="middle">{xval:.3g}</text>',
            f'<text x="{left - 10}" y="{y + 4}" text-anchor="end">{yval:.3g}</text>',
        ])
    colors = ["#1565c0", "#d32f2f", "#00875a", "#7b1fa2"]
    for i, (label, values) in enumerate(series):
        color = colors[i % len(colors)]
        coords = " ".join(f"{x:.2f},{y:.2f}" for x, y in (position(*p) for p in values))
        content.extend([
            f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2"/>',
            f'<text x="565" y="{70 + 23 * i}" fill="{color}">{escape(label)}</text>',
        ])
    content.extend([
        f'<text x="{left + plot_width / 2}" y="420" text-anchor="middle">{escape(xlabel)}</text>',
        f'<text transform="translate(20,{top + plot_height / 2}) rotate(-90)" '
        f'text-anchor="middle">{escape(ylabel)}</text>',
        "</g></svg>",
    ])
    path.write_text("\n".join(content), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Analyze HSPICE characterization using only Python stdlib.")
    parser.add_argument("results", type=Path, help="Directory containing the three HSPICE runs")
    args = parser.parse_args()
    results = args.results.resolve()
    for name in ("characterization_dc", "characterization_tran", "channel_discharge"):
        text = (results / f"{name}.lis").read_text()
        if re.search(r"\*\*error|job aborted|\bfailed\b", text, re.I):
            raise ValueError(f"Failed simulation: {name}")
        if "job concluded" not in text.lower():
            raise ValueError(f"Missing normal completion: {name}")
        warnings = [line.strip() for line in text.splitlines() if "**warning" in line.lower()]
        for warning in warnings:
            print(f"{name}: {warning}")

    dc = measurements(results / "characterization_dc.ms0.csv")
    tran = measurements(results / "characterization_tran.mt0.csv")
    caps = measurements(results / "channel_discharge.mt0.csv")
    if [r["ratio"] for r in dc] != [r["ratio"] for r in tran]:
        raise ValueError("DC and transient ratio grids differ")
    best_dc = min(dc, key=lambda row: abs(row["vm"] - 0.9))
    best_tran = min(tran, key=lambda row: abs(row["diff"]))
    print(f"DC: {len(dc)} ratios; best sampled ratio={best_dc['ratio']}; VM={best_dc['vm']:.10g} V")
    print(f"Transient: {len(tran)} ratios; best sampled ratio={best_tran['ratio']}; "
          f"asymmetry={best_tran['asym_pct']:.6g}%")

    tables = print_tables(results / "channel_discharge.lis", "time")
    if len(tables) != 2 * len(caps):
        raise ValueError("Expected voltage/NMOS-current and PMOS-current table per capacitor")
    resistance_rows = []
    discharge_series = []
    for cap_index, cap in enumerate(caps):
        columns, values = tables[2 * cap_index]
        pcolumns, pvalues = tables[2 * cap_index + 1]
        if columns != ["dn", "dp", "vsn"] or pcolumns != ["vsp"]:
            raise ValueError("Unexpected discharge print columns")
        if [r[0] for r in values] != [r[0] for r in pvalues]:
            raise ValueError("NMOS and PMOS time grids differ")
        for kind in ("n", "p"):
            samples = []
            for row, prow in zip(values, pvalues):
                time = row[0]
                voltage = row[1] if kind == "n" else 1.8 - row[2]
                current = row[3] if kind == "n" else -prow[1]
                # UIC prints zero source currents at t=0, not a physical on-resistance.
                if time > 0 and 0.9 <= voltage <= 1.8:
                    if current <= 0 or not math.isfinite(current):
                        raise ValueError(f"Invalid current in averaging window: {kind}, {time}")
                    samples.append((time, voltage, voltage / current))
            if len(samples) < 2:
                raise ValueError("Insufficient resistance samples")
            steps = [b[0] - a[0] for a, b in zip(samples, samples[1:])]
            if not all(math.isclose(step, steps[0], rel_tol=1e-6) for step in steps):
                raise ValueError("Arithmetic mean requires a uniform output time grid")
            mean = fmean(r for _, _, r in samples)
            resistance_rows.append({
                "capacitor_F": cap["ctest"], "device": kind,
                "sample_count": len(samples), "time_first_s": samples[0][0],
                "time_last_s": samples[-1][0], "voltage_first_V": samples[0][1],
                "voltage_last_V": samples[-1][1], "mean_V_over_I_ohm": mean,
                "rc_half_time_ohm": cap[f"r{kind}_rc"],
            })
            discharge_series.append((
                f"{kind.upper()} {cap['ctest'] * 1e12:g} pF",
                [(v, r / 1e3) for _, v, r in samples],
            ))
            print(f"{kind.upper()} C={cap['ctest'] * 1e12:g} pF: samples={len(samples)}, "
                  f"mean(V/I)={mean / 1e3:.7g} kohm, "
                  f"R_RC={cap[f'r{kind}_rc'] / 1e3:.7g} kohm")

    output = results / "analisis"
    output.mkdir(exist_ok=True)
    with (output / "resistencias.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(resistance_rows[0]))
        writer.writeheader()
        writer.writerows(resistance_rows)

    cgn = 0.36 * (0.18 * 8.46 + 0.33)
    cgp_per_ratio = 0.36 * (0.18 * 8.91 + 0.32)
    comparison = []
    for d, t in zip(dc, tran):
        ratio = d["ratio"]
        cl = 2 * (cgn + ratio * cgp_per_ratio) * 1e-15
        comparison.append({
            "ratio": ratio, "wp_um": 0.36 * ratio, "vm_V": d["vm"],
            "isc_peak_A": d["isc_peak"], "tphl_s": t["tphl"],
            "tplh_s": t["tplh"], "tpd_s": t["tpd"], "asym_pct": t["asym_pct"],
            "CL_first_order_F": cl,
            "Rn_delay_ohm": t["tphl"] / (math.log(2) * cl),
            "Rp_delay_actual_width_ohm": t["tplh"] / (math.log(2) * cl),
            "Rp_delay_normalized_036um_ohm": ratio * t["tplh"] / (math.log(2) * cl),
        })
    with (output / "comparacion.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(comparison[0]))
        writer.writeheader()
        writer.writerows(comparison)
    for ratio in (2, best_tran["ratio"], best_dc["ratio"], 3.375):
        print(next(row for row in comparison if row["ratio"] == ratio))

    iterations = []
    current = next(row for row in comparison if row["ratio"] == 2)
    for step in range(10):
        prediction = current["Rp_delay_normalized_036um_ohm"] / current["Rn_delay_ohm"]
        if not comparison[0]["ratio"] <= prediction <= comparison[-1]["ratio"]:
            raise ValueError("Iteration predicts a ratio outside the simulated sweep")
        following = min(comparison, key=lambda row: abs(row["ratio"] - prediction))
        iterations.append({
            "step": step, "ratio": current["ratio"],
            "CL_F": current["CL_first_order_F"], "Rn_ohm": current["Rn_delay_ohm"],
            "Rp_normalized_036um_ohm": current["Rp_delay_normalized_036um_ohm"],
            "predicted_ratio": prediction, "next_sampled_ratio": following["ratio"],
        })
        if following["ratio"] == current["ratio"]:
            break
        current = following
    else:
        raise ValueError("Width iteration did not converge within 10 steps")
    with (output / "iteracion.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(iterations[0]))
        writer.writeheader()
        writer.writerows(iterations)
    for row in iterations:
        print("Iteration:", row)

    figures = ROOT / "Imagenes"
    selected = (best_dc["ratio"], best_tran["ratio"], 3.375)
    vtc_tables = print_tables(results / "characterization_dc.lis", "volt")
    if len(vtc_tables) != len(dc):
        raise ValueError("Expected one VTC table per DC ratio")
    vtc_series = []
    for ratio in selected:
        index = next(i for i, row in enumerate(dc) if row["ratio"] == ratio)
        columns, values = vtc_tables[index]
        if columns != ["in", "out", "vdrv"]:
            raise ValueError(f"Unexpected VTC columns: {columns}")
        vtc_series.append((f"P/N={ratio:g}", [(row[1], row[2]) for row in values]))
    vtc_series.append(("Vin=Vout", [(0, 0), (1.8, 1.8)]))
    svg_plot(figures / "caracterizacion_vtc.svg", "VTC SPICE: carga FO1, tm, 70 C",
             "Vin (V)", "Vout (V)", vtc_series)
    svg_plot(figures / "caracterizacion_retardos.svg", "Retardos SPICE: FO1, flancos de 1 ps",
             "Relacion WP/WN", "Retardo (ps)", [
                 ("tpHL", [(r["ratio"], r["tphl"] * 1e12) for r in tran]),
                 ("tpLH", [(r["ratio"], r["tplh"] * 1e12) for r in tran]),
                 ("tpd", [(r["ratio"], r["tpd"] * 1e12) for r in tran]),
             ])
    svg_plot(figures / "caracterizacion_isc.svg", "Pico DC aislado del inversor bajo prueba",
             "Relacion WP/WN", "Corriente (microamperios)",
             [("Isc pico DC", [(r["ratio"], r["isc_peak"] * 1e6) for r in dc])])
    svg_plot(figures / "caracterizacion_resistencias.svg", "Resistencia durante descarga/carga",
             "VDS NMOS / VSD PMOS (V)", "V/I (kohm)", discharge_series)
    model_rows = []
    model_ratios = (best_dc["ratio"], best_tran["ratio"], 3.375)
    for ratio in model_ratios:
        index = next(i for i, row in enumerate(dc) if row["ratio"] == ratio)
        values = vtc_tables[index][1]
        prediction = [(row[1], vtc(row[1], ratio)) for row in values]
        rmse = math.sqrt(fmean((row[2] - pred[1]) ** 2 for row, pred in zip(values, prediction)))
        model_rows.append({
            "ratio": ratio, "VM_model_V": switching_voltage(ratio),
            "VM_spice_V": dc[index]["vm"], "VTC_RMSE_V": rmse,
        })
        svg_plot(figures / f"modelo_vtc_{ratio:g}.svg",
                 f"VTC analitica vs SPICE: P/N={ratio:g}", "Vin (V)", "Vout (V)", [
                     ("SPICE", [(row[1], row[2]) for row in values]),
                     ("Modelo primer orden", prediction),
                     ("Vin=Vout", [(0, 0), (1.8, 1.8)]),
                 ])
    with (output / "modelo_vtc.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(model_rows[0]))
        writer.writeheader()
        writer.writerows(model_rows)
    print("Critical voltages N/P:", critical_voltage("n"), critical_voltage("p"))
    print("Centered ratio, extended model:",
          current_per_width("n", .9, .9) / current_per_width("p", .9, .9))
    for row in model_rows:
        print("VTC comparison:", row)
    rn, rp = on_resistance("n"), on_resistance("p")
    print("Independent model Rn/Rp ohm and symmetric ratio:", rn, rp, rp / rn)
    load_constant = 2 * cgn * 1e-15
    load_slope = 2 * cgp_per_ratio * 1e-15
    print("Rabaey FO1 sizing, independent model:",
          fo1_sizing(rn, rp, load_constant, load_slope))
    for row in comparison:
        if row["ratio"] in (2.0, best_tran["ratio"]):
            print("Rabaey FO1 sizing, delay extraction at ratio", row["ratio"],
                  fo1_sizing(row["Rn_delay_ohm"], row["Rp_delay_normalized_036um_ohm"],
                             load_constant, load_slope))
    for ratio in (2.425, 3.125, rp / rn):
        load = 2 * (cgn + ratio * cgp_per_ratio) * 1e-15
        print("Independent model delays ps:", ratio, math.log(2) * load * rn * 1e12,
              math.log(2) * load * rp / ratio * 1e12)

    sweeps = read_hspice_2013_transient(results / "characterization_tran.tr0")
    if len(sweeps) != len(tran):
        raise ValueError("Binary waveform sweep count differs from measurements")
    waveform_rows = []
    for (ratio, rows), measured in zip(sweeps, tran):
        if not math.isclose(ratio, measured["ratio"], abs_tol=1e-6):
            raise ValueError("Waveform ratio order differs from measurement table")
        # TIME, ground, input, load_out, output, supplies, source currents.
        delay_hl = crossings(rows, 4, False)[1] - crossings(rows, 2, True)[1]
        delay_lh = crossings(rows, 4, True)[1] - crossings(rows, 2, False)[1]
        # Stored waveforms are adaptive/compressed, not the measurement solver grid.
        if max(abs(delay_hl - measured["tphl"]), abs(delay_lh - measured["tplh"])) > 1e-12:
            raise ValueError(f"Waveform delay disagrees with measures by >1 ps: ratio={ratio}")
        waveform_rows.append({
            "ratio": measured["ratio"], "tphl_from_wave_s": delay_hl,
            "tplh_from_wave_s": delay_lh, "tphl_measure_s": measured["tphl"],
            "tplh_measure_s": measured["tplh"],
        })
    with (output / "verificacion_ondas.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(waveform_rows[0]))
        writer.writeheader()
        writer.writerows(waveform_rows)
    for target in (best_dc["ratio"], best_tran["ratio"]):
        _, rows = min(sweeps, key=lambda sweep: abs(sweep[0] - target))
        svg_plot(figures / f"transitorio_{target:g}.svg",
                 f"Transitorio SPICE FO1: P/N={target:g}", "Tiempo (ps)", "Tension (V)", [
                     ("Vin", waveform_window(rows, 2, 1e-9, 1.9e-9)),
                     ("Vout", waveform_window(rows, 4, 1e-9, 1.9e-9)),
                 ])
    print(f"Verified binary waveform delays against measures for {len(sweeps)} ratios")
    print(f"Tables: {output}")
    print(f"Figures: {figures}")


if __name__ == "__main__":
    main()
