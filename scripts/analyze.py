from pathlib import Path
import csv,json,sys,importlib.util
root=Path(__file__).resolve().parents[1]
for repo in [root]:
 sys.path.insert(0,str(repo/'src'));spec=importlib.util.spec_from_file_location('analysis_run',repo/'src/run.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 if mod.PROJECT_KIND == 'supply_chain':
  rows=mod.enrich(mod.simulate());from collections import Counter
  d={'status':dict(Counter(r['status'] for r in rows)),'ordered_unblocked':sum(r['ordered_units'] for r in rows if not r['blocked']),'fulfilled':sum(r['fulfilled_units'] for r in rows),'otif_orders':sum(r['on_time_in_full'] for r in rows),'shortage_units':sum(r['shortage_units'] for r in rows),'scenario':[]}
  for seed in [7,42,99]:d['scenario'].append({'seed':seed,**mod.metrics(mod.simulate(seed=seed))})
 else:
  rows=mod.simulate();recs=mod.recommendations(rows);d={'demand':sum(r['demand'] for r in rows),'shipped':sum(r['shipped'] for r in rows),'alerts':[r for r in recs if r['reorder_alert']],'scenarios':[],'regions':[]}
  for lead in [3,7,10,14]:
   rec=mod.recommendations(rows,lead_time=lead);d['scenarios'].append({'lead_time':lead,'alerts':sum(r['reorder_alert'] for r in rec),'proposed_units':sum(r['recommended_order_qty'] for r in rec)})
  for w in mod.WAREHOUSES:
   sel=[r for r in rows if r['warehouse']==w];d['regions'].append({'warehouse':w,'observations':len(sel),'discrepancies':sum(r['variance']!=0 for r in sel),'demand':sum(r['demand'] for r in sel),'shipped':sum(r['shipped'] for r in sel)})
 (repo/'reports/analysis.json').write_text(json.dumps(d,indent=2)+'\n');print(repo.name,json.dumps(d))
 sys.path.pop(0)
