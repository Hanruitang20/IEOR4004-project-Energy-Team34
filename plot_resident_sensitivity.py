"""Draw the Section 6 sensitivity figures from results/sensitivity_resident/sensitivity_comparison.csv.

Usage: python plot_resident_sensitivity.py results/sensitivity_resident
"""
import sys, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
R = Path(sys.argv[1]); OUT = R / "figures"; OUT.mkdir(exist_ok=True)
d = pd.read_csv(R / "sensitivity_comparison.csv")
B1, B2, INK, INK2, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.titlecolor": INK,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "axes.grid.axis": "y",
    "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True, "figure.dpi": 200})

def save(fig, name):
    fig.tight_layout(); fig.savefig(OUT / name, bbox_inches="tight", facecolor="white"); plt.close(fig)

# Figure 3: budget
b = d[d.group.eq("budget")].sort_values("budget_usd")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.6, 3.4))
x = b.budget_usd / 1e6
a1.plot(x, b.service_rate * 100, color=B1, lw=2, marker="o", ms=6)
for xi, yi in zip(x, b.service_rate * 100):
    a1.annotate(f"{yi:.1f}%", (xi, yi), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8.5, color=INK)
a1.set_xlabel("Budget ($ millions)"); a1.set_ylabel("Projected demand served (%)")
a1.set_title("Service rate", loc="left", fontsize=10.5); a1.set_ylim(55, 71); a1.set_xticks(x)
a1.set_xticklabels([f"{v:g}" for v in x])
labels = [f"${v:g}M" for v in x]
a2.bar(labels, b.investment_usd / 1e6, color=B1, width=0.6, label="Invested")
a2.bar(labels, b.unused_budget_usd / 1e6, bottom=b.investment_usd / 1e6, color="#b7d0ef", width=0.6, label="Unused")
a2.set_ylabel("$ millions"); a2.set_xlabel("Budget"); a2.set_title("Invested vs unused budget", loc="left", fontsize=10.5)
a2.legend(frameon=False, fontsize=8.5, loc="upper left")
save(fig, "fig3_budget.png")

# Figure 4: curbside cost vs ports
c = d[d.group.eq("curbside_cost")].sort_values("curbside_site_cost_usd")
fig, ax = plt.subplots(figsize=(6.6, 3.4))
lab = [f"${v/1000:.0f}k" for v in c.curbside_site_cost_usd]; import numpy as np
i = np.arange(len(c)); w = 0.38
ax.bar(i - w/2 - 0.01, c.curbside_ports, w, color=B1, label="Curbside ports")
ax.bar(i + w/2 + 0.01, c.municipal_ports, w, color=B2, label="Municipal ports")
for xi, v in zip(i - w/2, c.curbside_ports): ax.text(xi, v + 6, f"{v}", ha="center", fontsize=8, color=INK)
for xi, v in zip(i + w/2, c.municipal_ports): ax.text(xi, v + 6, f"{v}", ha="center", fontsize=8, color=INK)
ax.set_xticks(i); ax.set_xticklabels(lab); ax.set_xlabel("Curbside cost per four-port site")
ax.set_ylabel("New ports"); ax.legend(frameon=False, fontsize=8.5, loc="upper right"); ax.set_ylim(0, 560)
save(fig, "fig4_curbside_cost_ports.png")

# Figure 5: equity weight
e = d[d.group.eq("equity")].sort_values("equity_lambda")
fig, ax = plt.subplots(figsize=(6.6, 3.4)); i = np.arange(len(e))
ax.bar(i - w/2 - 0.01, e.high_shortage_service_rate * 100, w, color=B1, label="High-shortage tracts (reference $g_i=1$)")
ax.bar(i + w/2 + 0.01, e.other_tracts_service_rate * 100, w, color=B2, label="All other tracts")
for xi, v in zip(i - w/2, e.high_shortage_service_rate * 100): ax.text(xi, v + 1.5, f"{v:.1f}%", ha="center", fontsize=8, color=INK)
for xi, v in zip(i + w/2, e.other_tracts_service_rate * 100): ax.text(xi, v + 1.5, f"{v:.1f}%", ha="center", fontsize=8, color=INK)
ax.set_xticks(i); ax.set_xticklabels([f"λ = {v:g}" for v in e.equity_lambda]); ax.set_ylim(0, 112)
ax.set_ylabel("Projected demand served (%)"); ax.legend(frameon=False, fontsize=8.5, loc="upper left", ncol=2)
save(fig, "fig5_equity_weight.png")

# Figure 6: radius (optional)
r = d[d.group.eq("radius")].sort_values("service_radius_miles")
fig, ax = plt.subplots(figsize=(6.6, 3.4)); xr = r.service_radius_miles
ax.plot(xr, r.service_rate * 100, color=B1, lw=2, marker="o", ms=6, label="All tracts")
ax.plot(xr, r.high_shortage_service_rate * 100, color=B2, lw=2, marker="s", ms=6, label="High-shortage tracts (reference $g_i=1$)")
for xi, yi in zip(xr, r.service_rate * 100): ax.annotate(f"{yi:.1f}%", (xi, yi), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8, color=INK)
for xi, yi in zip(xr, r.high_shortage_service_rate * 100): ax.annotate(f"{yi:.1f}%", (xi, yi), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=8, color=INK)
ax.set_xticks(xr); ax.set_xlabel("Service radius (miles)"); ax.set_ylabel("Projected demand served (%)"); ax.set_ylim(0, 100)
ax.legend(frameon=False, fontsize=8.5, loc="lower right")
save(fig, "fig6_radius.png")
print(sorted(p.name for p in OUT.iterdir()))
