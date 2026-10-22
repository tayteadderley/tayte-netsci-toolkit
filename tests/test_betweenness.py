"""
Test betweenness_centrality against networkx.

Run from the top of the repository, after installing the package:

    python tests/test_betweenness.py
"""

import networkx as nx

from tayte_netsci_toolkit import betweenness_centrality, run_tests


test_graphs = {
    "No nodes": nx.Graph(),
    "Not a graph": [1, 2, 3],
    "No Edges": nx.empty_graph(5),
    "Two Components": nx.disjoint_union(
        nx.connected_caveman_graph(5, 10), nx.barbell_graph(10, 5)
    ),
    "Karate": nx.karate_club_graph(),
    "Women": nx.davis_southern_women_graph(),
}


if __name__ == "__main__":
    run_tests(betweenness_centrality, test_graphs)
