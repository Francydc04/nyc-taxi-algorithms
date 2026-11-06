import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.graph import build_graph, components  # noqa: E402


def test_components_match_networkx():
    g = build_graph([(1, 2), (2, 3), (1, 2), (4, 5), (6, 6), (7, None)])
    assert g[1][2]["weight"] == 2
    expected = sorted(map(sorted, nx.connected_components(g)))
    for method in ("dfs", "bfs"):
        assert sorted(map(sorted, components(g, method))) == expected
