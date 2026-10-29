"""Validate embedded Power BI snapshot and query references without Desktop."""
import base64
import json
from pathlib import Path
import re
import unittest
ROOT = Path(__file__).resolve().parents[1]
class TestPowerBISource(unittest.TestCase):
    def test_embedded_csv_matches_reports(self):
        model = json.loads(next((ROOT/'powerbi').glob('*.SemanticModel/model.bim')).read_text())
        for table in model['model']['tables']:
            expression = '\n'.join(table['partitions'][0]['source']['expression'])
            payload = re.search(r'Binary.FromText\("([A-Za-z0-9+/=]+)"', expression).group(1)
            self.assertEqual(base64.b64decode(payload), (ROOT/'reports'/(table['name']+'.csv')).read_bytes())
    def test_visual_fields_and_bounds(self):
        model = json.loads(next((ROOT/'powerbi').glob('*.SemanticModel/model.bim')).read_text())
        fields = {t['name']: {c['name'] for c in t['columns']} | {m['name'] for m in t.get('measures', [])} for t in model['model']['tables']}
        visuals=list((ROOT/'powerbi').glob('*.Report/definition/pages/*/visuals/*/visual.json'))
        self.assertGreaterEqual(len(visuals), 9)
        for path in visuals:
            visual=json.loads(path.read_text());pos=visual['position']
            self.assertGreaterEqual(pos['x'],0);self.assertGreaterEqual(pos['y'],0)
            self.assertLessEqual(pos['x']+pos['width'],1280);self.assertLessEqual(pos['y']+pos['height'],720)
            for role in visual['visual']['query']['queryState'].values():
                for projection in role['projections']:
                    f=next(iter(projection['field'].values()))
                    self.assertIn(f['Property'], fields[f['Expression']['SourceRef']['Entity']])
    def test_all_csv_rows_match_declared_types(self):
        import csv
        model = json.loads(next((ROOT/'powerbi').glob('*.SemanticModel/model.bim')).read_text())
        for table in model['model']['tables']:
            with (ROOT/'reports'/(table['name']+'.csv')).open(encoding='utf-8', newline='') as stream:
                rows = list(csv.DictReader(stream))
            for column in table['columns']:
                for row in rows:
                    value = row[column['name']]
                    if column['dataType'] == 'int64':
                        self.assertEqual(float(value), int(value))
                    elif column['dataType'] == 'double':
                        float(value)
                    elif column['dataType'] == 'boolean':
                        self.assertIn(value, {'True','False'})

    def test_dax_reference_matches_model(self):
        model = json.loads(next((ROOT/'powerbi').glob('*.SemanticModel/model.bim')).read_text())
        reference = (ROOT/'powerbi/measures.dax').read_text()
        for table in model['model']['tables']:
            for measure in table.get('measures', []):
                self.assertIn(measure['name'] + ' = ' + measure['expression'], reference)

if __name__=='__main__':unittest.main()
