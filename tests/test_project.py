import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from run import simulate, reorder_point

class TestWarehouse(unittest.TestCase):
    def test_observations(self):
        self.assertEqual(len(simulate()), 5760)
    def test_reorder(self):
        self.assertGreater(reorder_point(12, 4), 84)
    def test_reproducible(self):
        self.assertEqual(simulate(2), simulate(2))

if __name__ == '__main__': unittest.main()
