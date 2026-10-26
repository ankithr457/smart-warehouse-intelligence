from pathlib import Path
import csv,json,math,inspect,sys,importlib.util,textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,Preformatted,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
ROOT=Path(__file__).resolve().parents[1]
NAVY='#15283d';TEAL='#008579';GRAY='#53667c';GOLD='#d99a35'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.labelcolor':NAVY,'text.color':NAVY})
import reportlab
for name,file,fallback in [('Body','DejaVuSans.ttf','Vera.ttf'),('Bold','DejaVuSans-Bold.ttf','VeraBd.ttf'),('Mono','DejaVuSansMono.ttf','Vera.ttf')]:
    font=Path('/usr/share/fonts/truetype/dejavu')/file
    if not font.exists():font=Path(reportlab.__file__).parent/'fonts'/fallback
    pdfmetrics.registerFont(TTFont(name,str(font)))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='P',fontName='Body',fontSize=10,leading=15,textColor=colors.HexColor(NAVY),spaceAfter=10))
styles.add(ParagraphStyle(name='H',fontName='Bold',fontSize=23,leading=29,textColor=colors.HexColor(NAVY),spaceAfter=18))
styles.add(ParagraphStyle(name='Hsmall',fontName='Bold',fontSize=12,leading=17,textColor=colors.HexColor(TEAL),spaceBefore=8,spaceAfter=9))
styles.add(ParagraphStyle(name='Caption2',fontName='Body',fontSize=8,leading=12,textColor=colors.HexColor(GRAY),spaceAfter=14))
styles.add(ParagraphStyle(name='Code2',fontName='Mono',fontSize=7.3,leading=10,textColor=colors.HexColor(NAVY),backColor=colors.HexColor('#eef3f8'),borderPadding=10,spaceAfter=12))
styles.add(ParagraphStyle(name='Cover',fontName='Bold',fontSize=36,leading=43,textColor=colors.HexColor(NAVY),spaceAfter=22))
def para(s,sty='P'):return Paragraph(s,styles[sty])
def table(rows,widths=None):
 data=[[para(str(c),'Caption2') for c in row] for row in rows]
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dfeeea')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),0.8,colors.HexColor(TEAL)),('LINEBELOW',(0,1),(-1,-1),0.3,colors.HexColor('#dce4eb')),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),4)]));return t
def img(path,width=475,maxheight=440):
 im=PILImage.open(path);w,h=im.size;scale=min(width/w,maxheight/h);return Image(str(path),width=w*scale,height=h*scale,hAlign='LEFT')
