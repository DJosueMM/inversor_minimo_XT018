import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from analyze_characterization import measurements, print_tables, svg_plot
from first_order_model import (
    PARAMETERS, critical_voltage, current_per_width, fo1_sizing, on_resistance,
    read_hspice_2013_transient, switching_voltage, vtc, waveform_window,
)


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "fixture.txt"

    def test_measurements_skip_hspice_metadata(self):
        self.path.write_text("$DATA1 SOURCE='HSPICE'\n.TITLE 'example'\nratio,current\n2,-2.5e-5\n")
        self.assertEqual(measurements(self.path), [{"ratio": 2.0, "current": -2.5e-5}])

    def test_failed_or_nonfinite_measurements_are_rejected(self):
        for value in ("failed", "nan", "inf"):
            with self.subTest(value=value):
                self.path.write_text(f"ratio,current\n2,{value}\n")
                with self.assertRaises(ValueError):
                    measurements(self.path)

    def test_split_print_tables_preserve_sign_and_columns(self):
        self.path.write_text(
            "header\nx\n\n time voltage current\n dn vsn\n"
            "0 1.8 0\n1e-11 1.79 2e-4\ny\n"
            "x\n time current\n vsp\n0 0\n1e-11 -1e-4\ny\n"
        )
        self.assertEqual(print_tables(self.path, "time"), [
            (["dn", "vsn"], [[0, 1.8, 0], [1e-11, 1.79, 2e-4]]),
            (["vsp"], [[0, 0], [1e-11, -1e-4]]),
        ])

    def test_truncated_table_is_rejected(self):
        self.path.write_text("time voltage\ndn\n0 1.8\n")
        with self.assertRaises(ValueError):
            print_tables(self.path, "time")

    def test_svg_is_well_formed_and_labels_are_escaped(self):
        svg_plot(self.path, "A & B", "x < y", "V/I", [("N & P", [(0, 1), (1, 2)])])
        tree = ET.parse(self.path)
        self.assertEqual(tree.getroot().tag, "{http://www.w3.org/2000/svg}svg")
        self.assertIn("A & B", "".join(tree.getroot().itertext()))

    def test_model_reproduces_ion_calibration_and_cutoff(self):
        for kind, (_, threshold, ion) in PARAMETERS.items():
            self.assertAlmostEqual(current_per_width(kind, 1.8, 1.8), ion, places=8)
            self.assertEqual(current_per_width(kind, threshold, 1.8), 0)
            self.assertEqual(current_per_width(kind, 1.8, 0), 0)
            self.assertGreater(on_resistance(kind), 0)

    def test_model_vtc_rails_monotonicity_and_switch_balance(self):
        for ratio in (2.425, 3.125):
            output = [vtc(i * .018, ratio) for i in range(101)]
            self.assertAlmostEqual(output[0], 1.8)
            self.assertAlmostEqual(output[-1], 0)
            self.assertTrue(all(a >= b - 1e-12 for a, b in zip(output, output[1:])))
            vm = switching_voltage(ratio)
            self.assertAlmostEqual(
                current_per_width("n", vm, vm),
                ratio * current_per_width("p", 1.8 - vm, 1.8 - vm),
            )

    def test_weste_linear_and_saturation_expressions(self):
        for kind, (kp, threshold, _) in PARAMETERS.items():
            critical = critical_voltage(kind)
            for gate in (.9, 1.8):
                overdrive = gate - threshold
                saturation = overdrive * critical / (overdrive + critical)
                expected_sat = (kp / .18) * critical * overdrive**2 / (2 * (overdrive + critical))
                self.assertAlmostEqual(current_per_width(kind, gate, saturation), expected_sat)
                self.assertAlmostEqual(current_per_width(kind, gate, 1.8), expected_sat)
                drain = saturation / 2
                expected_linear = (kp / .18) * (overdrive * drain - drain**2 / 2) / (1 + drain / critical)
                self.assertAlmostEqual(current_per_width(kind, gate, drain), expected_linear)
                self.assertAlmostEqual(
                    current_per_width(kind, gate, saturation * (1 - 1e-8)),
                    expected_sat, places=5,
                )

    def test_binary_waveform_rejects_truncated_file(self):
        self.path.write_bytes(b"truncated")
        with self.assertRaises(ValueError):
            read_hspice_2013_transient(self.path)

    def test_rabaey_fo1_free_minimum_and_symmetry(self):
        rn, rp = 7220.472571010651, 17546.78550692067
        a, b = 1.334016e-15, 1.385136e-15
        result = fo1_sizing(rn, rp, a, b)
        ratio = result["symmetric_ratio"]
        self.assertAlmostEqual(ratio, 2.430143641479777)
        self.assertAlmostEqual(result["free_ratio"], 1.5298550456224107)
        self.assertAlmostEqual(result["symmetric_delay_s"] * 1e12, 23.523273640902023)
        self.assertAlmostEqual(rn, rp / ratio)
        free = result["free_ratio"]
        derivative = b * rn - a * rp / free**2
        self.assertAlmostEqual(derivative, 0)
        def delay(r):
            return (a + b * r) * (rn + rp / r)
        self.assertLess(delay(free), delay(free * .99))
        self.assertLess(delay(free), delay(free * 1.01))
        self.assertNotAlmostEqual(rn, rp / free)
        # Equal capacitance per unit width recovers Rabaey's sqrt(Rp/Rn).
        self.assertAlmostEqual(fo1_sizing(rn, rp, a, a)["free_ratio"], (rp / rn)**.5)

    def test_rabaey_fo1_rejects_invalid_parameters(self):
        for value in (0, -1, float("nan"), float("inf")):
            for index in range(4):
                values = [1., 1., 1., 1.]
                values[index] = value
                with self.assertRaises(ValueError):
                    fo1_sizing(*values)

    def test_waveform_window_includes_interpolated_endpoints(self):
        rows = [(0.0, 0.0), (1e-9, 1.0), (2e-9, 0.0)]
        points = waveform_window(rows, 1, .5e-9, 1.5e-9)
        self.assertAlmostEqual(points[0][0], 500)
        self.assertAlmostEqual(points[0][1], .5)
        self.assertAlmostEqual(points[-1][1], .5)
        self.assertEqual(len(points), 3)


if __name__ == "__main__":
    unittest.main()
