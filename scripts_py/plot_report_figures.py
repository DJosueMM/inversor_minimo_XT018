import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
from matplotlib.ticker import FuncFormatter, MaxNLocator

from export_latex_figures import export_tables
from first_order_model import crossings, switching_voltage


BLUE, RED, GREEN = "#0072B2", "#D55E00", "#009E73"
PREFIXES = {-12: "p", -9: "n", -6: "\N{MICRO SIGN}", -3: "m", 0: "", 3: "k"}


def engineering_axis(ax, which, quantity, unit, exponent=0):
    """Keep SI data internally and use one explicit engineering prefix per axis."""
    prefix = PREFIXES[exponent]
    axis = ax.xaxis if which == "x" else ax.yaxis
    axis.set_major_formatter(FuncFormatter(lambda value, _: f"{value / 10**exponent:g}"))
    axis.set_major_locator(MaxNLocator(nbins=5))
    label = f"{quantity} ({prefix}{unit})"
    if which == "x":
        ax.set_xlabel(label)
    else:
        ax.set_ylabel(label)


def style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.labelsize": 9,
        "axes.titlesize": 9,
        "axes.linewidth": .7,
        "axes.grid": True,
        "grid.alpha": .25,
        "grid.linewidth": .5,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 7.5,
        "legend.frameon": False,
        "lines.linewidth": 1.4,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
        "savefig.facecolor": "white",
    })


def canvas(height=2.9):
    return plt.subplots(figsize=(3.5, height), layout="constrained")


def legend(ax, columns=2):
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.01, 1, .2),
              mode="expand", borderaxespad=0, ncol=columns, handlelength=2.5)


def save(fig, output, name, dpi):
    fig.canvas.draw()
    if not all(np.isfinite(ax.get_xlim() + ax.get_ylim()).all() for ax in fig.axes):
        raise ValueError(f"Nonfinite axes in {name}")
    for suffix in ("pdf", "svg", "png"):
        fig.savefig(output / f"{name}.{suffix}", dpi=dpi)
    plt.close(fig)


def table(output, name):
    data = np.genfromtxt(output / f"{name}.dat", names=True)
    if data.size < 2 or not all(np.isfinite(data[key]).all() for key in data.dtype.names):
        raise ValueError(f"Invalid plotting data: {name}")
    return data


def voltage_axes(ax):
    engineering_axis(ax, "x", r"Entrada, $V_{\mathrm{in}}$", "V")
    engineering_axis(ax, "y", r"Salida, $V_{\mathrm{out}}$", "V")
    ax.set(xlim=(0, 1.8), ylim=(-.05, 1.85),
           xticks=np.linspace(0, 1.8, 7), yticks=np.linspace(0, 1.8, 5))


def transfer_plots(output, dpi):
    for label, ratio in (("dc", 3.125), ("temporal", 2.425), ("inicial", 3.375)):
        data = table(output, f"vtc_{label}")
        fig, ax = canvas()
        ax.plot(data["vin"], data["spice"], color=BLUE, label="HSPICE")
        ax.plot(data["vin"], data["modelo"], "--", color=RED, label="Primer orden")
        ax.plot([0, 1.8], [0, 1.8], ":", color=".5", linewidth=.9)
        vm_model = switching_voltage(ratio)
        delta = data["spice"] - data["vin"]
        i = np.flatnonzero(delta[:-1] * delta[1:] <= 0)[0]
        vm_spice = data["vin"][i] - delta[i] * (
            data["vin"][i + 1] - data["vin"][i]) / (delta[i + 1] - delta[i])
        ax.plot(vm_spice, vm_spice, "o", color=BLUE, markersize=4)
        ax.plot(vm_model, vm_model, "s", color=RED, markersize=4)
        ax.text(.04, .08, f"$r={ratio:g}$\n"
                f"$V_M$ SPICE = {vm_spice:.4f} V\n"
                f"$V_M$ modelo = {vm_model:.4f} V",
                transform=ax.transAxes, fontsize=8,
                bbox={"facecolor": "white", "edgecolor": ".85", "alpha": .95})
        voltage_axes(ax)
        legend(ax)
        save(fig, output, f"modelo_vtc_{label}", dpi)

    fig, ax = canvas()
    for label, ratio, color, line in (
            ("dc", 3.125, BLUE, "-"), ("temporal", 2.425, RED, "--")):
        data = table(output, f"vtc_{label}")
        ax.plot(data["vin"], data["spice"], line, color=color, label=f"$r={ratio:g}$")
    voltage_axes(ax)
    legend(ax)
    save(fig, output, "vtc_comparacion", dpi)


