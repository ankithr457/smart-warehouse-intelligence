# Four-Pass Project Verification

Reviewed on 2026-10-28. Scope: the committed Germany, Czech Republic and India baseline and its project deliverables.

## Pass 1: Execution and Reproducibility

- 15 Python tests pass. The suite runs in the existing GitHub Actions workflow on pushes and pull requests.
- A clean temporary checkout with an unrelated folder name reproduces CSV, JSON, HTML and Power BI source byte for byte.
- Invalid-input, empty-input where supported, hand-calculated business-rule and same-seed reproducibility tests pass.
- A separate 100-seed run preserves stock-conservation and reorder invariants.
- A deliberately corrupted KPI file is rejected by the independent audit.

Finding fixed: `analyze.py` and `build_powerbi.py` selected a project from the checkout directory name. They now use an explicit project identifier. Column types in the Power BI builder are explicit, instead of inferred from the first observation.

## Pass 2: Independent Numbers and Assumptions

The audit uses SQLite queries and direct raw-row arithmetic. It does not import the implementation's KPI or replenishment functions.

- KPI SQL independently reproduces 4,320 observations, 1,671 discrepancies, 99.42% fill, two reorder alerts and 469 proposed units.
- Every daily stock-conservation equation, day-to-day opening balance, variance, discrepancy row and weekly aggregation is checked.
- All 36 proposals are recalculated from the final 28 raw demand observations, including sample standard deviation, ceiling operations and trigger logic.
- Regional totals and all four lead-time scenarios are independently recalculated.
- Fulfillment is 52,131 / 52,437. The 100-seed range is 98.05% to 100%, averaging 99.47%. High fill follows generous receipts and opening stock, not an executed policy improvement.

The existing baseline numbers were retained. No metrics were increased or reduced for presentation. Country names are analytical groups, not calibrated regional operating models.

Evidence: [SQL](../sql/kpis.sql), [numerical audit](../reports/numerical_audit.json), [100-seed results](../reports/robustness_check.json).

## Pass 3: Dashboards and Power BI Source

- Chromium checks pass for all three country filters, zero-result search, downloaded CSV contents and complete row counts, and a 390px viewport without page overflow.
- Both HTML dashboards opens offline without script errors. Screenshots were refreshed from the actual browser.
- Power BI embedded CSV bytes match the committed report files.
- Visual fields resolve to model columns/measures and remain within page bounds.
- All embedded CSV values match the declared model types. The standalone DAX reference matches the model expressions.
- 18 PBIR and definition-property documents pass validation against Microsoft's published JSON schemas.

Boundary: schema/source validation does not execute DAX, Power Query refresh, or Power BI Desktop rendering. Desktop validation remains outstanding. The KNIME directory is a specification, not an executed native KNWF workflow. There is no SAP connection.

## Pass 4: IEEE Report and Repository Consistency

- The six-page IEEEtran PDF was rebuilt and all pages visually inspected.
- Report calculations, tables and result explanations match CSV/JSON outputs. Screenshots depict the current three-country baseline.
- README now separates the operational question, numerical definitions, assumptions, deliverables and verification evidence.
- Internal Markdown links resolve. No obsolete country names or release labels remain in current project text or PDF content.
- PDF layout diagrams are labeled as diagrams, not Power BI Desktop screenshots. No savings, deployed SAP integration or implemented policy improvement is claimed.

## Re-run the Checks

```bash
python -m unittest discover -s tests -v
python scripts/verify_project.py
python scripts/check_robustness.py
python -m pip install -r requirements-validation.txt
python scripts/validate_powerbi_schema.py
```

For browser checks, install Playwright and its Chromium browser, then run `node scripts/capture_dashboards.cjs`. For PDF rebuild instructions, see [IEEE source](ieee/README.md).

`verify_project.py` audits the committed default baseline, including its seven-day lead time and 21-day target for the warehouse project. Alternate parameter runs belong in a separate output folder and need their own expected results. The 100-seed ranges describe these generators, not confidence intervals for a real operation.
