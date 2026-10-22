"""
Reading and comparing saved graph files.

Functions for loading graphs from several file formats and checking
which formats preserve a graph's structure and attributes.
"""

import json
import os
import pickle
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd


def load_graph(file_path, directed=False):
    """
    Load a graph from a file, choosing the reader based on the extension.

    Supported formats: .edgelist, .graphml, .json (node-link), .npy
    (adjacency matrix), and .pkl (pickled networkx graph).

    Parameters
    ----------
    file_path : str or pathlib.Path
        Path to the graph file.
    directed : bool, optional
        Whether to build a directed graph for .edgelist and .npy files,
        which don't store directedness themselves. Default False.

    Returns
    -------
    G : networkx.Graph or networkx.DiGraph

    Raises
    ------
    ValueError
        If the file extension is not supported.

    Notes
    -----
    Only load .pkl files you trust; unpickling can run arbitrary code.
    """
    file_path = Path(file_path)
    ext = file_path.suffix.lower()
    graph_type = nx.DiGraph if directed else nx.Graph

    if ext == ".edgelist":
        return nx.read_edgelist(file_path, create_using=graph_type)
    elif ext == ".graphml":
        return nx.read_graphml(file_path)
    elif ext == ".json":
        with open(file_path, "r") as f:
            return nx.node_link_graph(json.load(f))
    elif ext == ".npy":
        return nx.from_numpy_array(np.load(file_path), create_using=graph_type)
    elif ext == ".pkl":
        with open(file_path, "rb") as f:
            return pickle.load(f)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def compare_graph_files(G, folder_path=".", directed=False):
    """
    Load every supported graph file in a folder and compare it to G.

    Useful for checking which file formats preserve a graph's structure,
    directedness, attributes, and node labels.

    Parameters
    ----------
    G : networkx.Graph
        The original graph the files were saved from.
    folder_path : str or pathlib.Path, optional
        Folder to search. Default is the current directory.
    directed : bool, optional
        Passed to load_graph for formats that don't store directedness.

    Returns
    -------
    pandas.DataFrame
        One row per file, with columns for file name, size, node and edge
        counts, directedness, attributes, equality with G, node label
        type, and whether node labels match.
    """
    rows = []
    for file_path in Path(folder_path).iterdir():
        try:
            G_back = load_graph(file_path, directed=directed)
        except ValueError:
            print(f"Skipping unsupported file type: {file_path.name}")
            continue

        rows.append({
            "File Name": file_path.name,
            "File Size": os.path.getsize(file_path),
            "Num Nodes": G_back.number_of_nodes(),
            "Num Edges": G_back.number_of_edges(),
            "Directed?": G_back.is_directed(),
            "Attributes?": any(G_back.nodes.values()),
            "Equal?": nx.utils.graphs_equal(G, G_back),
            "Label Type": (type(next(iter(G_back.nodes()))).__name__
                           if G_back.number_of_nodes() > 0 else None),
            "Labels Match?": set(G.nodes()) == set(G_back.nodes()),
        })

    return pd.DataFrame(rows)
