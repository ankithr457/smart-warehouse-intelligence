"""Check 100 seeds and record observed simulation ranges, not business forecasts."""
from pathlib import Path
import importlib.util,sys,json
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
spec=importlib.util.spec_from_file_location('simulation',root/'src/run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
results=[]
for seed in range(100):
 rows=m.simulate(seed=seed)
 if m.PROJECT_KIND=='supply_chain':
  assert len(rows)==1200
  for r in rows:
   assert 0<=r['fulfilled_units']<=min(r['ordered_units'],r['available_units'])
   assert not r['blocked'] or r['fulfilled_units']==0
  results.append(m.metrics(rows)['otif_rate'])
 else:
  assert len(rows)==4320
  for r in rows:
   assert r['erp_stock']==r['opening_stock']+r['received']-r['shipped']
   assert 0<=r['shipped']<=r['demand']
  for lead in [0,3,7,14,21]:
   recs=m.recommendations(rows,lead_time=lead)
   assert len(recs)==36
   assert all(r['recommended_order_qty']>=0 and (r['reorder_alert'] or r['recommended_order_qty']==0) for r in recs)
  results.append(sum(r['shipped'] for r in rows)/sum(r['demand'] for r in rows))
out={'seeds':100,'result':'passed','metric':'otif_rate' if m.PROJECT_KIND=='supply_chain' else 'unit_fill_rate','minimum':round(min(results),6),'maximum':round(max(results),6),'mean':round(sum(results)/len(results),6)}
(root/'reports/robustness_check.json').write_text(json.dumps(out,indent=2)+'\n');print(root.name,out)
