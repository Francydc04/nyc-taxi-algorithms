"""Busiest zone-to-zone routes, read straight off the trip graph's edge weights (images/top_routes.png)."""

from pathlib import Path

import matplotlib.pyplot as plt

from src.graph import build_graph
from src.taxi_data import read_trips, read_zones

ROOT = Path(__file__).parent
TOP = 10
BAR, INK, MUTED, GRID = "#2a78d6", "#1f1f1e", "#6b6a64", "#e4e3de"

trips = read_trips(ROOT / "data" / "trips_100k.csv")
names = read_zones(ROOT / "data" / "taxi_zone_lookup.csv")
g = build_graph((t.pickup_zone, t.dropoff_zone) for t in trips)

routes = sorted(((d["weight"], a, b) for a, b, d in g.edges(data=True)
                 if a != b and a in names and b in names), reverse=True)[:TOP]
labels = [f"{names[a]}  ↔  {names[b]}" for _, a, b in routes][::-1]
values = [w for w, _, _ in routes][::-1]

fig, ax = plt.subplots(figsize=(10, 5.2), dpi=150)
bars = ax.barh(labels, values, color=BAR, height=0.6)
for bar, v in zip(bars, values):
    ax.text(v + 15, bar.get_y() + bar.get_height() / 2, f"{v:,}", va="center", fontsize=9, color=INK)
ax.set_title("Busiest taxi routes between different zones (100,000 trips, 2022)", loc="left", fontsize=13, color=INK, pad=12)
ax.set_xlabel("Trips in either direction", color=MUTED)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="y", length=0, labelsize=10, colors=INK)
ax.tick_params(axis="x", colors=MUTED)
ax.xaxis.grid(True, color=GRID)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(ROOT / "images" / "top_routes.png")
same = sum(d["weight"] for a, b, d in g.edges(data=True) if a == b)
print("same-zone trips:", same, "of", len(trips))
