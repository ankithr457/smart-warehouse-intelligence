"""Regenerate report charts from the committed analysis exports (requires matplotlib)."""
from pathlib import Path
import csv
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / 'reports'
FIGURES = REPORTS / 'figures'
COLORS = ['#007f73', '#3279b7', '#c18b28', '#a14854']
plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})

def records(name):
    with (REPORTS / name).open() as stream:
        return list(csv.DictReader(stream))

def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIGURES / name, dpi=180, facecolor='white')
    plt.close(fig)

def main():
    analysis = json.loads((REPORTS / 'analysis.json').read_text())
    if 'status' in analysis:
        fig, ax = plt.subplots(figsize=(7, 3.5))
        labels = ['Blocked', 'Stock shortage', 'Late', 'On track']
        bars = ax.barh(labels, [analysis['status'][s] for s in labels], color=COLORS)
        ax.bar_label(bars, padding=4)
        ax.set_xlim(0, max(analysis['status'].values()) * 1.18)
        ax.set_xlabel('Orders')
        ax.set_title('Order exception workload')
        save(fig, 'results.png')
        rows = records('warehouse_scorecard.csv')
        fig, ax = plt.subplots(figsize=(7, 3.5))
        x = list(range(len(rows)))
        for offset, key, label, color in [(-.19, 'fill_rate', 'Unit fill rate', COLORS[0]), (.19, 'otif_rate', 'OTIF', COLORS[1])]:
            bars = ax.bar([i+offset for i in x], [100*float(r[key]) for r in rows], width=.36, label=label, color=color)
            ax.bar_label(bars, fmt='%.2f', padding=3, fontsize=9)
        ax.set_xticks(x, [r['warehouse'] for r in rows])
        ax.set_ylim(0, 110)
        ax.set_ylabel('Percent')
        ax.legend(loc='upper right', frameon=False, ncol=2)
        save(fig, 'comparison.png')
    else:
        rows = analysis['regions']
        fig, ax = plt.subplots(figsize=(7, 3.5))
        bars = ax.bar([r['warehouse'] for r in rows], [r['discrepancies'] for r in rows], color=COLORS[:3])
        ax.bar_label(bars, padding=4)
        ax.set_ylim(0, max(r['discrepancies'] for r in rows)*1.2)
        ax.set_ylabel('Daily observations with a discrepancy')
        ax.set_title('ERP/WMS reconciliation workload')
        save(fig, 'results.png')
        rows = records('weekly_kpis.csv')
        fig, ax = plt.subplots(figsize=(7, 3.5))
        for key, label, color, style in [('demand', 'Demand', COLORS[0], '-'), ('shipped', 'Shipped', COLORS[1], '--')]:
            ax.plot([int(r['week']) for r in rows], [int(r[key]) for r in rows], style, label=label, color=color, linewidth=2)
        ax.set_xlabel('Simulation week (week 18 contains one day)')
        ax.set_ylabel('Units')
        ax.legend(frameon=False)
        save(fig, 'comparison.png')

if __name__ == '__main__':
    main()
