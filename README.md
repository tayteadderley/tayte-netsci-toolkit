# tayte-netsci-toolkit

Reusable network science functions from NETS/PHYS 7052 (Computational Methods for Network Science, Fall 2026, Prof. Brennan Klein). The toolkit collects code written for my class assignments into one installable package: graph and degree-sequence generators, a betweenness centrality implementation, tools for loading and comparing saved graph files, and a test runner for centrality functions. Version 0.2.0 coming soon!

## Installation

Install directly from GitHub with pip:

```bash
pip install git+https://github.com/tayteadderley/tayte-netsci-toolkit.git
```

Or clone the repository and install it locally:

```bash
git clone https://github.com/tayteadderley/tayte-netsci-toolkit.git
cd tayte-netsci-toolkit
pip install .
```

Requires Python 3.9 or newer. pip installs the dependencies (networkx, numpy, and pandas) automatically.

## Quick start

```python
import networkx as nx
import tayte_netsci_toolkit as tnt

# Generate a power-law degree sequence and build a configuration model
k = tnt.powerlaw_degree_sequence(N=1000, gamma=2.5, avg_k=6)
G = nx.configuration_model(k)

# Split each node's degree into within- and between-community parts
k_in, k_out = tnt.split_degrees(k, mu=0.3)

# Compute betweenness centrality on a small graph
bc = tnt.betweenness_centrality(nx.karate_club_graph())
```

## Package structure

| Module | Functions | Purpose |
|---|---|---|
| `generators` | `barabasi_albert_model`, `barabasi_albert_model_sequence`, `powerlaw_degree_sequence`, `split_degrees` | Create networks and degree sequences |
| `measures` | `betweenness_centrality` | Compute properties of existing networks |
| `readwrite` | `load_graph`, `compare_graph_files` | Load graphs from files and compare file formats |
| `testing` | `run_tests` | Check a centrality function against networkx |

All functions can be imported directly from the package, for example `from tayte_netsci_toolkit import split_degrees`. Every function also has a full docstring, viewable with `help()`, such as `help(tnt.split_degrees)`.

## Function reference

### Generators

#### `barabasi_albert_model(N, m, size)`

Grows a network by preferential attachment, following the Barabási-Albert model. It starts from a complete graph of `N` nodes and adds nodes one at a time; each new node connects to `m` existing nodes, chosen with probability proportional to their degree. Along the way, it saves the network's degree sequence when it reaches 100, 1,000, and 10,000 nodes.

- **Parameters:** `N` (int), the size of the initial complete graph; `m` (int), the number of edges each new node adds; `size` (int), the target network size.
- **Returns:** a tuple `(G, deg_seq_list)`, where `G` is the grown `networkx.Graph` and `deg_seq_list` is a list of degree sequences (each sorted in descending order) saved at the 100, 1,000, and 10,000 node checkpoints.

```python
G, snapshots = tnt.barabasi_albert_model(N=4, m=4, size=10000)
```

Note that the checkpoints are fixed, so a smaller `size` returns fewer snapshots.

#### `barabasi_albert_model_sequence(N, m, size)`

Grows a Barabási-Albert network the same way, but returns only the final degree sequence rather than the graph and snapshots. This is useful when generating many networks, such as an ensemble for estimating a degree exponent, where only the degrees are needed.

- **Parameters:** same as `barabasi_albert_model`.
- **Returns:** a list of ints, the final network's degrees sorted in descending order.

```python
degrees = tnt.barabasi_albert_model_sequence(N=4, m=4, size=10000)
```

#### `powerlaw_degree_sequence(N, gamma, avg_k)`

Generates a degree sequence following a power law, p(k) ∝ k^(-gamma), for use in a configuration model. Degrees are drawn by inverse transform sampling, with the minimum degree chosen so the expected average degree is `avg_k`. Values are rounded to integers and clipped to the range 1 to N−1, and the sequence's sum is made even so it can be realized as a graph. This is Step 1 of the LFR benchmark.

- **Parameters:** `N` (int), the number of nodes; `gamma` (float), the power-law exponent, which must be greater than 2; `avg_k` (float), the target average degree.
- **Returns:** a list of `N` ints with an even sum.
- **Raises:** `ValueError` if `gamma <= 2`.

```python
k = tnt.powerlaw_degree_sequence(N=1000, gamma=2.5, avg_k=6)
G = nx.configuration_model(k)
```

Because of rounding and clipping, the realized average degree is only approximately `avg_k`. For gamma below 3, the distribution's heavy tail also makes the sample average vary noticeably between runs.

