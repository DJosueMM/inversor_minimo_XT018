import argparse
from pathlib import Path

from analyze_characterization import measurements, print_tables
from first_order_model import read_hspice_2013_transient, vtc, waveform_window


def write_table(path, columns, rows):
    with path.open("w", encoding="ascii") as stream:
        stream.write(" ".join(columns) + "\n")
        for row in rows:
            stream.write(" ".join(f"{value:.12g}" for value in row) + "\n")


def export_tables(results, output):
    output.mkdir(exist_ok=True)
    dc = measurements(results / "characterization_dc.ms0.csv")
    tran = measurements(results / "characterization_tran.mt0.csv")
    tables = print_tables(results / "characterization_dc.lis", "volt")
    sweeps = read_hspice_2013_transient(results / "characterization_tran.tr0")
    if not (len(dc) == len(tran) == len(tables) == len(sweeps)):
        raise ValueError("Inconsistent characterization sweep counts")
    if any(d["ratio"] != t["ratio"] for d, t in zip(dc, tran)):
        raise ValueError("DC and transient ratios are not aligned")
    write_table(output / "barrido.dat", ["ratio", "tphl", "tplh", "tpd", "isc"], [
        (d["ratio"], t["tphl"] * 1e12, t["tplh"] * 1e12,
         t["tpd"] * 1e12, d["isc_peak"] * 1e6)
        for d, t in zip(dc, tran)
    ])
    for ratio, label in ((3.125, "dc"), (2.425, "temporal"), (3.375, "inicial")):
        index = next(i for i, row in enumerate(dc) if row["ratio"] == ratio)
        write_table(output / f"vtc_{label}.dat", ["vin", "spice", "modelo"], [
            (row[1], row[2], vtc(row[1], ratio)) for row in tables[index][1]
        ])
        sweep_ratio, rows = sweeps[index]
        if abs(sweep_ratio - ratio) > 1e-6:
            raise ValueError("Unexpected sweep order")
        vin = waveform_window(rows, 2, 1e-9, 1.9e-9)
        vout = waveform_window(rows, 4, 1e-9, 1.9e-9)
        if len(vin) != len(vout) or any(a[0] != b[0] for a, b in zip(vin, vout)):
            raise ValueError("Transient signals are not aligned")
        write_table(output / f"onda_{label}.dat", ["tiempo", "vin", "vout"], [
            (a[0], a[1], b[1]) for a, b in zip(vin, vout)
        ])
    discharge = print_tables(results / "channel_discharge.lis", "time")
    if len(discharge) != 4:
        raise ValueError("Expected two discharge print tables per capacitance")
    for index, label in enumerate(("1pf", "2pf")):
        values = discharge[2 * index][1]
        pvalues = discharge[2 * index + 1][1]
        if len(values) != len(pvalues) or any(a[0] != b[0] for a, b in zip(values, pvalues)):
            raise ValueError("Discharge print tables are not aligned")
        for kind in ("n", "p"):
            result = []
            for row, prow in zip(values, pvalues):
                voltage = row[1] if kind == "n" else 1.8 - row[2]
                current = row[3] if kind == "n" else -prow[1]
                if row[0] > 0 and .9 <= voltage <= 1.8:
                    if current <= 0:
                        raise ValueError("Invalid discharge current")
                    result.append((voltage, voltage / current / 1e3))
            write_table(output / f"resistencia_{kind}_{label}.dat", ["voltaje", "resistencia"], result)
    print(f"LaTeX figure data: {output}")


def main():
    parser = argparse.ArgumentParser(description="Export verified characterization plot data.")
    parser.add_argument("results", type=Path)
    args = parser.parse_args()
    export_tables(args.results, Path(__file__).resolve().parents[2] / "figuras_latex")


if __name__ == "__main__":
    main()
