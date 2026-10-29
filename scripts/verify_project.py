"""Audit committed exports independently of src/run.py, using SQL and raw rows."""
import argparse
from collections import Counter, defaultdict
import csv
import json
import math
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
COUNTRIES = {'Germany', 'Czech Republic', 'India'}


def read_rows(path):
    with path.open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    text = {'order_id', 'warehouse', 'sku', 'status'}
    for row in rows:
        for key, value in row.items():
            if key not in text:
                row[key] = (value == 'True') if value in {'True', 'False'} else float(value) if '.' in value else int(value)
    return rows


def require(condition, message):
    if not condition:
        raise ValueError(message)


def audit(root=ROOT):
    reports = root / 'reports'
    supply = (root / 'powerbi/SupplyChain.pbip').exists()
    sources = ['orders'] if supply else ['warehouse_daily', 'replenishment_recommendations']
    data = {name: read_rows(reports / (name + '.csv')) for name in sources}
    with sqlite3.connect(':memory:') as db:
        db.row_factory = sqlite3.Row
        for name, rows in data.items():
            require(bool(rows), f'{name}: empty baseline')
            columns = ', '.join('"' + key + '"' for key in rows[0])
            db.execute(f'CREATE TABLE {name} ({columns})')
            db.executemany(f'INSERT INTO {name} VALUES ({",".join("?" for _ in rows[0])})', [list(r.values()) for r in rows])
        calculated = dict(db.execute((root / 'sql/kpis.sql').read_text()).fetchone())
    require(calculated == json.loads((reports / 'kpis.json').read_text()), 'SQL KPI totals disagree with kpis.json')
    rows = data[sources[0]]
    require({r['warehouse'] for r in rows} == COUNTRIES, 'Wrong country set')
    if supply:
        require(len({r['order_id'] for r in rows}) == len(rows), 'Duplicate order IDs')
        for r in rows:
            full = 0 if r['blocked'] else min(r['ordered_units'], r['available_units'])
            shortage = max(r['ordered_units'] - r['available_units'], 0)
            otif = not r['blocked'] and full == r['ordered_units'] and r['delivery_delay_days'] <= 0
            status = 'Blocked' if r['blocked'] else 'Stock shortage' if shortage else 'Late' if r['delivery_delay_days'] > 0 else 'On track'
            require((r['fulfilled_units'], r['shortage_units'], r['on_time_in_full'], r['status']) == (full, shortage, otif, status), f"Incorrect derived order fields: {r['order_id']}")
        require(read_rows(reports / 'exception_register.csv') == [r for r in rows if r['status'] != 'On track'], 'Exception export mismatch')
        scorecard = read_rows(reports / 'warehouse_scorecard.csv')
        require(len(scorecard) == 3 and {r['warehouse'] for r in scorecard} == COUNTRIES, 'Scorecard grain mismatch')
        for s in scorecard:
            group = [r for r in rows if r['warehouse'] == s['warehouse']]
            denominator = sum(r['ordered_units'] for r in group if not r['blocked'])
            expected = {'warehouse': s['warehouse'], 'orders': len(group), 'blocked_orders': sum(r['blocked'] for r in group), 'fill_rate': round(sum(r['fulfilled_units'] for r in group)/denominator, 4), 'otif_rate': round(sum(r['on_time_in_full'] for r in group)/len(group), 4)}
            require(s == expected, 'Warehouse scorecard mismatch')
        a = json.loads((reports / 'analysis.json').read_text())
        evidence = {'status': dict(Counter(r['status'] for r in rows)), 'ordered_unblocked': sum(r['ordered_units'] for r in rows if not r['blocked']), 'fulfilled': sum(r['fulfilled_units'] for r in rows), 'otif_orders': sum(r['on_time_in_full'] for r in rows), 'shortage_units': sum(r['shortage_units'] for r in rows)}
        require(all(a[k] == v for k, v in evidence.items()), 'Analysis totals mismatch')
        evidence['all_order_demand'] = sum(r['ordered_units'] for r in rows)
        evidence['all_demand_fill_rate'] = round(evidence['fulfilled']/evidence['all_order_demand'], 4)
        evidence['expected_otif_under_generator'] = round(.91 * (26/71) * (3/11), 6)
    else:
        groups = defaultdict(list)
        for r in rows:
            require(r['erp_stock'] == r['opening_stock'] + r['received'] - r['shipped'], 'Stock conservation failed')
            require(r['shipped'] == min(r['opening_stock'] + r['received'], r['demand']), 'Shipment calculation mismatch')
            require(r['variance'] == r['wms_stock'] - r['erp_stock'], 'Variance mismatch')
            groups[(r['warehouse'], r['sku'])].append(r)
        require(len({(r['warehouse'], r['sku'], r['day']) for r in rows}) == len(rows), 'Duplicate daily key')
        for group in groups.values():
            group.sort(key=lambda r: r['day'])
            require([r['day'] for r in group] == list(range(1, len(group)+1)), 'Missing day')
            require(all(a['erp_stock'] == b['opening_stock'] for a,b in zip(group,group[1:])), 'Stock continuity failed')
        recs = data['replenishment_recommendations']
        require(len(recs) == len(groups) == len({(r['warehouse'],r['sku']) for r in recs}), 'Proposal grain mismatch')
        for r in recs:
            history = groups[(r['warehouse'], r['sku'])][-28:]
            values = [row['demand'] for row in history]
            mean = sum(values)/len(values)
            std = math.sqrt(sum((v-mean)**2 for v in values)/(len(values)-1)) if len(values)>1 else 0
            safety = 1.65 * std * math.sqrt(7)
            point, target = math.ceil(mean*7+safety), math.ceil(mean*21+safety)
            last = history[-1]
            alert = last['wms_stock'] <= point
            expected = {'warehouse':r['warehouse'], 'sku':r['sku'], 'as_of_day':last['day'], 'history_days':len(history), 'mean_daily_demand':round(mean,3), 'sample_std':round(std,3), 'wms_stock':last['wms_stock'], 'reorder_point':point, 'target_stock':target, 'reorder_alert':alert, 'recommended_order_qty':max(target-last['wms_stock'],0) if alert else 0, 'stock_variance':last['variance']}
            require(r == expected, f"Reorder calculation mismatch: {r['warehouse']} {r['sku']}")
        require(read_rows(reports/'erp_wms_discrepancies.csv') == [r for r in rows if r['variance'] != 0], 'Discrepancy export mismatch')
        weeks = defaultdict(list)
        for r in rows: weeks[(r['day']-1)//7+1].append(r)
        expected_weeks = []
        for week, group in sorted(weeks.items()):
            demand, shipped = sum(r['demand'] for r in group), sum(r['shipped'] for r in group)
            expected_weeks.append({'week':week, 'demand':demand, 'shipped':shipped, 'discrepancy_records':sum(r['variance']!=0 for r in group), 'fill_rate':round(shipped/demand,4)})
        require(read_rows(reports/'weekly_kpis.csv') == expected_weeks, 'Weekly aggregation mismatch')
        demand, shipped = sum(r['demand'] for r in rows), sum(r['shipped'] for r in rows)
        a = json.loads((reports/'analysis.json').read_text())
        require(a['demand'] == demand and a['shipped'] == shipped and a['alerts'] == [r for r in recs if r['reorder_alert']], 'Analysis totals mismatch')
        regions = []
        for country in ['Germany', 'Czech Republic', 'India']:
            group = [r for r in rows if r['warehouse'] == country]
            regions.append({'warehouse':country, 'observations':len(group), 'discrepancies':sum(r['variance'] != 0 for r in group), 'demand':sum(r['demand'] for r in group), 'shipped':sum(r['shipped'] for r in group)})
        require(a['regions'] == regions, 'Regional analysis mismatch')
        scenarios = []
        for lead in [3, 7, 10, 14]:
            alerts, units = 0, 0
            for group in groups.values():
                values = [r['demand'] for r in group[-28:]]
                mean = sum(values)/len(values)
                std = math.sqrt(sum((v-mean)**2 for v in values)/(len(values)-1))
                safety = 1.65*std*math.sqrt(lead)
                stock = group[-1]['wms_stock']
                if stock <= math.ceil(mean*lead+safety):
                    alerts += 1
                    units += max(math.ceil(mean*21+safety)-stock, 0)
            scenarios.append({'lead_time':lead, 'alerts':alerts, 'proposed_units':units})
        require(a['scenarios'] == scenarios, 'Lead-time scenario mismatch')
        evidence = {'warehouse_sku_pairs':len(groups), 'total_demand':demand, 'total_shipped':shipped, 'unfulfilled_units':demand-shipped, 'discrepancy_rate':round(calculated['discrepancy_records']/len(rows),6), 'expected_daily_receipts':round(80/6,6), 'expected_daily_demand':12, 'positive_proposals':[{'warehouse':r['warehouse'],'sku':r['sku'],'units':r['recommended_order_qty']} for r in recs if r['reorder_alert']]}
    return {'method':'Independent SQLite KPI aggregation and raw-field recomputation; no imports from implementation', 'result':'passed', 'locations':sorted(COUNTRIES), 'kpis':calculated, 'evidence':evidence}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Refresh the committed audit evidence after verification')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2) + '\n'
    if args.write:
        (ROOT/'reports/numerical_audit.json').write_text(result)
    print(result, end='')


if __name__ == '__main__':
    main()