def sweep_plots(output, dpi):
    data = table(output, "barrido")
    fig, ax = canvas()
    for key, name, color, line in (
            ("tphl", "$t_{HL}$", BLUE, "-"),
            ("tplh", "$t_{LH}$", RED, "--"),
            ("tpd", "$t_{pd}$", GREEN, "-.")):
        ax.plot(data["ratio"], data[key] * 1e-12, line, color=color, label=name)
    ax.axvline(2.425, color=".4", linestyle=":", linewidth=1)
    ax.text(2.47, 19.5e-12, "$r=2.425$", fontsize=8)
    ax.set_xlabel(r"Relación de anchos, $r=W_P/W_N$ (1)")
    engineering_axis(ax, "y", "Retardo de propagación", "s", -12)
    ax.set_xlim(1.5, 4)
    legend(ax, 3)
    save(fig, output, "retardos", dpi)

    fig, ax = canvas()
    ax.plot(data["ratio"], data["isc"] * 1e-6, color=BLUE)
    for ratio, color, position in ((2.425, RED, (.08, .82)), (3.125, GREEN, (.58, .25))):
        row = data[np.flatnonzero(np.isclose(data["ratio"], ratio))[0]]
        current = float(row["isc"]) * 1e-6
        ax.plot(ratio, current, "o", color=color, markersize=4)
        ax.annotate(f"$r={ratio:g}$\n{current * 1e6:.2f} \N{MICRO SIGN}A",
                    (ratio, current), xytext=position, textcoords="axes fraction",
                    fontsize=8, bbox={"facecolor": "white", "edgecolor": ".85"},
                    arrowprops={"arrowstyle": "-", "color": color, "lw": .8})
    ax.set_xlabel(r"Relación de anchos, $r=W_P/W_N$ (1)")
    engineering_axis(ax, "y", r"Corriente pico DC, $I_{\mathrm{sc}}$", "A", -6)
    ax.set_xlim(1.5, 4)
    save(fig, output, "corriente_pico", dpi)


def transient_plot(output, label, ratio, dpi):
    data = table(output, f"onda_{label}")
    time = data["tiempo"] * 1e-12
    rows = list(zip(time, data["vin"], data["vout"]))
    fig = plt.figure(figsize=(7.16, 3.9), layout="constrained")
    grid = fig.add_gridspec(2, 2, height_ratios=(1, 1.2))
    overview = fig.add_subplot(grid[0, :])
    overview.plot(time, data["vin"], color=BLUE, label="Entrada")
    overview.plot(time, data["vout"], "--", color=RED, label="Salida")
    engineering_axis(overview, "x", "Tiempo absoluto, t", "s", -9)
    engineering_axis(overview, "y", "Tensión", "V")
    overview.set_xlim(time[0], time[-1])
    overview.set_title(f"FO1; $r={ratio:g}$; $V_{{DD}}=1.8$ V; 70 \N{DEGREE SIGN}C",
                       loc="left")
    overview.legend(loc="upper right", ncol=2)
    limits = min(data["vin"].min(), data["vout"].min()) - .08, max(
        data["vin"].max(), data["vout"].max()) + .08
    overview.set_ylim(*limits)
    for index, (rising, name) in enumerate(((True, "HL"), (False, "LH"))):
        edge = crossings(rows, 1, rising)[0]
        output_edge = crossings(rows, 2, not rising)[0]
        delay = output_edge - edge
        if delay <= 0:
            raise ValueError("Nonpositive propagation delay")
        ax = fig.add_subplot(grid[1, index])
        ax.plot(time - edge, data["vin"], color=BLUE)
        ax.plot(time - edge, data["vout"], "--", color=RED)
        ax.axhline(.9, color=".5", linewidth=.7, linestyle=":")
        for x in (0, delay):
            ax.axvline(x, color=".5", linewidth=.7, linestyle=":")
        ax.annotate("", (0, .9), (delay, .9),
                    arrowprops={"arrowstyle": "<->", "color": ".15", "lw": 1})
        ax.set_title(f"$t_{{{name}}}={delay * 1e12:.3f}$ ps", loc="left")
        engineering_axis(ax, "x", r"Tiempo desde cruce de entrada, $\Delta t$", "s", -12)
        engineering_axis(ax, "y", "Tensión", "V")
        ax.set(xlim=(-10e-12, delay + 30e-12), ylim=limits)
    save(fig, output, f"transitorio_{label}", dpi)


