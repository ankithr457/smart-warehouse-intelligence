-- Daily observations and closing recommendations have different grains.
SELECT
  (SELECT COUNT(*) FROM warehouse_daily) AS observations,
  (SELECT COUNT(*) FROM warehouse_daily WHERE wms_stock <> erp_stock) AS discrepancy_records,
  (SELECT ROUND(1.0 * SUM(shipped) / NULLIF(SUM(demand), 0), 4) FROM warehouse_daily) AS unit_fill_rate,
  (SELECT COUNT(*) FROM replenishment_recommendations WHERE wms_stock <= reorder_point) AS reorder_alerts,
  (SELECT SUM(CASE WHEN wms_stock <= reorder_point THEN MAX(target_stock - wms_stock, 0) ELSE 0 END)
    FROM replenishment_recommendations) AS recommended_units;
