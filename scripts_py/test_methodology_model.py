import contextlib
import io
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import complete_methodology
from methodology_model import (
    MODEL, capacitances, delay_resistances, inverter_capacitances, junction_factor,
)


def fixture_row():
    gate = inverter_capacitances(2)["gate_F"]
    return {
        "ratio_used": 2.,
        "tphl3": 40e-12, "tphl4": 40e-12 + math.log(2) * 7000 * gate,
        "tplh3": 42e-12, "tplh4": 42e-12 + math.log(2) * 8000 * gate,
        "tin_r": 30e-12, "tin_f": 31e-12,
        "tr3": 32e-12, "tf3": 33e-12, "tr4": 40e-12, "tf4": 41e-12,
    }


class MethodologyTests(unittest.TestCase):
    def test_junction_average_matches_numerical_integration(self):
        steps = 10000
        low, high = .9, 1.8
        for model in MODEL.values():
            for pb, grading in (("pb", "mj"), ("pbsw", "mjsw"), ("pbswg", "mjswg")):
                potential, exponent = model[pb], model[grading]
                values = [(1 + (low + (high - low) * i / steps) / potential)**(-exponent)
                          for i in range(steps + 1)]
                average = (sum(values) - .5 * (values[0] + values[-1])) / steps
                self.assertAlmostEqual(junction_factor(potential, exponent), average, places=9)
        self.assertAlmostEqual(junction_factor(1, 0), 1)
        self.assertGreater(junction_factor(1, 1), 0)

    def test_gate_includes_both_overlaps_and_units(self):
        cap = capacitances("n", .36)
        self.assertAlmostEqual(cap["area_m2"] / 1e-12, .162)
        self.assertAlmostEqual(cap["perimeter_m"] / 1e-6, 1.62)
        self.assertAlmostEqual(cap["overlap_each_F"] / 1e-15, .082224)
        self.assertAlmostEqual(cap["gate_input_F"],
                               cap["channel_F"] + 2 * cap["overlap_each_F"], places=28)
        self.assertAlmostEqual(cap["intrinsic_output_F"],
                               cap["junction_F"] + 2 * cap["overlap_each_F"], places=28)

    def test_initial_capacitance_totals_and_scaling(self):
        cap = inverter_capacitances(2)
        self.assertAlmostEqual(cap["fo1_load_F"] * 1e15, 4.039179401003365)
        self.assertAlmostEqual(cap["gate_F"] * 1e15, 2.0987702390878594)
        self.assertAlmostEqual(cap["intrinsic_F"] * 1e15, 1.940409161915506)
        self.assertAlmostEqual(capacitances("p", .72)["gate_input_F"],
                               2 * capacitances("p", .36)["gate_input_F"], places=28)
        # Fixed diffusion endwalls are retained, not scaled as gate area.
        self.assertGreater(2 * capacitances("p", .36)["junction_F"],
                           capacitances("p", .72)["junction_F"])

    def test_fanout_difference_recovers_resistance_and_convention(self):
        result = delay_resistances(fixture_row())
        self.assertAlmostEqual(result["Rn_RC_ohm"], 7000)
        self.assertAlmostEqual(result["Rp_RC_actual_ohm"], 8000)
        self.assertAlmostEqual(result["Rp_RC_ref_ohm"], 16000)
        self.assertAlmostEqual(result["proposed_ratio"], 16000 / 7000)
        self.assertAlmostEqual(result["Rn_Weste_ohm"], 7000 * math.log(2))
        self.assertAlmostEqual(result["fo4_fall_to_input_rise"], 41 / 30)

    def test_invalid_inputs_are_explicit_errors(self):
        for value in (0, -1, float("inf"), float("nan")):
            with self.assertRaises(ValueError):
                inverter_capacitances(value)
        row = fixture_row()
        row["tphl4"] = row["tphl3"]
        with self.assertRaises(ValueError):
            delay_resistances(row)
        row = fixture_row()
        row["tin_r"] = 0
        with self.assertRaises(ValueError):
            delay_resistances(row)

    def test_prepare_archives_numeric_dc_sizes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "spice_decks").mkdir()
            with patch.object(complete_methodology, "ROOT", root), contextlib.redirect_stdout(io.StringIO()):
                complete_methodology.prepare(2)
            content = (root / "spice_decks" / "methodology_sizes.inc").read_bytes()
            self.assertNotIn(b"\r", content)
            self.assertIn(b".param RATIO=2\n", content)
            rows = content.decode().split(".data dc_ratios RATIO\n")[1].split(".enddata")[0].split()
            self.assertEqual(len(rows), 2)
            self.assertAlmostEqual(float(rows[0]), complete_methodology.centered_ratio())
            self.assertEqual(float(rows[1]), 2)

    def test_analyzer_fixture_end_to_end_and_stale_parameters(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "methodology_sizes.inc").write_text(".param RATIO=2\n")
            for name in ("methodology_dc", "methodology_fanout", "methodology_fo1"):
                (root / f"{name}.lis").write_text("job concluded\n")
            complete_methodology.write_rows(root / "methodology_fanout.mt0.csv", [fixture_row()])
            complete_methodology.write_rows(root / "methodology_dc.ms0.csv", [
                {"ratio_used": complete_methodology.centered_ratio(), "vm": .9, "isc_peak": 1e-5},
                {"ratio_used": 2., "vm": .87, "isc_peak": 1e-5},
            ])
            complete_methodology.write_rows(root / "methodology_fo1.mt0.csv",
                                           [{"ratio_used": 2., "tphl": 22e-12, "tplh": 24e-12}])
            with patch("sys.argv", ["complete_methodology.py", "analyze", str(root)]):
                with contextlib.redirect_stdout(io.StringIO()):
                    complete_methodology.main()
            self.assertTrue((root / "analisis_metodologia" / "extraccion.csv").is_file())
            self.assertTrue((root / "analisis_metodologia" / "capacitancias.csv").is_file())
            (root / "methodology_sizes.inc").write_text(".param RATIO=3\n")
            with patch("sys.argv", ["complete_methodology.py", "analyze", str(root)]):
                with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(ValueError):
                    complete_methodology.main()


if __name__ == "__main__":
    unittest.main()
