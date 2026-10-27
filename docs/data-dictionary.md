# Data Dictionary

The committed files are generated simulation outputs. The CLI does not import external operational CSVs.

## warehouse_daily.csv

Grain: One warehouse-SKU-day observation. Baseline rows: 5,760.

| Column | Meaning |
| --- | --- |
| `warehouse` | Warehouse region used for grouping and filtering. |
| `sku` | Synthetic stock-keeping unit identifier. |
| `day` | One-based simulation day, not a calendar date. |
| `opening_stock` | ERP stock before the current day's receipts and shipments. |
| `received` | Receipt quantity for the day. |
| `demand` | Daily requested units. |
| `shipped` | Units shipped, capped by demand and available ERP stock. |
| `erp_stock` | ERP closing stock after receipts and shipments. |
| `wms_stock` | Closing WMS observation, including synthetic measurement noise. |
| `variance` | WMS observation minus ERP closing stock. |

## replenishment_recommendations.csv

Grain: One closing-snapshot proposal per warehouse-SKU. Baseline rows: 48.

| Column | Meaning |
| --- | --- |
| `warehouse` | Warehouse region used for grouping and filtering. |
| `sku` | Synthetic stock-keeping unit identifier. |
| `as_of_day` | Final simulation day used for the proposal. |
| `history_days` | Number of demand observations used, at most 28. |
| `mean_daily_demand` | Mean demand over the retained history. |
| `sample_std` | Sample demand standard deviation, using n - 1. |
| `wms_stock` | Closing WMS observation, including synthetic measurement noise. |
| `reorder_point` | Ceiling of lead-time demand plus safety stock. |
| `target_stock` | Ceiling of target-horizon demand plus safety stock. |
| `reorder_alert` | True when WMS stock is at or below the reorder point. |
| `recommended_order_qty` | Target minus WMS stock, floored at zero and applied only when triggered. |
| `stock_variance` | ERP/WMS difference at the final proposal snapshot. |

## Aggregation Rules

Stock fields are snapshots. Do not sum them across orders or dates as a physical balance. Ratio measures must be recomputed from their numerator and denominator, rather than averaged across groups. Boolean flags overlap unless the methodology defines an exclusive status.

Daily observations and replenishment proposals have different grains. They are separate Power BI tables. A proposal is not an executed purchase order.
