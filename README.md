# Smart Warehouse Intelligence

A reproducible warehouse reconciliation and replenishment portfolio case study using synthetic data.

## Features
- 4 warehouses, 12 SKUs and 120 days, totaling 5,760 observations
- ERP versus WMS stock discrepancy checks
- Demand, receipts and shipment simulation
- Illustrative reorder point using lead-time demand and safety stock
- CSV export and unit tests

## Run
```bash
python src/run.py
python -m unittest discover -s tests -v
```

The published Python code uses only the standard library. `requirements.txt` lists pandas for possible extensions.

## Scope and limitations
All data are synthetic. No live SAP, native Power BI PBIX or executable KNIME workflow is included. The inventory planning assumptions are simplified and are not production-ready.
