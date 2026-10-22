"""
Testing utilities.

Tools for checking a betweenness centrality function against networkx
across a set of test graphs.
"""

import networkx as nx
import numpy as np


def run_tests(centrality_function, test_graphs):
  """
  Test a betweenness centrality function against networkx.

  For each test graph, checks that invalid inputs (non-graphs or empty
  graphs) raise a ValueError or TypeError, and that valid graphs produce
  the same values as unnormalized nx.betweenness_centrality. Prints PASS
  or FAIL for each case.

  Parameters
  ----------
  centrality_function : callable
      Function taking a graph and returning a {node: value} dict.
  test_graphs : dict
      Mapping of {test name: graph or invalid input}.
  """
  for name, graph in test_graphs.items():

    # Defines error cases
    error_cases = not isinstance(graph, nx.Graph) or graph.number_of_nodes() == 0

    # Tries the centrality function and stores as result
    try:
      result = centrality_function(graph)

      # If error_cases returns True
      if error_cases:  # bad input, but no error raised
        print(name, ": FAIL (expected an error, none raised)")
      else:  # Good input: compare against networkx
        expected = nx.betweenness_centrality(graph, normalized=False)
        if set(result) == set(expected) and np.allclose(
            [result[n] for n in expected], [expected[n] for n in expected], atol=1e-5): # Code taken from Class
          print(name, ": PASS")
        else:
          print(name, ": FAIL (values differ from networkx)")

    except (ValueError, TypeError):  # The function raised an error
      if error_cases:
        print(name, ": PASS (error raised as expected)")
      else:
        print(name, ": FAIL (unexpected error on a valid graph)")
