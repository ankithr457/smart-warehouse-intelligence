"""Synthetic warehouse reconciliation and replenishment analysis."""
from pathlib import Path
import random
import math
import statistics
import json
import argparse
from collections import defaultdict
from reporting import write_csv, dashboard

PROJECT_KIND = "warehouse"

WAREHOUSES = ("Germany", "Czech Republic", "India")

def simulate(days=120, seed=43):
    if days < 1:
        raise ValueError("Days must be at least 1")
    rng = random.Random(seed)
    rows = []
    for warehouse in WAREHOUSES:
        for sku in range(1, 13):
            erp_stock = rng.randint(120, 500)
            for day in range(days):
                opening_stock = erp_stock
                demand = rng.randint(2, 22)
                received = rng.choice((0, 0, 0, 0, 30, 50))
                shipped = min(erp_stock + received, demand)
                erp_stock += received - shipped
                wms_stock = max(0, erp_stock + rng.choice((-3, 0, 0, 0, 2)))
                rows.append({"warehouse": warehouse, "sku": f"SKU{sku:03d}", "day": day + 1,
                             "opening_stock": opening_stock, "received": received, "demand": demand, "shipped": shipped, "erp_stock": erp_stock,
                             "wms_stock": wms_stock, "variance": wms_stock - erp_stock})
    return rows

def reorder_point(mean_daily_demand, daily_std, lead_time=7, z=1.65):
    if min(mean_daily_demand, daily_std, lead_time, z) < 0:
        raise ValueError("Replenishment inputs must be nonnegative")
    return math.ceil(mean_daily_demand * lead_time + z * daily_std * math.sqrt(lead_time))

def recommendations(rows, lead_time=7, target_days=21, window=28):
    if lead_time < 0 or target_days < lead_time or window < 2:
        raise ValueError("Require nonnegative lead time, target >= lead time, window >= 2")
    groups = defaultdict(list)
    for row in rows:
        groups[(row["warehouse"], row["sku"])].append(row)
    result = []
    for (warehouse, sku), group in sorted(groups.items()):
        history = sorted(group, key=lambda r: r["day"])[-window:]
        demands = [r["demand"] for r in history]
        mean = statistics.mean(demands)
        std = statistics.stdev(demands) if len(demands) > 1 else 0
        latest = history[-1]
        safety = 1.65 * std * math.sqrt(lead_time)
        point = reorder_point(mean, std, lead_time)
        target = math.ceil(mean * target_days + safety)
        stock = latest["wms_stock"]
        alert = stock <= point
        result.append({"warehouse": warehouse, "sku": sku, "as_of_day": latest["day"], "history_days": len(history), "mean_daily_demand": round(mean, 3), "sample_std": round(std, 3), "wms_stock": stock, "reorder_point": point, "target_stock": target, "reorder_alert": alert, "recommended_order_qty": max(0, target-stock) if alert else 0, "stock_variance": latest["variance"]})
    return result


def build(output, days=120, seed=43, lead_time=7, target_days=21):
    rows = simulate(days, seed)
    recs = recommendations(rows, lead_time, target_days)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    discrepancies = [r for r in rows if r["variance"] != 0]
    write_csv(output / "warehouse_daily.csv", rows)
    write_csv(output / "erp_wms_discrepancies.csv", discrepancies, list(rows[0]))
    write_csv(output / "replenishment_recommendations.csv", recs)
    weekly = defaultdict(lambda: {"demand": 0, "shipped": 0, "discrepancy_records": 0})
    for r in rows:
        w = weekly[(r["day"] - 1) // 7 + 1]
        w["demand"] += r["demand"]
        w["shipped"] += r["shipped"]
        w["discrepancy_records"] += r["variance"] != 0
    write_csv(output / "weekly_kpis.csv", [{"week": k, **v, "fill_rate": round(v["shipped"] / v["demand"], 4) if v["demand"] else 0} for k, v in sorted(weekly.items())])
    total_demand = sum(r["demand"] for r in rows)
    kpis = {"observations": len(rows), "discrepancy_records": len(discrepancies), "unit_fill_rate": round(sum(r["shipped"] for r in rows) / total_demand, 4) if total_demand else 0, "reorder_alerts": sum(r["reorder_alert"] for r in recs), "recommended_units": sum(r["recommended_order_qty"] for r in recs)}
    (output / "kpis.json").write_text(json.dumps(kpis, indent=2) + "\n")
    dashboard(output / "dashboard.html", "Smart Warehouse Intelligence", "ERP/WMS reconciliation and replenishment proposals based on the latest 28 days of simulated demand.",
              {"Daily observations": len(rows), "Discrepancies": len(discrepancies), "Demand fulfillment": f"{kpis['unit_fill_rate']:.1%}", "Reorder alerts": kpis["reorder_alerts"]}, recs, "warehouse", "recommended_order_qty")
    audit_rows = [{**r, "discrepancy_flag": int(r["variance"] != 0)} for r in rows]
    dashboard(output / "reconciliation.html", "Inventory Reconciliation", "Daily ERP and WMS snapshots with warehouse filters and a searchable discrepancy register.",
              {"Observations": len(rows), "Discrepancies": len(discrepancies), "Discrepancy rate": f"{len(discrepancies)/len(rows):.2%}", "Lost demand units": sum(r["demand"]-r["shipped"] for r in rows)}, audit_rows, "warehouse", "discrepancy_flag")
    return kpis


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=120)
    parser.add_argument("--seed", type=int, default=43)
    parser.add_argument("--lead-time", type=int, default=7)
    parser.add_argument("--target-days", type=int, default=21)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "reports")
    args = parser.parse_args()
    try:
        kpis = build(args.output, args.days, args.seed, args.lead_time, args.target_days)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(kpis, indent=2))
    print(f"Dashboard: {args.output / 'dashboard.html'}")


if __name__ == "__main__":
    main()
