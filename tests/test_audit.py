"""Independent export checks and regressions for portable project builds."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('independent_audit', ROOT/'scripts/verify_project.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def copy_project(target):
    for name in ['src', 'scripts', 'reports', 'powerbi', 'sql']:
        shutil.copytree(ROOT/name, target/name, ignore=shutil.ignore_patterns('__pycache__', '*.pdf', '*.png'))


class TestAudit(unittest.TestCase):
    def test_sql_and_raw_row_audit(self):
        self.assertEqual(checker.audit(), json.loads((ROOT/'reports/numerical_audit.json').read_text()))

    def test_corrupt_kpi_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            copy_project(target)
            p = target/'reports/kpis.json'
            data = json.loads(p.read_text())
            key = next(iter(data))
            data[key] += 1
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'SQL KPI totals'):
                checker.audit(target)

    def test_builds_work_after_checkout_is_renamed(self):
        with tempfile.TemporaryDirectory(prefix='renamed-checkout-') as directory:
            target = Path(directory)
            copy_project(target)
            before = {str(p.relative_to(target)):p.read_bytes() for folder in ['reports','powerbi'] for p in (target/folder).rglob('*') if p.is_file()}
            for script in ['src/run.py','scripts/analyze.py','scripts/build_powerbi.py']:
                subprocess.run([sys.executable,str(target/script)], cwd=directory, check=True, capture_output=True)
            after = {str(p.relative_to(target)):p.read_bytes() for folder in ['reports','powerbi'] for p in (target/folder).rglob('*') if p.is_file()}
            self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