def chart_save(fig,p):fig.tight_layout();fig.savefig(p,dpi=180,bbox_inches='tight',facecolor='white');plt.close(fig)
for repo in [ROOT]:
 supply=repo.name.startswith('international');short='Supply chain analytics' if supply else 'Warehouse intelligence';title='International Supply Chain Analytics' if supply else 'Smart Warehouse Intelligence';a=json.loads((repo/'reports/analysis.json').read_text());k=json.loads((repo/'reports/kpis.json').read_text());figs=repo/'reports/figures';figs.mkdir(exist_ok=True)
 if supply:
  fig,ax=plt.subplots(figsize=(8,3.3));names=list(a['status']);values=list(a['status'].values());ax.barh(names,values,color=[GOLD,TEAL,'#527596',NAVY]);ax.invert_yaxis();ax.set_xlabel('Orders');ax.set_title('Primary exception status');
  for i,v in enumerate(values):ax.text(v+8,i,str(v),va='center')
  ax.set_xlim(0,max(values)*1.17);chart_save(fig,figs/'results.png')
  score=list(csv.DictReader((repo/'reports/warehouse_scorecard.csv').open()))
  fig,ax=plt.subplots(figsize=(8,3.3));x=range(4);ax.bar([i-.18 for i in x],[100*float(r['fill_rate']) for r in score],.36,label='Unit fill rate',color=TEAL);ax.bar([i+.18 for i in x],[100*float(r['otif_rate']) for r in score],.36,label='OTIF',color=GOLD);ax.set_xticks(list(x),[r['warehouse'] for r in score]);ax.set_ylim(0,100);ax.set_ylabel('Percent');ax.legend();chart_save(fig,figs/'comparison.png')
 else:
  fig,ax=plt.subplots(figsize=(8,3.3));regions=a['regions'];ax.bar([r['warehouse'] for r in regions],[r['discrepancies'] for r in regions],color=TEAL);ax.set_ylabel('Discrepancy observations');ax.set_title('Reconciliation workload by warehouse');chart_save(fig,figs/'results.png')
  weekly=list(csv.DictReader((repo/'reports/weekly_kpis.csv').open()));fig,ax=plt.subplots(figsize=(8,3.3));ax.plot([int(r['week']) for r in weekly],[int(r['demand']) for r in weekly],color=TEAL,label='Demand',marker='o',markersize=3);ax.plot([int(r['week']) for r in weekly],[int(r['shipped']) for r in weekly],color=GOLD,label='Shipped',linestyle='--');ax.set_xlabel('Simulation week (week 18 contains one day)');ax.set_ylabel('Units');ax.legend();chart_save(fig,figs/'comparison.png')
 # Layout derived directly from PBIR coordinates, not presented as a screenshot.
 report=next((repo/'powerbi').glob('*.Report'));fig,axs=plt.subplots(2,1,figsize=(9,9))
 for ax,page in zip(axs,['overview','detail']):
  ax.set_xlim(0,1280);ax.set_ylim(720,0);ax.axis('off');ax.set_title('Overview page' if page=='overview' else 'Detail page',loc='left')
  for p in (report/'definition/pages'/page/'visuals').glob('*/visual.json'):
   d=json.loads(p.read_text());pos=d['position'];kind=d['visual']['visualType'];ax.add_patch(Rectangle((pos['x'],pos['y']),pos['width'],pos['height'],facecolor='#e7f2ef' if kind=='card' else '#f0f4f8',edgecolor='#8095a7'))
   label=d['visual']['visualContainerObjects']['title'][0]['properties']['text']['expr']['Literal']['Value'].strip("'")
   ax.text(pos['x']+12,pos['y']+pos['height']/2,textwrap.fill(label,28)+'\n['+kind+']',va='center',fontsize=8)
 chart_save(fig,figs/'powerbi-layout.png')
 story=[]
 def add(s,sty='P'):story.append(para(s,sty))
 def page(n,heading):
  if story:story.append(PageBreak())
  add(f'{n:02d} / PROJECT REPORT','Caption2');add(heading,'H')
 def pic(name,cap,width=475,maxheight=420):story.append(img(figs/name,width,maxheight));add(cap,'Caption2')
 def grid(rows,widths=None):story.append(table(rows,widths or [475/len(rows[0])]*len(rows[0])));story.append(Spacer(1,8))
 # 1
 add('OPERATIONS ANALYTICS / INDEPENDENT CASE STUDY','Hsmall');story.append(Spacer(1,40));add(title,'Cover');add('Technical project report','Hsmall');add('Ankith Ramesh Babu');add('26 October 2026 | Release 2');story.append(Spacer(1,30))
 add('Order fulfillment, exception prioritization and regional performance.' if supply else 'Inventory reconciliation, demand fulfillment and replenishment planning.','Hsmall')
 add('This report documents a reproducible analysis of synthetic operational records. It connects the business questions, calculation rules, software implementation, dashboard views and verification evidence in one reviewable package.')
 story.append(Spacer(1,24));grid([['Scope','Default dataset','Primary outputs'],['Four warehouse regions','1,200 orders' if supply else '5,760 daily observations','Python analysis, HTML dashboards, Power BI project source, CSV exports']],[145,150,180])
 add('Results describe the included simulation. They are not employer performance measurements, deployed ERP outcomes or quantified cost savings.','Caption2')
 add('Repository: github.com/ankithr457/'+repo.name,'Caption2')
 #2
 page(2,'Executive summary and contents')
 add('The analysis turns order-level stock and fulfillment records into an exception queue and a warehouse scorecard. The central distinction is between unit fill rate and on-time-in-full (OTIF): a partially fulfilled order can contribute shipped units while still failing OTIF.' if supply else 'The analysis separates reconciliation from replenishment. Daily ERP and WMS snapshots identify discrepancies, while a separate SKU-level decision table uses recent demand to propose replenishment quantities. A discrepancy is an investigation signal, not evidence of physical loss.')
 grid([['Result','Value','Interpretation'],*([['Blocked orders','106 / 1,200','Administrative release queue'],['Unit fill rate','78.57%','52,713 / 67,089 unblocked ordered units'],['OTIF','8.92%','107 complete, unblocked, on-time orders']] if supply else [['Discrepancies','2,245 / 5,760','38.98% of observations'],['Demand fulfillment','99.56%','69,327 / 69,633 demanded units'],['Replenishment','469 units','Two proposals at the final snapshot']])],[125,120,230])
 add('Report navigation','Hsmall');grid([['Section','Page'],['Business scope and architecture','3'],['Data specification and provenance','4'],['Calculation methodology','5'],['Results and operational interpretation','6'],['Dashboard overview and interaction','7-8'],['Power BI model and report layout','9'],['Sensitivity analysis','10'],['Implementation excerpts','11'],['Validation and reproducibility','12'],['Limitations and conclusion','13'],['References and artifact index','14']],[375,100])
 #3
 page(3,'Business scope and architecture')
 add('Questions addressed','Hsmall')
 for q in (['Which orders require action, and why?','How much demand can be fulfilled on unblocked orders?','Which warehouse has the largest exception workload?','How does the definition of OTIF change interpretation?'] if supply else ['Where do ERP and WMS snapshots disagree?','How much demand remains unfulfilled?','Which warehouse-SKU pairs cross the reorder threshold?','How sensitive are proposals to assumed lead time?']):add('• '+q)
 add('Processing sequence','Hsmall');grid([['Stage','Implementation','Output'],['Generate','Seeded Python simulation','Operational records'],['Calculate','Documented business rules','KPIs and decision fields'],['Export','Deterministic CSV / JSON writer','Auditable report files'],['Present','HTML and PBIR visual definitions','Interactive review surfaces'],['Verify','Unit tests, schema and browser checks','Validation evidence']],[85,200,190])
 add('Design decisions','Hsmall');add('The analysis uses Python standard-library functions to keep execution portable. The browser report embeds its data and needs no server. The Power BI model embeds the same CSV snapshot in Power Query, avoiding machine-specific paths. Data generation and decision rules remain separate from presentation.')
 add('Operational boundaries','Hsmall');add('This is a batch analysis of simulated observations. It does not write to SAP, execute procurement transactions, reserve stock or authorize operational changes. Each exported row retains the identifiers needed to trace a result back to its source observation.')
 #4
 page(4,'Data specification and provenance')
 add('All source observations are generated in src/run.py with a fixed random seed. No customer, supplier or employee data is used. Regional names represent four analytical groups, not actual sites.')
 if supply:
  grid([['Field','Type','Meaning'],['order_id','Text / unique','SO-prefixed order identifier'],['warehouse','Text','Germany, Hong Kong, Taiwan, Malaysia'],['ordered_units','Integer','Uniformly sampled from 1 to 120'],['available_units','Integer','max(0, order quantity + offset -45 to +25)'],['blocked','Boolean','Independent probability of 9%'],['delivery_delay_days','Integer','Uniform integer from -2 to 8'],['fulfilled_units','Integer','0 if blocked, otherwise min(quantity, stock)'],['status / OTIF','Derived','Priority classification and strict delivery flag']],[130,100,245])
  add('The availability field is a per-order snapshot. The simulation does not share inventory between orders or model a rolling stock ledger. Delivery delay is sampled independently of stock and block status. These simplifications create a controlled exception dataset. Seed 42 produces the committed baseline.')
 else:
  grid([['Field','Type','Meaning'],['warehouse + sku + day','Composite key','4 warehouses x 12 SKUs x 120 days'],['opening_stock','Integer','Previous ERP closing stock'],['received','Integer','Sampled from 0, 0, 0, 0, 30, 50'],['demand','Integer','Daily demand sampled from 2 to 22'],['shipped','Integer','min(opening stock + receipts, demand)'],['erp_stock','Integer','Opening + received - shipped'],['wms_stock','Integer','max(0, ERP stock + sampled noise)'],['variance','Integer','WMS minus ERP stock']],[140,90,245])
  add('Each warehouse-SKU series starts with 120 to 500 ERP units. WMS noise is sampled from -3, 0, 0, 0, 2. Stock observations are snapshots, so totals across dates are not an inventory balance. Seed 43 produces the baseline. Simulation days are numbered periods, not calendar dates.')
 add('Traceability','Hsmall');add('Committed CSVs, KPI JSON, analysis JSON and the Power BI embedded snapshot refer to the same default run. Changes to seeds or assumptions require regenerated reports and a new result interpretation.')
 #5
 page(5,'Calculation methodology')
 if supply:
  grid([['Metric','Definition'],['Unit fill rate','Fulfilled units / ordered units on unblocked orders'],['OTIF rate','Unblocked AND full quantity AND delay <= 0, divided by all orders'],['Shortage units','max(ordered units - available units, 0)'],['Status priority','Blocked, then Stock shortage, then Late, then On track']],[130,345])
  add('Worked example','Hsmall');add('An unblocked order requests 10 units with 6 available and a delay of -1 day. Fulfilled quantity is 6, shortage is 4 and the order contributes 60% unit fill. OTIF is false because the order is incomplete. If the order is blocked, fulfillment becomes zero and its quantity is excluded from the unit-fill denominator.')
  add('Overlapping flags versus exclusive status','Hsmall');add('The baseline contains 753 orders with an availability shortage, but 687 rows carry the primary status Stock shortage. The remaining 66 shortage orders are blocked and therefore receive the higher-priority Blocked status. Counting primary status and counting shortage flags answer different questions.')
  add('Denominator policy','Hsmall');add('OTIF uses all 1,200 orders and therefore includes the operational effect of blocks. Unit fill rate excludes blocked demand to isolate fulfillable, released demand. These two measures must not be treated as interchangeable service measures.')
 else:
  grid([['Calculation','Rule'],['History window','Latest 28 observations per warehouse-SKU'],['Demand variability','Sample standard deviation (n - 1)'],['Safety stock','1.65 x standard deviation x sqrt(lead time)'],['Reorder point','ceil(mean demand x lead time + safety stock)'],['Target stock','ceil(mean demand x 21 target days + safety stock)'],['Trigger','Latest WMS stock <= reorder point'],['Proposal','max(target stock - WMS stock, 0), only when triggered']],[130,345])
  add('Worked example','Hsmall');add('At mean demand 12 units/day, standard deviation 4 and lead time 7 days, the reorder point is ceil(84 + 17.46) = 102 units. The 21-day target is 270. Stock of 90 triggers a proposal for 180 units. Stock of 120 does not trigger an order, even though it is below target.')
  add('Decision timing','Hsmall');add('Proposals use the final day after closing stock is known. They do not feed back into the receipt simulation. This is a decision snapshot, not a tested replenishment policy. The z value is illustrative and does not establish achieved service probability.')
 #6
 page(6,'Results and interpretation')
 pic('results.png','Figure 1. Baseline results calculated from the committed operational records.',maxheight=230)
 if supply:
  grid([['Warehouse','Orders','Fill rate','OTIF'],*[[r['warehouse'],r['orders'],f"{float(r['fill_rate']):.2%}",f"{float(r['otif_rate']):.2%}"] for r in score]],[160,85,115,115])
  add('The main workload is stock shortage: 687 orders carry this primary status. Another 300 complete, unblocked orders are late. Only 107 orders meet the complete, unblocked and on-time condition. The 1,093-row exception register excludes the 107 On track orders.')
  add('The low OTIF value follows the deliberately difficult simulation distributions. It is not a benchmark for any company. The practical use is testing whether the exception rules and denominator choices produce an auditable queue.')
 else:
  grid([['Warehouse','Discrepancies','Demand','Shipped'],*[[r['warehouse'],r['discrepancies'],f"{r['demand']:,}",f"{r['shipped']:,}"] for r in a['regions']]],[145,110,110,110])
  add('The dataset contains 306 unfulfilled demand units. High aggregate fulfillment does not remove SKU-level risk: Germany SKU005 ends at zero WMS stock and receives a 290-unit proposal. Germany SKU002 receives 179 units. Both final proposal rows have zero ERP/WMS variance.')
  add('The 2,245 discrepancy count describes noisy observations across time, not 2,245 distinct damaged items or stock-loss events. Repeated observations of a SKU must not be interpreted as independent physical losses.')
 #7
 page(7,'Interactive dashboard overview')
 pic('dashboard.png','Figure 2. Actual browser capture of the generated HTML dashboard, baseline run.',maxheight=460)
 add('The overview combines full-dataset KPI cards with warehouse filtering, text search, a comparative bar chart and a detailed register. Its data is embedded in the HTML, so the report opens offline without account access.')
 add('Display precision differs from the calculation exports: the HTML KPI cards show one decimal place for ratios, while KPI JSON preserves four decimal places. This is display rounding, not a calculation difference.')
 #8
 page(8,'Dashboard interaction and audit trail')
 pic('dashboard-germany.png' if supply else 'reconciliation.png','Figure 3. '+('Actual browser capture with the Germany filter applied.' if supply else 'Actual browser capture of the daily inventory reconciliation view.'),maxheight=440)
 add('Warehouse and search filters update the chart and visible detail rows. Summary cards intentionally remain scoped to the complete dataset. The table displays at most 200 matching rows for responsiveness. CSV export includes every matching row, not only the displayed sample.')
 add('In the browser checks, selecting Germany returned records, an unmatched search returned zero rows, and filtered CSV download succeeded. The layout also passed a 390-pixel mobile-width overflow check. The wide detail table remains horizontally scrollable.')
 #9
 page(9,'Power BI model and page layout')
 pic('powerbi-layout.png','Figure 4. Layout diagram derived from PBIR visual coordinates. This is not a Power BI Desktop screenshot.',maxheight=360)
 add('The package includes a PBIP entry point, PBIR report pages and a TMSL model.bim semantic model. Power Query decodes an embedded CSV snapshot, promotes headers and applies explicit data types. DAX measures provide aggregation under report filter context.')
 add('The overview page groups KPI cards, a warehouse slicer and two charts. The detail page exposes '+('order-level exception fields.' if supply else 'replenishment proposals and a separate warehouse slicer. The daily and recommendation tables are independent grains, so each page uses measures from its own table.'))
 add('Verification boundary: JSON schema and field-reference checks cover the source package. Power BI Desktop rendering, refresh and DAX execution remain unverified because the Windows application is unavailable in this environment. No PBIX or Desktop screenshot is represented as tested.')
 #10
 page(10,'Sensitivity and comparative analysis')
 pic('comparison.png','Figure 5. '+('Warehouse-level rates under the baseline simulation.' if supply else 'Weekly demand and shipped units. The final period contains only day 120.'),maxheight=230)
 if supply:
  grid([['Seed','Blocked orders','Fill rate','OTIF'],*[[r['seed'],r['blocked_orders'],f"{r['fill_rate']:.2%}",f"{r['otif_rate']:.2%}"] for r in a['scenario']]],[80,135,130,130])
  add('The alternate-seed runs retain 1,200 orders and identical distributions. Fill rate ranges from 78.26% to 79.32%, while OTIF ranges from 8.67% to 9.75%. This checks that the analysis works beyond one random draw. It is not a statistical confidence interval or a business forecast.')
  add('The warehouse comparison reflects random allocation and sampled conditions. Ranking regions from this artificial dataset is useful for checking scorecard behavior, but not for evaluating real logistics performance.')
 else:
  grid([['Lead time (days)','Reorder alerts','Proposed units'],*[[r['lead_time'],r['alerts'],r['proposed_units']] for r in a['scenarios']]],[160,150,165])
  add('With the same closing stock and demand history, increasing lead time from 3 to 14 days increases the alert count from one to five and proposed units from 280 to 836. The 21-day target horizon remains fixed. This isolates the effect of lead-time demand and safety stock.')
  add('No service-level improvement is estimated from these proposals because they are not simulated as future receipts. A policy comparison would require a forward simulation with supplier lead-time variation, purchase orders and holding-cost assumptions.')
 #11
 page(11,'Implementation excerpts')
 sys.path.insert(0,str(repo/'src'));spec=importlib.util.spec_from_file_location('report_run',repo/'src/run.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 if supply:
  code=inspect.getsource(mod.metrics);add('KPI calculation','Hsmall');story.append(Preformatted('\n'.join(textwrap.fill(line,width=82,subsequent_indent='        ',replace_whitespace=False) if len(line)>82 else line for line in code.splitlines()),styles['Code2']))
  add('The denominator explicitly excludes blocked orders for unit fill rate. OTIF requires all three conditions in a single predicate. Empty input produces zero rather than a division error.')
  add('Power BI measure','Hsmall');story.append(Preformatted('OTIF Rate =\nDIVIDE(\n  CALCULATE(COUNTROWS(orders),\n            orders[on_time_in_full] = TRUE()),\n  COUNTROWS(orders),\n  0\n)',styles['Code2']))
 else:
  add('Reorder threshold','Hsmall');story.append(Preformatted('def reorder_point(mean_daily_demand, daily_std,\n                  lead_time=7, z=1.65):\n    if min(mean_daily_demand, daily_std, lead_time, z) < 0:\n        raise ValueError("Inputs must be nonnegative")\n    return math.ceil(\n        mean_daily_demand * lead_time\n        + z * daily_std * math.sqrt(lead_time)\n    )',styles['Code2']))
  add('Equivalent formatted excerpt of src/run.py. The production function uses the same calculation and rejects negative inputs. The recommendation function adds history selection, target stock and the trigger condition.')
  add('Stock conservation','Hsmall');story.append(Preformatted('shipped = min(erp_stock + received, demand)\nerp_stock += received - shipped\nwms_stock = max(0, erp_stock + measurement_noise)',styles['Code2']));add('The last line illustrates the WMS observation rule. Measurement noise does not change ERP closing stock and is not carried forward as a physical adjustment.')
 sys.path.pop(0)
 add('Code organization','Hsmall');add('src/run.py owns simulation and business rules. src/reporting.py handles CSV and HTML rendering. scripts/analyze.py creates scenario evidence. scripts/build_powerbi.py regenerates the embedded snapshot and report definitions. Tests exercise calculations, edge cases and report generation.')
 #12
 page(12,'Validation and reproducibility')
 grid([['Check','Evidence','Outcome'],['Business-rule tests','Blocked/partial OTIF, quantity bounds and invalid counts' if supply else 'Stock conservation, reorder examples and invalid inputs','Passed'],['Repeat generation','Same seed and arguments reproduce identical exports','Passed'],['Browser interactions','Warehouse filter, empty search, CSV export, mobile width','Passed'],['Report source','PBIR JSON schema and model-field linkage checks','Passed'],['Desktop Power BI','Windows application, refresh and DAX engine','Not executed']],[125,255,95])
 add('Reproduction commands','Hsmall');story.append(Preformatted('python src/run.py\npython scripts/analyze.py\npython scripts/build_powerbi.py\npython -m unittest discover -s tests -v',styles['Code2']))
 add('The default analysis uses the Python standard library. Report authoring dependencies are isolated in requirements-report.txt. PDF charts and tables draw from committed CSV and JSON outputs. Browser screenshots record the generated HTML interface rather than a hand-drawn imitation.')
 add('Cross-checks','Hsmall');add('The total primary-status count equals 1,200. Fulfilled units never exceed ordered or available units. Blocked orders always have zero fulfillment. The exception export contains only non-On track rows. The scorecard partitions the same order population.' if supply else 'All 5,760 rows satisfy ERP stock conservation. Shipments never exceed demand or available ERP stock. The 48-row recommendation table contains one latest proposal per warehouse-SKU pair. Recommended quantity is zero whenever the trigger is false.')
 add('Scope of assurance','Hsmall');add('Passing these checks establishes internal consistency for the stated rules and dataset. It does not establish calibration against a real warehouse, production readiness or economic benefit.')
 #13
 page(13,'Limitations and conclusion')
 add('Model limitations','Hsmall')
 points=['Stock snapshots are independent across orders, so orders do not compete for a shared balance.','Delay and block status are independently sampled. Real causes are often correlated.','No promised calendar date, transport milestone or partial-shipment history exists.','The scenario analysis changes random seeds rather than estimating real uncertainty.'] if supply else ['Lead time is fixed and daily demand is treated as independent.','No open purchase orders, backorders, reservations, MOQ or expiry constraints are modeled.','WMS variance is injected measurement noise, not an inferred reconciliation cause.','Proposals are evaluated at one closing snapshot and not executed in the simulation.']
 for point in points:add('• '+point)
 add('Next engineering priorities','Hsmall');add('An operational extension should introduce validated external data, explicit business definitions, schema checks and exception ownership. '+('A continuous stock ledger and dated shipment events would enable a more realistic service model.' if supply else 'A replenishment policy backtest should model order placement, supplier lead times, receipts and total inventory cost.'))
 add('Conclusion','Hsmall');add('The project provides an auditable chain from simulated observations to decision fields, exports and visual review. '+('Its main contribution is a consistent separation of fulfillment, strict OTIF and exception priority.' if supply else 'Its main contribution is the separation of stock reconciliation from demand-based replenishment decisions.'))
 add('The reported outputs are reproducible and the calculation boundaries are documented. Power BI source is supplied as an editable project, with Desktop verification explicitly separated from the automated source checks.')
 #14
 page(14,'References and artifact index')
 refs=[('Python Software Foundation. random: Generate pseudo-random numbers.','https://docs.python.org/3/library/random.html'),('Python Software Foundation. statistics: Mathematical statistics functions.','https://docs.python.org/3/library/statistics.html'),('Microsoft. Power BI Desktop projects.','https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview'),('Microsoft. Power BI project report folder and PBIR.','https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report'),('Microsoft. Power BI project semantic model folder.','https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset'),('Microsoft. DIVIDE function (DAX).','https://learn.microsoft.com/en-us/dax/divide-function-dax')]
 for i,(label,url) in enumerate(refs,1):add(f'[{i}] {label}<br/><link href="{url}" color="#008579">{url}</link>','Caption2')
 add('Sources consulted 26 October 2026. The inventory policy is an illustrative project assumption. Documentation references support software formats and function behavior, not a claim of real-world model validation.','Caption2')
 add('Artifact index','Hsmall');grid([['Path','Purpose'],['src/','Simulation, calculations and HTML reporting'],['reports/*.csv, *.json','Baseline and scenario evidence'],['reports/dashboard.html','Interactive operational dashboard'],['reports/figures/','Actual browser captures, charts and layout diagram'],['powerbi/','PBIP, PBIR and semantic model source'],['tests/','Automated checks'],['docs/methodology.md','Definitions and assumptions'],['reports/project-report.pdf','This technical report']],[195,280])
 def footer(canvas,doc):
  canvas.saveState();canvas.setStrokeColor(colors.HexColor('#dce4eb'));canvas.line(60,48,535,48);canvas.setFont('Body',8);canvas.setFillColor(colors.HexColor(GRAY));canvas.drawString(60,34,short+' | Ankith Ramesh Babu');canvas.drawRightString(535,34,f'{doc.page} / 14');canvas.restoreState()
 output=repo/'reports/project-report.pdf';doc=SimpleDocTemplate(str(output),pagesize=(595.28,841.89),rightMargin=60,leftMargin=60,topMargin=48,bottomMargin=64,title=title+' | Technical Report',author='Ankith Ramesh Babu');doc.build(story,onFirstPage=footer,onLaterPages=footer);print(output)
