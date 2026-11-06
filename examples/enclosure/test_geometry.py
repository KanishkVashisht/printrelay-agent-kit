"""Local regression checks; no upload, supplier, payment, or printer calls."""
import json
from pathlib import Path
import tempfile
import unittest

from verify import measure, report

ROOT = Path(__file__).resolve().parent


class EnclosureChecks(unittest.TestCase):
    def test_default_parts_have_expected_bounds_and_volumes(self):
        actual = report()
        self.assertFalse(actual["certifies_printability"])
        base, lid = [actual["parts"][f"enclosure-{part}.stl"] for part in ("base", "lid")]
        self.assertEqual(base["extents_mm"], [60, 40, 22])
        self.assertEqual(lid["extents_mm"], [60, 40, 6])
        self.assertAlmostEqual(base["signed_volume_mm3"], 12360, places=5)
        self.assertAlmostEqual(lid["signed_volume_mm3"], 5857.28, places=3)

    def test_removed_face_fails_edge_check(self):
        lines = (ROOT / "enclosure-base.stl").read_text().splitlines()
        malformed = "\n".join(lines[:1] + lines[8:]).encode()
        with self.assertRaisesRegex(ValueError, "edge"):
            measure(malformed)

    def test_inch_reinterpretation_is_rejected(self):
        params = json.loads((ROOT / "parameters.json").read_text())
        params["units"] = "inch"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "parameters.json"
            path.write_text(json.dumps(params))
            with self.assertRaisesRegex(ValueError, "mm units"):
                report(parameter_file=path)


if __name__ == "__main__":
    unittest.main()
