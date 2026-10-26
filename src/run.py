"""Synthetic warehouse reconciliation and replenishment. Not production advice."""
from pathlib import Path
import random
import csv
import math

WAREHOUSES = ("Germany", "Hong Kong", "Taiwan", "Malaysia")

def simulate(days=120, seed=43):
    rng = random.Random(seed)
    rows = []
    for warehouse in WAREHOUSES:
        for sku in range(1, 13):
            erp_stock = rng.randint(120, 500)
            for day in range(days):
                demand = rng.randint(2, 22)
                received = rng.choice((0, 0, 0, 40, 80))
                shipped = min(erp_stock + received, demand)
                erp_stock += received - shipped
                wms_stock = max(0, erp_stock + rng.choice((-3, 0, 0, 0, 2)))
                rows.append({"warehouse": warehouse, "sku": f"SKU{sku:03d}", "day": day + 1,
                             "demand": demand, "shipped": shipped, "erp_stock": erp_stock,
                             "wms_stock": wms_stock, "variance": wms_stock - erp_stock})
    return rows

def reorder_point(mean_daily_demand, daily_std, lead_time=7, z=1.65):
    return math.ceil(mean_daily_demand * lead_time + z * daily_std * math.sqrt(lead_time))

def main():
    rows = simulate()
    output = Path(__file__).resolve().parents[1] / "reports"
    output.mkdir(exist_ok=True)
    with (output / "warehouse_daily.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    print(f"Simulated observations: {len(rows)}; stock variances: {sum(r['variance'] != 0 for r in rows)}")
    print(f"Illustrative reorder point (mean demand 12, std 4): {reorder_point(12, 4)}")

if __name__ == "__main__": main()