def resistance_plot(output, dpi):
    fig, axes = plt.subplots(2, 1, figsize=(3.5, 4.2), layout="constrained", sharex=True)
    for ax, kind, color in zip(axes, ("n", "p"), (BLUE, RED)):
        for cap, line, marker in (("1pf", "-", None), ("2pf", "--", "o")):
            data = table(output, f"resistencia_{kind}_{cap}")
            ax.plot(data["voltaje"], data["resistencia"] * 1e3, line, color=color,
                    marker=marker, markersize=2.5, markevery=max(1, len(data) // 8),
                    label=cap.replace("pf", " pF"))
        ax.set_title("NMOS" if kind == "n" else "PMOS", loc="left")
        engineering_axis(ax, "y", r"Resistencia, $V/I$", "\N{GREEK CAPITAL LETTER OMEGA}", 3)
        ax.legend(loc="upper left", ncol=2)
        ax.set_xlim(.9, 1.8)
    engineering_axis(axes[-1], "x", r"Tensión de canal, $V_{DS}$ o $V_{SD}$", "V")
    axes[-1].set_xticks([.9, 1.2, 1.5, 1.8])
    save(fig, output, "resistencias", dpi)


def schematic(output, dpi):
    fig, ax = plt.subplots(figsize=(3.5, 3.1), layout="constrained")
    ax.set(xlim=(0, 5), ylim=(-.4, 5.5), aspect="equal")
    ax.axis("off")
    wire = {"color": ".15", "linewidth": 1.2}
    for low, high in ((3, 4), (1, 2)):
        ax.plot([2.35, 2.35], [low, high], **wire)
        ax.plot([2.65, 2.65], [low, high], **wire)
        ax.plot([2.65, 3, 3], [high, high, high + .8], **wire)
        ax.plot([2.65, 3, 3], [low, low, low - .8], **wire)
    ax.plot([3, 3], [2, 3], **wire)
    ax.plot([.5, 1.3, 1.3], [2.5, 2.5, 3.5], **wire)
    ax.plot([1.3, 1.3, 2.35], [2.5, 1.5, 1.5], **wire)
    ax.plot([1.3, 2.05], [3.5, 3.5], **wire)
    ax.add_patch(Circle((2.2, 3.5), .15, fill=False, **wire))
    ax.plot([3, 4.5], [2.5, 2.5], **wire)
    ax.plot([2.5, 3.5], [4.8, 4.8], **wire)
    for width, y in ((.8, .2), (.5, .05), (.2, -.1)):
        ax.plot([3 - width / 2, 3 + width / 2], [y, y], **wire)
    for x, y in ((1.3, 2.5), (3, 2.5)):
        ax.plot(x, y, "o", color=".15", markersize=3)
    ax.text(3, 5, "$V_{DD}=1.8$ V", ha="center")
    ax.text(.5, 2.7, "$V_{in}$", ha="center")
    ax.text(4.5, 2.7, "$V_{out}$", ha="center")
    ax.text(3.25, 3.4, "PMOS\n$W_P=r W_N$", fontsize=8, va="center")
    ax.text(3.25, 1.4, "NMOS\n$W_N=360$ nm", fontsize=8, va="center")
    ax.text(.3, .25, "$L_N=L_P=180$ nm", fontsize=8)
    save(fig, output, "esquema_inversor", dpi)


def main():
    parser = argparse.ArgumentParser(description="Generate report figures: vector PDF/SVG and 600 dpi PNG.")
    parser.add_argument("results", type=Path)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).resolve().parents[2] / "figuras_latex")
    parser.add_argument("--dpi", type=int, default=600)
    args = parser.parse_args()
    if args.dpi < 300:
        parser.error("--dpi must be at least 300 for print-quality figures")
    export_tables(args.results, args.output)
    style()
    schematic(args.output, args.dpi)
    transfer_plots(args.output, args.dpi)
    sweep_plots(args.output, args.dpi)
    for label, ratio in (("dc", 3.125), ("temporal", 2.425)):
        transient_plot(args.output, label, ratio, args.dpi)
    resistance_plot(args.output, args.dpi)
    print(f"Generated 10 figures in PDF, SVG and PNG ({args.dpi} dpi): {args.output}")


if __name__ == "__main__":
    main()
