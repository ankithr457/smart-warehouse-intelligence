# Project explanation and interview practice

## Short explanation
This project explores stock reconciliation and replenishment using synthetic operations data. Python generates the data, applies documented business rules and exports a filterable offline dashboard and CSV reports. Fixed seeds make the results reproducible.

## Demonstrate in five minutes
1. Run `python src/run.py` and open `reports/dashboard.html`.
2. Explain the full-dataset cards and filter one warehouse.
3. Search for SKU001 and export the filtered records.
4. Open `docs/methodology.md` and explain one formula with a small example.
5. Run the unit tests and describe one edge case they protect.

## Worked example
Mean demand 12, standard deviation 4, lead time 7: reorder point = ceil(84 + 1.65 * 4 * sqrt(7)) = 102. A 21-day target is ceil(252 + 17.46) = 270. Stock 90 triggers an order proposal of 180 units. Stock 120 triggers no order even though it is below target.

## Questions to practise
- Why separate ERP stock from WMS observations?
- Which assumptions would fail with real operational data?
- How would you validate an imported CSV before analysis?
- Which rule has the largest effect on the output?
- What would you change before connecting an ERP system?

## Next practical exercise
Change the seed and lead time, predict the direction of change, rebuild and explain the result. Read every function in `src/run.py` before discussing implementation in an interview.

Describe your own role and assistance accurately. These are portfolio simulations, not employment projects or measured cost-saving deployments.
