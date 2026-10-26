# Smart Warehouse Intelligence

Inventory reconciliation and SKU-level replenishment analysis across four warehouses, combining daily stock checks with demand-based order proposals.

**Author:** Ankith Ramesh Babu  
**Scope:** Independent case study using synthetic operational data

[Technical report](reports/project-report.pdf) · [Power BI project](powerbi/Warehouse.pbip) · [Methodology](docs/methodology.md)

![Dashboard overview](reports/figures/dashboard.png)

## Results

The baseline contains 5,760 daily observations and 48 warehouse-SKU pairs. It identifies 2,245 ERP/WMS discrepancies, 99.56% demand fulfillment and two final replenishment proposals totaling 469 units. A lead-time sensitivity analysis increases the proposed quantity from 280 units at three days to 836 units at fourteen days.

These results describe the simulation, not an employer operation or measured business savings.

## Deliverables

- [14-page technical report](reports/project-report.pdf): methodology, results, actual dashboard screenshots, Power BI layout, code excerpts, validation and references.
- [Offline HTML dashboard](reports/dashboard.html): warehouse filter, text search and filtered CSV export. Download the repository to open HTML locally.
- [Inventory reconciliation dashboard](reports/reconciliation.html): daily ERP/WMS record review.
- [Power BI source](powerbi/README.md): two report pages, visual definitions, typed semantic model and embedded dataset.
- [Scenario evidence](reports/analysis.json): lead-time sensitivity and regional reconciliation totals.
- [Validation record](docs/validation.json): browser and source validation scope.

## Run

Python 3.11 or newer. The analysis has no third-party dependencies.

```bash
git clone https://github.com/ankithr457/smart-warehouse-intelligence.git
cd smart-warehouse-intelligence
python src/run.py
python scripts/analyze.py
python -m unittest discover -s tests -v
```

Open `reports/dashboard.html`. The HTML works offline. Cards display the full dataset. Chart and table filters apply to matching rows, and the CSV export includes every match.

## Power BI

Open `powerbi/Warehouse.pbip` in Power BI Desktop and refresh the embedded data. No local CSV path is required. The report and model are provided as editable source. JSON schemas, embedded-data identity and visual-field references are validated. Desktop rendering and DAX execution have not been tested here. A PBIX binary is not included.

Regenerate the embedded source after an analysis change:

```bash
python scripts/build_powerbi.py
```

## Analysis parameters

```bash
python src/run.py --days 180 --seed 7 --lead-time 10 --target-days 28 --output reports/scenario
```

## Repository structure

| Directory | Contents |
| --- | --- |
| `src/` | Simulation, calculations, CSV and HTML generation |
| `scripts/` | Scenario analysis, Power BI and PDF report authoring |
| `tests/` | Business rules, edge cases, reproducibility and model checks |
| `reports/` | Baseline outputs, technical report and dashboard screenshots |
| `powerbi/` | PBIP, PBIR, semantic model and DAX measures |
| `docs/` | Methodology and validation record |

## Assumptions

Lead time is fixed, demand variation is independent, and the policy excludes open purchase orders, minimum quantities, expiry and budget constraints. Recommendations are closing-snapshot proposals and are not fed back into the receipt simulation.

The project does not connect to SAP or execute operational transactions. The KNIME directory provides a reproduction specification, not an executed native workflow.
