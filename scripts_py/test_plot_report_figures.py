import tempfile
import unittest
from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image

from plot_report_figures import engineering_axis, save, style, table, voltage_axes


class ReportFigureTests(unittest.TestCase):
    def setUp(self):
        style()
        self.addCleanup(plt.close, "all")

    def test_engineering_units_preserve_si_data(self):
        fig, ax = plt.subplots()
        engineering_axis(ax, "x", "Tiempo", "s", -12)
        engineering_axis(ax, "y", "Corriente", "A", -6)
        ax.plot([0, 25e-12], [0, 24e-6])
        self.assertEqual(ax.get_xlabel(), "Tiempo (ps)")
        self.assertEqual(ax.get_ylabel(), "Corriente (\N{MICRO SIGN}A)")
        self.assertEqual(ax.xaxis.get_major_formatter()(25e-12), "25")
        self.assertEqual(ax.yaxis.get_major_formatter()(24e-6), "24")
        self.assertEqual(ax.lines[0].get_xdata()[1], 25e-12)
        engineering_axis(ax, "y", "Resistencia", "\N{GREEK CAPITAL LETTER OMEGA}", 3)
        self.assertEqual(ax.yaxis.get_major_formatter()(6450), "6.45")
        self.assertEqual(ax.get_ylabel(), "Resistencia (k\N{GREEK CAPITAL LETTER OMEGA})")

    def test_voltage_axes_include_switching_reference_and_endpoints(self):
        fig, ax = plt.subplots()
        voltage_axes(ax)
        self.assertAlmostEqual(ax.get_xticks()[3], .9)
        self.assertAlmostEqual(ax.get_xticks()[-1], 1.8)
        self.assertAlmostEqual(ax.get_yticks()[2], .9)

    def test_vector_outputs_and_png_resolution(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            fig, ax = plt.subplots(figsize=(3.5, 2.9))
            ax.plot([0, 1], [0, 1])
            save(fig, output, "test", 600)
            for suffix in ("pdf", "svg", "png"):
                self.assertGreater((output / f"test.{suffix}").stat().st_size, 100)
            with Image.open(output / "test.png") as image:
                self.assertEqual(image.size, (2100, 1740))
                self.assertAlmostEqual(image.info["dpi"][0], 600, delta=.01)

    def test_nonfinite_data_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "bad.dat").write_text("x y\n0 1\n1 nan\n", encoding="ascii")
            with self.assertRaisesRegex(ValueError, "Invalid plotting data"):
                table(output, "bad")


if __name__ == "__main__":
    unittest.main()
