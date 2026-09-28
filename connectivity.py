"""Classify multi-country projects by how connected their countries are.

Countries are nodes in a graph; an edge joins two countries that are
neighbours in data/borders.csv. A project's countries are then classified as:

    0    SingleCountry   one country only
    1    StrongRegional  the countries form one connected block of neighbours
    2    WeakRegional    every country is within two steps of another one
    999  MultiRegional   at least one country is further away than that
"""

import csv
from pathlib import Path

import networkx as nx

LABELS = {0: "SingleCountry", 1: "StrongRegional", 2: "WeakRegional", 999: "MultiRegional"}

BORDERS = Path(__file__).parent / "data" / "borders.csv"


def load_graph(path=BORDERS):
    """Build an undirected graph of neighbouring countries (ISO3 codes)."""
    G = nx.Graph()
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            G.add_edge(row["iso3_a"], row["iso3_b"])
    return G


def connected_within_two(G, nodes):
    """True if every country can reach at least one other in the set within two steps."""
    for u in nodes:
        if u not in G:
            return False
        # neighbours (distance 1)
        neigh = set(G.neighbors(u))
        # neighbours of neighbours (distance 2)
        two_step = set()
        for n in neigh:
            two_step.update(G.neighbors(n))

        # candidates reachable within 2 steps
        reachable = neigh | two_step

        # check if u can reach at least one other node in the set
        if not (set(nodes) - {u}) & reachable:
            return False

    return True


def check_connection(G, countries):
    """Return 0, 1, 2 or 999 for a list of ISO3 country codes (see module docstring)."""
    countries = list(dict.fromkeys(countries))
    if len(countries) == 1:
        return 0

    H = G.subgraph(countries)

    # every country must be in the graph, otherwise subgraph() silently drops it
    if len(H) == len(countries) and nx.is_connected(H):
        return 1
    elif connected_within_two(G, countries):
        return 2
    else:
        return 999


def classify(G, countries):
    """Same as check_connection, but returns the label."""
    return LABELS[check_connection(G, countries)]


if __name__ == "__main__":
    G = load_graph()
    examples = [["KEN"], ["KEN", "TZA", "UGA"], ["KEN", "RWA"], ["KEN", "BRA"]]
    for countries in examples:
        print(", ".join(countries), "->", classify(G, countries))
