"""Small, dependency-free report writer for portable offline demos."""
import csv
import html
import json
from pathlib import Path


def write_csv(path, rows, fields=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def dashboard(path, title, subtitle, metrics, rows, chart_field, chart_value):
    """Write a self-contained report with accessible warehouse/search filters."""
    payload = json.dumps(rows).replace("<", r"\u003c")
    cards = "".join(f'<article><small>{html.escape(str(k))}</small><strong>{html.escape(str(v))}</strong></article>' for k, v in metrics.items())
    template = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f3f6fa;color:#15283d;font:16px system-ui,sans-serif}main{max-width:1200px;margin:auto;padding:40px 24px}header{border-bottom:1px solid #cad5df;padding-bottom:24px}h1{font-size:clamp(28px,5vw,44px);margin:12px 0}p{line-height:1.65;color:#4d6177}.eyebrow{font-size:12px;letter-spacing:2px;color:#00756b;font-weight:700}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin:28px 0}article,section{background:white;border:1px solid #dce4eb;border-radius:12px;padding:22px}small{display:block;color:#53667c}strong{display:block;font-size:30px;margin-top:10px}section{margin:20px 0}label{display:inline-block;margin:8px 18px 8px 0}input,select,button{font:inherit;padding:10px;border:1px solid #aebdcd;border-radius:6px;background:white}button{cursor:pointer;background:#006b61;color:white}table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:10px;border-bottom:1px solid #e0e7ee;white-space:nowrap}th{background:#edf3f8;position:sticky;top:0}.table{overflow:auto;max-height:500px}.bar{display:grid;grid-template-columns:120px 1fr 75px;gap:10px;align-items:center;margin:15px 0}.track{background:#e8f0f3;height:22px;border-radius:4px}.fill{height:100%;background:#008579;border-radius:4px}footer{font-size:13px;color:#53667c;margin-top:25px}@media(max-width:550px){main{padding:20px 12px}.bar{grid-template-columns:90px 1fr 60px}input{max-width:100%}}</style></head><body><main>
<header><span class="eyebrow">ANKITH RAMESH BABU / OPERATIONS ANALYTICS</span><h1>__TITLE__</h1><p>__SUBTITLE__</p></header><div class="cards">__CARDS__</div>
<section><h2>Explore the report</h2><label>Warehouse <select id="warehouse"><option value="">All warehouses</option></select></label><label>Search records <input id="search" type="search" placeholder="Search any field"></label><button id="download">Export filtered CSV</button><p>Cards show the full dataset. The chart and table follow your filters.</p><div id="chart" aria-label="Warehouse comparison"></div></section>
<section><h2>Operational detail</h2><p id="count" aria-live="polite"></p><div class="table"><table><thead id="head"></thead><tbody id="body"></tbody></table></div><p>Table shows the first 200 matching rows. CSV export includes every matching row.</p></section><footer>Synthetic portfolio case study. No employer data or live ERP connection. Rebuild with python src/run.py.</footer></main>
<script>const rows=__DATA__, keys=Object.keys(rows[0]||{}), field=__FIELD__, value=__VALUE__;let filtered=[];
const $=id=>document.getElementById(id);const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
[...new Set(rows.map(r=>r.warehouse))].sort().forEach(w=>{const o=document.createElement('option');o.value=w;o.textContent=w;$('warehouse').append(o)});
$('head').innerHTML='<tr>'+keys.map(k=>'<th scope="col">'+esc(k.replaceAll('_',' '))+'</th>').join('')+'</tr>';
function render(){const q=$('search').value.toLowerCase();filtered=rows.filter(r=>(!$('warehouse').value||r.warehouse===$('warehouse').value)&&Object.values(r).join(' ').toLowerCase().includes(q));$('count').textContent=filtered.length+' of '+rows.length+' records';$('body').innerHTML=filtered.slice(0,200).map(r=>'<tr>'+keys.map(k=>'<td>'+esc(r[k])+'</td>').join('')+'</tr>').join('');const groups={};filtered.forEach(r=>groups[r[field]]=(groups[r[field]]||0)+Number(r[value]));const max=Math.max(1,...Object.values(groups));$('chart').innerHTML='<h3>'+esc(value.replaceAll('_',' '))+' by '+esc(field)+'</h3>'+Object.entries(groups).map(([k,v])=>'<div class="bar"><span>'+esc(k)+'</span><div class="track"><div class="fill" style="width:'+Math.max(0,100*v/max)+'%"></div></div><span>'+v.toLocaleString()+'</span></div>').join('')}
$('warehouse').addEventListener('change',render);$('search').addEventListener('input',render);$('download').addEventListener('click',()=>{const cell=v=>'"'+String(v).replaceAll('"','""')+'"';const csv=[keys,...filtered.map(r=>keys.map(k=>r[k]))].map(r=>r.map(cell).join(',')).join('\r\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='filtered-report.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)});render();</script></body></html>'''
    replacements = {"__TITLE__": html.escape(title), "__SUBTITLE__": html.escape(subtitle), "__CARDS__": cards, "__DATA__": payload, "__FIELD__": json.dumps(chart_field), "__VALUE__": json.dumps(chart_value)}
    for key, value in replacements.items():
        template = template.replace(key, value)
    Path(path).write_text(template, encoding="utf-8")
