# Analytical Methodology

## Metric Definitions
- Stock conservation: closing ERP stock = opening ERP stock + receipts - shipped units.
- Shipments cannot exceed available ERP stock or demand. Unfulfilled demand is lost sales, not carried as backlog.
- WMS variance = WMS snapshot minus ERP stock. Nonzero variance triggers investigation, not an automatic stock correction.
- Demand fulfillment = total shipped units / total demand units.
- Reorder point = ceil(mean demand * lead time + 1.65 * sample standard deviation * sqrt(lead time)).
- Demand statistics use the last 28 daily observations per warehouse and SKU, including the current day. Short histories use available observations and zero standard deviation for a single observation.
- Target stock = ceil(mean demand * target days + the same safety stock).
- Recommend max(target stock - latest WMS stock, 0) only if WMS stock <= reorder point.
- Weekly output uses numbered seven-day simulation periods, not calendar weeks.

## Operational Interpretation
Investigate discrepancies before acting on replenishment proposals. Recommendations are calculated after the simulated day closes and never fed back into receipts. The default run produces two alerts and 469 proposed units.

## Modeling Limitations
Fixed lead time, independent daily demand and illustrative z=1.65. The factor does not establish achieved service. No open purchase orders, reservations, MOQ, expiry, budget or supplier variation. WMS observations include independent measurement noise. A physical inventory ledger would need reconciliation events. Snapshot stocks must not be summed across dates.
