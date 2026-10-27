# Power BI Report Source

`Warehouse.pbip` contains two report pages, an import semantic model, typed data, DAX measures and visual definitions. The sample data is embedded in Power Query, so no absolute CSV path or credentials are required.

## Open the Report
Open `Warehouse.pbip` in a current Windows version of Power BI Desktop with Power BI Project and PBIR support. Refresh the model to load the embedded simulation snapshot. Save as PBIX if a single-file package is needed.

## Report Pages
- Operations overview: KPI cards, warehouse slicer and comparative charts.
- Replenishment review: warehouse filter, alert cards and SKU-level proposals.

The embedded data matches the committed CSV outputs. Rebuild the source package after changing the simulation data. Report source has been checked against Microsoft JSON schemas and model field references. Power BI Desktop rendering and DAX execution remain outside the completed verification scope.
