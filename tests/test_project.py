import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from run import simulate, reorder_point

class TestWarehouse(unittest.TestCase):
    def test_observations(self):
        self.assertEqual(len(simulate()), 4320)
        self.assertEqual({row["warehouse"] for row in simulate()}, {"Germany", "Czech Republic", "India"})
    def test_reorder(self):
        self.assertGreater(reorder_point(12, 4), 84)
    def test_reproducible(self):
        self.assertEqual(simulate(2), simulate(2))




class TestBusinessRules(unittest.TestCase):
    def test_stock_conservation(self):
        for r in simulate():
            self.assertEqual(r['erp_stock'], r['opening_stock'] + r['received'] - r['shipped'])
            self.assertLessEqual(r['shipped'], r['demand'])
            self.assertGreaterEqual(r['erp_stock'], 0)
            self.assertEqual(r['variance'], r['wms_stock'] - r['erp_stock'])
    def test_hand_calculated_reorder(self):
        self.assertEqual(reorder_point(12, 4), 102)
        self.assertEqual(reorder_point(12, 0), 84)
        self.assertEqual(reorder_point(12, 4, 0), 0)
    def test_invalid_parameters(self):
        from run import recommendations
        with self.assertRaises(ValueError):
            simulate(0)
        with self.assertRaises(ValueError):
            reorder_point(12, -1)
        with self.assertRaises(ValueError):
            recommendations([], lead_time=30, target_days=21)
    def test_trigger_and_no_trigger(self):
        from run import recommendations
        rows = [dict(warehouse='Germany', sku='A', day=d, demand=10, wms_stock=70, variance=0) for d in range(1,30)]
        result = recommendations(list(reversed(rows)))[0]
        self.assertEqual(result['history_days'], 28)
        self.assertEqual(result['reorder_point'], 70)
        self.assertEqual(result['recommended_order_qty'], 140)
        rows[-1]['wms_stock'] = 71
        self.assertEqual(recommendations(rows)[0]['recommended_order_qty'], 0)
    def test_build_is_reproducible(self):
        import tempfile
        import csv
        from run import build
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build(output, days=3)
            original = {p.name: p.read_bytes() for p in output.iterdir()}
            with (output/'replenishment_recommendations.csv').open() as f:
                self.assertEqual(len(list(csv.DictReader(f))), 36)
            build(output, days=3)
            self.assertEqual(original, {p.name: p.read_bytes() for p in output.iterdir()})

if __name__ == '__main__':
    unittest.main()