#### `split_degrees(degree_sequence, mu)`

Splits each node's degree into internal edges (within its community) and external edges (to other communities), following Step 2 of the LFR benchmark. Each node keeps round((1 − mu) × k) internal edges, and the rest are external, so the two parts always add up to the original degree.

- **Parameters:** `degree_sequence` (list of int), each node's total degree; `mu` (float), the mixing parameter between 0 and 1, where higher values mean weaker community structure.
- **Returns:** a tuple `(internal, external)` of two lists of ints.
- **Raises:** `ValueError` if `mu` is not between 0 and 1.

```python
k = tnt.powerlaw_degree_sequence(N=1000, gamma=2.5, avg_k=6)
k_in, k_out = tnt.split_degrees(k, mu=0.3)
```

### Measures

#### `betweenness_centrality(T)`

Computes the unnormalized betweenness centrality of every node in an undirected graph. For each pair of nodes, it finds all shortest paths between them and credits each intermediate node with the fraction of those paths that pass through it. Endpoints aren't counted, and pairs with no path between them are skipped.

- **Parameters:** `T` (`networkx.Graph`), an undirected graph.
- **Returns:** a dict mapping each node to its betweenness value.
- **Raises:** `TypeError` if `T` is not a networkx graph; `ValueError` if `T` has no nodes.

```python
G = nx.karate_club_graph()
bc = tnt.betweenness_centrality(G)

# Matches networkx's unnormalized betweenness
expected = nx.betweenness_centrality(G, normalized=False)
```

This implementation lists every shortest path explicitly, which makes the algorithm easy to follow but slow on large graphs. For anything beyond a few hundred nodes, use `nx.betweenness_centrality` instead.

### Reading and comparing files

#### `load_graph(file_path, directed=False)`

Loads a graph from a file, choosing the right reader based on the file extension. Supported formats are `.edgelist`, `.graphml`, `.json` (node-link format), `.npy` (adjacency matrix), and `.pkl` (pickled networkx graph).

- **Parameters:** `file_path` (str or `pathlib.Path`), the file to load; `directed` (bool, default `False`), whether to build a directed graph for `.edgelist` and `.npy` files, which don't record directedness themselves.
- **Returns:** a `networkx.Graph` or `networkx.DiGraph`.
- **Raises:** `ValueError` if the file extension isn't supported.

```python
G = tnt.load_graph("network.graphml")
D = tnt.load_graph("network.edgelist", directed=True)
```

Only load `.pkl` files from sources you trust, since unpickling a file can run arbitrary code.

#### `compare_graph_files(G, folder_path=".", directed=False)`

Loads every supported graph file in a folder and compares each one to an original graph `G`. This is useful for checking which file formats preserve a network's structure, directedness, attributes, and node labels when saved and reloaded. Unsupported files are skipped with a printed message.

- **Parameters:** `G` (`networkx.Graph`), the original graph the files were saved from; `folder_path` (str or `pathlib.Path`, default the current folder), where to look; `directed` (bool, default `False`), passed to `load_graph`.
- **Returns:** a pandas DataFrame with one row per file and columns for file name, file size, node and edge counts, directedness, whether attributes are present, whether the graph equals `G`, node label type, and whether node labels match `G`'s.

```python
table = tnt.compare_graph_files(G, "saved_graphs/", directed=True)
```

### Testing

#### `run_tests(centrality_function, test_graphs)`

Tests a betweenness centrality function against networkx's unnormalized `nx.betweenness_centrality`. For each test case, it checks that invalid inputs (non-graphs or empty graphs) raise a `ValueError` or `TypeError`, and that valid graphs produce matching values (within a tolerance of 1e-5). It prints PASS or FAIL for each case.

- **Parameters:** `centrality_function` (callable), a function that takes a graph and returns a `{node: value}` dict; `test_graphs` (dict), mapping test names to graphs or invalid inputs.
- **Returns:** nothing; results are printed.

```python
test_graphs = {
    "No nodes": nx.Graph(),
    "Not a graph": [1, 2, 3],
    "Karate": nx.karate_club_graph(),
}
tnt.run_tests(tnt.betweenness_centrality, test_graphs)
```

## Running the tests

After cloning and installing the package, run the betweenness tests from the top of the repository:

```bash
python tests/test_betweenness.py
```

All six test cases should print PASS. They cover an empty graph, an invalid input, a graph with no edges, a disconnected graph, Zachary's karate club, and the Davis Southern Women network.

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.
