# Power BI reproduction
Import the CSV files from `reports/` after running `python src/run.py`. Use the CSV basename as the table name. Set quantities to whole numbers and flags to Boolean. Add measures from `measures.dax` one at a time and format ratio measures as percentages. Compare cards with `reports/kpis.json`.

Do not sum daily stock snapshots across dates. This repository provides DAX and import instructions, not a tested PBIX file.
