# KNIME workflow implementation guide

This is an implementation guide, **not an executable .knwf file**.

1. Run `python src/run.py` to generate `reports/warehouse_daily.csv`.
2. CSV Reader: load the CSV. Verify numeric types for `day`, `demand`, `shipped`, `erp_stock`, `wms_stock`, `variance`.
3. Rule Engine: flag discrepancies with `$variance$ != 0 => "Investigate"`, `TRUE => "Matched"`.
4. GroupBy: group by `warehouse`, `sku`; sum demand and shipped, count discrepancy flags.
5. Math Formula: calculate `fulfillment_rate = shipped / demand`, guarding against zero demand.
6. Row Filter: retain groups with discrepancy count > 0.
7. CSV Writer: export discrepancy register.
8. Add a Line Plot for daily demand and a Bar Chart for discrepancies by warehouse.

Validation: reconcile KNIME counts against Python output, and document any difference. Do not claim this guide as an exported KNIME workflow.

