# Smart Warehouse Intelligence

Operations analytics portfolio by Ankith Ramesh Babu.

Reconcile ERP and WMS stock snapshots, examine demand fulfillment and prepare SKU-level replenishment proposals.

All records are synthetic. This is an independent learning case study, with no employer data or live SAP connection.

## Quick start
Requires Python 3.11 or newer. No third-party packages or credentials.

```bash
git clone https://github.com/ankithr457/smart-warehouse-intelligence.git
cd smart-warehouse-intelligence
python src/run.py
python -m unittest discover -s tests -v
```

Open `reports/dashboard.html` in a browser. It works offline. Filter by warehouse, search any field and export matching records. Top cards show the full dataset, while charts and tables follow filters.

## Included outputs
`reports/` contains warehouse_daily.csv, erp_wms_discrepancies.csv, replenishment_recommendations.csv, weekly_kpis.csv, kpis.json, dashboard.html.

The default run creates 5,760 observations: 4 warehouses x 12 SKUs x 120 days, seed 43.

```bash
python src/run.py --days 180 --seed 7 --lead-time 10 --target-days 28 --output reports/scenario
```

## Project structure
- `src/run.py`: deterministic simulation, analysis and command-line interface.
- `src/reporting.py`: CSV exports and self-contained dashboard.
- `tests/`: calculation, edge case, reproducibility and report integration checks.
- `docs/methodology.md`: formulas, assumptions and limits.
- `docs/interview-guide.md`: technical explanation and practice questions.
- `powerbi/`: matching DAX measures and import instructions.
- `knime/`: manual workflow reproduction guide.

## Results and scope
Default: 2,245 discrepancy observations, 99.56% demand fulfillment and two reorder alerts.
These numbers describe the included simulation. They do not measure real company performance or validated savings.

Native Power BI `.pbix` and KNIME `.knwf` files are not included. Guides and DAX have not been executed in those desktop applications.
