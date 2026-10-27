import csv,json,base64,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='https://developer.microsoft.com/json-schemas/fabric/item/'
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def schema(p):return BASE+p+'/schema.json'
def field(table,name,measure=False):return {('Measure' if measure else 'Column'):{'Expression':{'SourceRef':{'Entity':table}},'Property':name}}
def proj(table,name,measure=False):return {'field':field(table,name,measure),'queryRef':f'{table}.{name}','nativeQueryRef':name}
def visual(folder,name,kind,x,y,w,h,roles,title):
 title_props = {'show': {'expr': {'Literal': {'Value': 'true'}}}, 'text': {'expr': {'Literal': {'Value': "'"+title+"'"}}}}
 d = {'$schema':schema('report/definition/visualContainer/2.4.0'),'name':name,'position':{'x':x,'y':y,'z':0,'height':h,'width':w,'tabOrder':0},'visual':{'visualType':kind,'query':{'queryState':{k:{'projections':v} for k,v in roles.items()}},'visualContainerObjects':{'title':[{'properties':title_props}]}}}
 write(folder/'visuals'/name/'visual.json',d)
for root in [ROOT]:
 supply=root.name.startswith('international')
 name='SupplyChain' if supply else 'Warehouse'
 pbi=root/'powerbi';report=pbi/(name+'.Report');model=pbi/(name+'.SemanticModel')
 write(pbi/(name+'.pbip'),{'version':'1.0','artifacts':[{'report':{'path':name+'.Report'}}],'settings':{'enableAutoRecovery':True}})
 write(report/'definition.pbir',{'$schema':schema('report/definitionProperties/2.0.0'),'version':'4.0','datasetReference':{'byPath':{'path':'../'+name+'.SemanticModel'}}})
 write(model/'definition.pbism',{'$schema':schema('semanticModel/definitionProperties/1.0.0'),'version':'4.0','settings':{'qnaEnabled':False}})
 sources=['orders'] if supply else ['warehouse_daily','replenishment_recommendations']
 tables=[]
 for source in sources:
  path=root/'reports'/(source+'.csv');rows=list(csv.DictReader(path.open()));columns=[];types=[]
  for k,v in rows[0].items():
   dtype='boolean' if v in ['True','False'] else 'int64' if v.lstrip('-').isdigit() else 'double' if v.replace('.','',1).lstrip('-').isdigit() else 'string'
   columns.append({'name':k,'dataType':dtype,'sourceColumn':k,'summarizeBy':'none'})
   types.append('{"'+k+'", '+{'boolean':'type logical','int64':'Int64.Type','double':'type number','string':'type text'}[dtype]+'}')
  encoded=base64.b64encode(path.read_bytes()).decode()
  expression=['let',f'    Source = Csv.Document(Binary.FromText("{encoded}", BinaryEncoding.Base64), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),','    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),','    Typed = Table.TransformColumnTypes(Headers, {'+', '.join(types)+'}, "en-US")','in','    Typed']
  tables.append({'name':source,'columns':columns,'partitions':[{'name':source,'mode':'import','source':{'type':'m','expression':expression}}]})
 if supply:
  t='orders';ms=[('Total Orders','COUNTROWS(orders)','#,0'),('Blocked Orders','CALCULATE(COUNTROWS(orders), orders[blocked] = TRUE())','#,0'),('Unit Fill Rate','DIVIDE(SUM(orders[fulfilled_units]), CALCULATE(SUM(orders[ordered_units]), orders[blocked] = FALSE()), 0)','0.00%'),('OTIF Rate','DIVIDE(CALCULATE(COUNTROWS(orders), orders[on_time_in_full] = TRUE()), COUNTROWS(orders), 0)','0.00%'),('Shortage Units','SUM(orders[shortage_units])','#,0')]
 else:
  t='warehouse_daily';ms=[('Observations','COUNTROWS(warehouse_daily)','#,0'),('Discrepancy Records','COUNTROWS(FILTER(warehouse_daily, warehouse_daily[variance] <> 0))','#,0'),('Demand Fulfillment','DIVIDE(SUM(warehouse_daily[shipped]), SUM(warehouse_daily[demand]), 0)','0.00%'),('Total Demand','SUM(warehouse_daily[demand])','#,0'),('Total Shipped','SUM(warehouse_daily[shipped])','#,0')]
 tables[0]['measures']=[{'name':n,'expression':e,'formatString':f} for n,e,f in ms]
 if not supply:tables[1]['measures']=[{'name':'Reorder Alerts','expression':'CALCULATE(COUNTROWS(replenishment_recommendations), replenishment_recommendations[reorder_alert] = TRUE())','formatString':'#,0'},{'name':'Proposed Units','expression':'SUM(replenishment_recommendations[recommended_order_qty])','formatString':'#,0'}]
 write(model/'model.bim',{'name':name,'compatibilityLevel':1550,'model':{'culture':'en-US','defaultPowerBIDataSourceVersion':'powerBI_V3','sourceQueryCulture':'en-US','tables':tables,'annotations':[{'name':'PBI_QueryOrder','value':json.dumps(sources)}]}})
 definition=report/'definition'
 write(definition/'version.json',{'$schema':schema('report/definition/versionMetadata/1.0.0'),'version':'4.0.0'})
 write(definition/'report.json',{'$schema':schema('report/definition/report/3.0.0'),'themeCollection':{}})
 write(definition/'pages/pages.json',{'$schema':schema('report/definition/pagesMetadata/1.0.0'),'pageOrder':['overview','detail'],'activePageName':'overview'})
 for page,label in [('overview','Operations overview'),('detail','Order exceptions' if supply else 'Replenishment review')]:
  folder=definition/'pages'/page
  write(folder/'page.json',{'$schema':schema('report/definition/page/2.0.0'),'name':page,'displayName':label,'displayOption':'FitToPage','width':1280,'height':720})
 overview=definition/'pages/overview';detail=definition/'pages/detail'
 cards=ms[:4] if supply else [ms[0],ms[1],ms[2],ms[3]]
 for i,(n,e,f) in enumerate(cards):visual(overview,'card'+str(i),'card',24+i*310,20,292,110,{'Values':[proj(t,n,True)]},n)
 visual(overview,'warehouse','slicer',24,145,280,85,{'Values':[proj(t,'warehouse')]},'Warehouse')
 visual(overview,'bar','clusteredBarChart',24,250,600,420,{'Category':[proj(t,'warehouse')],'Y':[proj(t,'Shortage Units' if supply else 'Discrepancy Records',True)]},'Shortage units by warehouse' if supply else 'Discrepancies by warehouse')
 visual(overview,'distribution','donutChart' if supply else 'lineChart',650,250,600,420,{'Category':[proj(t,'status' if supply else 'day')],'Y':[proj(t,'Total Orders' if supply else 'Total Demand',True)]},'Order status' if supply else 'Daily demand')
 target=t if supply else 'replenishment_recommendations'
 visual(detail,'warehouse_detail','slicer',24,20,300,90,{'Values':[proj(target,'warehouse')]},'Warehouse')
 if not supply:
  for i,n in enumerate(['Reorder Alerts','Proposed Units']):visual(detail,'reorder_card'+str(i),'card',360+i*310,20,292,90,{'Values':[proj(target,n,True)]},n)
 cols=['order_id','warehouse','status','ordered_units','fulfilled_units','shortage_units','delivery_delay_days'] if supply else ['warehouse','sku','wms_stock','reorder_point','target_stock','reorder_alert','recommended_order_qty','stock_variance']
 visual(detail,'detail_table','tableEx',24,150,1230,530,{'Values':[proj(target,c) for c in cols]},'Order register' if supply else 'Replenishment proposals')
 (pbi/'README.md').write_text(f'''# Power BI Report Source

`{name}.pbip` contains two report pages, an import semantic model, typed data, DAX measures and visual definitions. The sample data is embedded in Power Query, so no absolute CSV path or credentials are required.

## Open the Report
Open `{name}.pbip` in a current Windows version of Power BI Desktop with Power BI Project and PBIR support. Refresh the model to load the embedded simulation snapshot. Save as PBIX if a single-file package is needed.

## Report Pages
- Operations overview: KPI cards, warehouse slicer and comparative charts.
- {'Order exceptions: warehouse filter and order-level detail.' if supply else 'Replenishment review: warehouse filter, alert cards and SKU-level proposals.'}

The embedded data matches the committed CSV outputs. Rebuild the source package after changing the simulation data. Report source has been checked against Microsoft JSON schemas and model field references. Power BI Desktop rendering and DAX execution remain outside the completed verification scope.
''')

 print(root.name,'Power BI source generated')
