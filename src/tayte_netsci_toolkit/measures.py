"""
Network measures.

Functions that compute properties of an existing network, such as
node centralities.
"""

from itertools import combinations

import networkx as nx


def betweenness_centrality(T):
    """
    Compute the (unnormalized) betweenness centrality of every node.

    For each pair of nodes (s, t), finds all shortest paths between them
    and credits each intermediate node v with the fraction of those paths
    that pass through v. Endpoints are not counted, and disconnected
    pairs are skipped.

    Parameters
    ----------
    T : networkx.Graph
        An undirected graph.

    Returns
    -------
    betweenness : dict
        Mapping of {node: betweenness value}.

    Raises
    ------
    TypeError
        If T is not a networkx graph.
    ValueError
        If T has no nodes.

    Notes
    -----
    This enumerates all shortest paths explicitly, so it is slow on large
    graphs. For anything beyond a few hundred nodes, use
    nx.betweenness_centrality instead.
    """
    if not isinstance(T, nx.Graph):
        raise TypeError("This is not a networkx object")

    if T.number_of_nodes() == 0:
        raise ValueError("This graph has no nodes!")

    betweenness = {node: 0.0 for node in T.nodes()}

    for s, t in combinations(T.nodes(), 2):
        if not nx.has_path(T, s, t):
            continue
        paths = list(nx.all_shortest_paths(T, s, t))

        for v in T.nodes():
            if v == s or v == t:
                continue
            count = sum(1 for path in paths if v in path)
            betweenness[v] += count / len(paths)

    return betweenness
