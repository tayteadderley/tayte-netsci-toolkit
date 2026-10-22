"""
Network and degree-sequence generators.

Functions for growing Barabási-Albert networks and for building the
degree sequences used in configuration models and the LFR benchmark.
"""

import networkx as nx
import numpy as np


def barabasi_albert_model(N, m, size):
    """
    Grow a network by preferential attachment (Barabási-Albert model).

    Starts from a complete graph of N nodes and adds nodes one at a time,
    each connecting to m existing nodes chosen with probability
    proportional to their degree.

    Parameters
    ----------
    N : int
        Number of nodes in the initial complete graph.
    m : int
        Number of edges each new node adds.
    size : int
        Target network size.

    Returns
    -------
    G : networkx.Graph
        The grown network.
    deg_seq_list : list of lists
        Degree sequences (sorted, descending) saved when the network
        reaches 100, 1,000, and 10,000 nodes.
    """
    G = nx.complete_graph(N)
    num_nodes = N
    deg_seq_list = []

    while num_nodes <= size:
        total_degree = (2 * G.number_of_edges())

        for i in G.nodes():
            G.nodes[i]["prob"] = G.degree(i) / total_degree

        candidates = list(G.nodes())
        p = [G.nodes[i]["prob"] for i in candidates]
        targets = np.random.choice(candidates, replace=False, size=m, p=p)

        G.add_node(num_nodes)
        for i in targets:
            G.add_edge(num_nodes, i)

        num_nodes = num_nodes + 1

        if num_nodes in [100, 1000, 10000]:
            degree_sequence = sorted([d for n, d in G.degree()], reverse=True)
            deg_seq_list.append(degree_sequence)

    return G, deg_seq_list


def barabasi_albert_model_sequence(N, m, size):
    """
    Grow a Barabási-Albert network and return its final degree sequence.

    Starts from a complete graph of N nodes and adds nodes one at a time,
    each connecting to m existing nodes chosen with probability
    proportional to their degree.

    Parameters
    ----------
    N : int
        Number of nodes in the initial complete graph.
    m : int
        Number of edges each new node adds.
    size : int
        Target network size.

    Returns
    -------
    degree_sequence : list of int
        Degrees of the final network, sorted in descending order.
    """
    H = nx.complete_graph(N)
    num_nodes = N

    while num_nodes < size:
        candidates = list(H.nodes())
        degrees = np.array([H.degree(i) for i in candidates])
        p = degrees / degrees.sum()
        targets = np.random.choice(candidates, replace=False, size=m, p=p)

        H.add_node(num_nodes)
        for i in targets:
            H.add_edge(num_nodes, i)

        num_nodes = num_nodes + 1

    degree_sequence = sorted([d for n, d in H.degree()], reverse=True)
    return degree_sequence


def powerlaw_degree_sequence(N, gamma, avg_k):
    """
    Generate a power-law degree sequence for use in a configuration model.

    Degrees are drawn from p(k) ∝ k^(-gamma) by inverse transform
    sampling, with the minimum degree set so the expected average degree
    is avg_k. Values are rounded to integers and clipped to [1, N-1], and
    the sum is made even so the sequence can be realized as a graph.

    Parameters
    ----------
    N : int
        Number of nodes.
    gamma : float
        Power-law exponent. Must be greater than 2.
    avg_k : float
        Target average degree.

    Returns
    -------
    list of int
        Degree sequence of length N with an even sum.

    Raises
    ------
    ValueError
        If gamma <= 2.

    Notes
    -----
    Rounding and clipping mean the realized average degree is only
    approximately avg_k, especially for gamma close to 2. This is the
    degree-sampling step (Step 1) of the LFR benchmark.
    """
    if gamma <= 2:
        raise ValueError("gamma must be greater than 2 for a finite average degree.")

    kmin = avg_k * (gamma - 2) / (gamma - 1)
    u = np.random.random(N)
    k = kmin * (1 - u) ** (-1 / (gamma - 1))
    k = np.clip(np.round(k), 1, N - 1).astype(int)

    if k.sum() % 2 == 1:
        eligible = np.where(k < N - 1)[0]
        k[np.random.choice(eligible)] += 1

    return k.tolist()


def split_degrees(degree_sequence, mu):
    """
    Split each node's degree into internal and external parts.

    Following Step 2 of the LFR benchmark, each node keeps a fraction
    (1 - mu) of its degree for edges inside its community and the
    remaining fraction mu for edges to other communities.

    Parameters
    ----------
    degree_sequence : list of int
        Total degree of each node.
    mu : float
        Mixing parameter, between 0 and 1. Higher values mean more edges
        between communities and weaker community structure.

    Returns
    -------
    internal : list of int
        Internal degree of each node, round((1 - mu) * k).
    external : list of int
        External degree of each node, k - internal.

    Raises
    ------
    ValueError
        If mu is not between 0 and 1.
    """
    if not 0 <= mu <= 1:
        raise ValueError("mu must be between 0 and 1.")

    k = np.asarray(degree_sequence)
    internal = np.round((1 - mu) * k).astype(int)
    external = k - internal
    return internal.tolist(), external.tolist()
