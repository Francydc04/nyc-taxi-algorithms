"""Benchmark the six sorting algorithms and the three graph searches on NYC taxi data.

Run:  python benchmark.py
Writes results/*.csv and images/*.png (takes about 2 minutes).
"""

import csv
import math
import random
import statistics
import time
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import networkx as nx

from src.graph import build_graph, components
from src.sorting import ALGORITHMS, QUADRATIC
from src.taxi_data import read_trips, valid_values

ROOT = Path(__file__).parent
SIZES = [500, 1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 99_000]
QUADRATIC_MAX = 20_000  # beyond this a single bubble-sort run takes minutes
COLORS = {  # fixed categorical order, validated for colour-vision deficiency
    "Bubble sort": "#2a78d6", "Selection sort": "#eb6834", "Insertion sort": "#1baf7a",
    "Merge sort": "#eda100", "Quick sort": "#e87ba4", "Heap sort": "#008300",
}
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3de"
random.seed(42)


def time_it(fn, values, repeats):
    runs = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn(values)
        runs.append(time.perf_counter() - start)
    return statistics.median(runs)


def style(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=10)
    ax.grid(True, which="major", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def sorting_benchmark(totals):
    rows = []
    for n in SIZES:
        sample = totals[:n]
        for name, fn in ALGORITHMS.items():
            if name in QUADRATIC and n > QUADRATIC_MAX:
                continue
            repeats = 3 if name in QUADRATIC else 7
            rows.append({"algorithm": name, "n": n, "seconds": time_it(fn, sample, repeats)})
            print(f"{name:15s} n={n:>6}  {rows[-1]['seconds']:.4f}s")
    return rows


def plot_runtime(rows):
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
    ends = {}
    for name in COLORS:
        pts = [(r["n"], r["seconds"]) for r in rows if r["algorithm"] == name]
        ends[name] = pts[-1]
    label_y = {}
    for name in sorted(ends, key=lambda k: ends[k][1], reverse=True):  # nudge end labels apart
        y = ends[name][1]
        same_x = [label_y[o] for o in label_y if ends[o][0] == ends[name][0]]
        while any(abs(math.log10(y) - math.log10(o)) < 0.15 for o in same_x):
            y /= 10 ** 0.03
        label_y[name] = y
    for name, color in COLORS.items():
        pts = [(r["n"], r["seconds"]) for r in rows if r["algorithm"] == name]
        xs, ys = zip(*pts)
        dashed = name in QUADRATIC
        ax.plot(xs, ys, color=color, linewidth=2, linestyle="--" if dashed else "-",
                marker="o", markersize=5, label=name + (" (O(n²))" if dashed else " (O(n log n))"))
        ax.annotate(name, (xs[-1], label_y[name]), xytext=(8, 0), textcoords="offset points",
                    va="center", fontsize=10, color=INK)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Number of trips sorted (log scale)", color=INK)
    ax.set_ylabel("Runtime in seconds (log scale)", color=INK)
    ax.set_title("Sorting taxi fares: quadratic algorithms hit a wall", loc="left",
                 fontsize=14, color=INK, pad=14)
    ax.set_xlim(right=SIZES[-1] * 3.2)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    style(ax)
    ax.legend(frameon=False, fontsize=9, loc="upper left", labelcolor=INK)
    fig.tight_layout()
    fig.savefig(ROOT / "images" / "runtime_vs_size.png")
    plt.close(fig)


def input_shape_experiment(trips, totals, n=10_000):
    """Same size, different data: does the shape of the input change the winner?"""
    shapes = {
        "Random fares": totals[:n],
        "Passenger counts (7 distinct values)": valid_values(trips, "passengers")[:n],
        "Already sorted (descending)": sorted(totals[:n], reverse=True),
    }
    rows = []
    for shape, values in shapes.items():
        for name in ("Bubble sort", "Insertion sort", "Quick sort", "Merge sort"):
            reps = 3 if name in QUADRATIC else 7
            rows.append({"input": shape, "algorithm": name,
                         "seconds": time_it(ALGORITHMS[name], values, reps)})
    return rows


def graph_benchmark(trips):
    g = build_graph((t.pickup_zone, t.dropoff_zone) for t in trips)
    results = {
        "Own DFS": time_it(lambda _: components(g, "dfs"), None, 50),
        "Own BFS": time_it(lambda _: components(g, "bfs"), None, 50),
        "NetworkX": time_it(lambda _: list(nx.connected_components(g)), None, 50),
    }
    sizes = sorted((len(c) for c in components(g)), reverse=True)
    return g, results, sizes


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    trips = read_trips(ROOT / "data" / "trips_100k.csv")
    totals = valid_values(trips, "total")
    random.shuffle(totals)

    sort_rows = sorting_benchmark(totals)
    write_csv(ROOT / "results" / "sorting_runtime.csv", sort_rows)
    plot_runtime(sort_rows)

    shape_rows = input_shape_experiment(trips, totals)
    write_csv(ROOT / "results" / "input_shape.csv", shape_rows)

    g, graph_times, comp_sizes = graph_benchmark(trips)
    write_csv(ROOT / "results" / "graph_search.csv",
              [{"method": k, "seconds": v} for k, v in graph_times.items()])
    for label, path in [("5k", "trips_5k.csv"), ("30k", "trips_30k.csv"), ("100k", "trips_100k.csv")]:
        sub = read_trips(ROOT / "data" / path)
        gg = build_graph((t.pickup_zone, t.dropoff_zone) for t in sub)
        print(f"components {label}: zones={gg.number_of_nodes()} routes={gg.number_of_edges()} comps={sorted((len(c) for c in components(gg)), reverse=True)}")
    print("graph:", g.number_of_nodes(), "zones,", g.number_of_edges(), "routes, components:", comp_sizes)
    print(graph_times)
    print(shape_rows)
