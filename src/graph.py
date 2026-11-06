"""Zone-to-zone trip graph and connected components via DFS, BFS and NetworkX."""

from collections import deque
from typing import Iterable, List, Set, Tuple

import networkx as nx


def build_graph(edges: Iterable[Tuple[int, int]]) -> nx.Graph:
    """Undirected graph: nodes are taxi zones, edge weight = number of trips between them."""
    g = nx.Graph()
    for a, b in edges:
        if a is None or b is None:
            continue
        if g.has_edge(a, b):
            g[a][b]["weight"] += 1
        else:
            g.add_edge(a, b, weight=1)
    return g


def _search(g: nx.Graph, start, use_queue: bool) -> Set:
    frontier = deque([start])
    seen = {start}
    while frontier:
        node = frontier.popleft() if use_queue else frontier.pop()
        for nxt in g[node]:
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(nxt)
    return seen


def components(g: nx.Graph, method: str = "dfs") -> List[Set]:
    """Connected components using our own DFS ('dfs') or BFS ('bfs')."""
    seen: Set = set()
    found = []
    for node in g.nodes:
        if node not in seen:
            comp = _search(g, node, use_queue=(method == "bfs"))
            seen |= comp
            found.append(comp)
    return found
