# KNIME Workflow Specification

The Python implementation is the executable reference. This document specifies an equivalent KNIME flow. A native KNWF export is not included.

## Reconciliation
CSV Reader (`reports/warehouse_daily.csv`) -> Rule Engine (`$variance$ != 0 => TRUE`) -> Row Filter -> CSV Writer. Group by warehouse to compare discrepancy counts. Sum demand and shipped units to calculate fulfillment. Never sum stock snapshots across dates.

## Replenishment
Sort by warehouse, SKU and day. Retain the latest 28 rows per warehouse-SKU. Calculate demand mean and sample standard deviation. Join the latest WMS stock. Apply the reorder point, target stock and trigger definitions in `docs/methodology.md`. Export one proposal per warehouse-SKU.

## Expected Baseline Outputs
Default dataset: 5,760 observations, 2,245 discrepancy rows, 48 proposals, two alerts and 469 proposed units. Compare the output to the committed Python CSVs before using the workflow for further analysis.
