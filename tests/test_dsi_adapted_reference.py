"""Comprova que les constants de la referència del DSI adaptat coincideixen amb les recalculades.

Ús (des de l'arrel): .venv/bin/python -m unittest tests.test_dsi_adapted_reference
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from core.dsi_adapted import DSI_ADAPTED_REFERENCE as REF  # noqa: E402
from compute_dsi_adapted_reference import DEFAULT_CSV, compute_reference  # noqa: E402


@unittest.skipUnless(DEFAULT_CSV.exists(), "ASOS/ és fora de git: falta el CSV de controls")
class TestDsiAdaptedReference(unittest.TestCase):
    def test_constants_match_recomputed(self):
        ref = compute_reference()
        self.assertEqual(ref["n_recordings"], REF["n_recordings"])
        for k in ("mean", "sd", "min", "max"):
            self.assertAlmostEqual(ref[k], REF[k], places=4, msg=k)
            self.assertEqual(round(ref[k], 4), REF[k], k)


if __name__ == "__main__":
    unittest.main()
