# Country network: are a project's countries neighbours?

A small tool that asks one question of a multi-country project: **are its countries neighbours?**

It was written to test a hypothesis in development finance: projects spanning neighbouring countries may move money more slowly, because political tension between neighbours can hold up approvals, transfers or spending. Classifying each project's countries by how connected they are makes that testable, for example by plotting disbursement against project maturity for each group.

## How it works

Countries are nodes in a graph, and an edge joins two neighbouring countries (`data/borders.csv`, ISO3 codes). For a project's list of countries:

| Code | Label | Meaning |
|---|---|---|
| 0 | SingleCountry | one country only |
| 1 | StrongRegional | the countries form one connected block of neighbours |
| 2 | WeakRegional | every country is within two steps of at least one other |
| 999 | MultiRegional | at least one country is further away than that |

```python
from connectivity import load_graph, classify

G = load_graph()
classify(G, ["KEN", "TZA", "UGA"])   # 'StrongRegional'
classify(G, ["KEN", "RWA"])          # 'WeakRegional' (Uganda sits between them)
classify(G, ["KEN", "BRA"])          # 'MultiRegional'
```

Apply it to a table of projects with pandas:

```python
project_df["Connectivity"] = project_df["Countries"].apply(lambda c: classify(G, c))
```

`docs/border_graph.html` is an interactive view of the neighbour graph (open it in a browser; click a country to highlight its neighbours).

## The maths

**Countries as a graph.** The border data defines a graph G = (V, E): each country or territory is a node in V, and each pair of neighbours is an edge in E (243 nodes, 588 edges).

**StrongRegional: a connected induced subgraph.** For a project's set of countries S, take the induced subgraph G[S]: the nodes in S and only the edges between them. S is StrongRegional if G[S] is connected, meaning there is a path between every pair of countries in S that never leaves S. `networkx.is_connected` tests this with a breadth-first search from one node, visiting neighbours level by level, and checks whether every node was reached. Cost: O(|S| + edges within S).

**WeakRegional: distance at most two.** Let d(u, v) be the shortest path length between u and v in the full graph G (paths may pass through countries outside S). S is WeakRegional if

    for every u in S there exists v in S, v != u, with d(u, v) <= 2

The code computes the radius two neighbourhood N(u) ∪ N(N(u)) with set unions, then intersects it with S \ {u}. An empty intersection means u is isolated.

**Edge case.** The WeakRegional rule asks only that each country has one partner within two steps. Two separate clusters therefore pass: Kenya + Uganda + Brazil + Argentina is classified WeakRegional. A stricter rule would require S to be connected in the square of the graph, G², where countries at distance two or less are joined.

**The picture.** `docs/border_graph.html` was generated with pyvis, which wraps the vis-network JavaScript library. Its layout is a force-directed physics simulation: edges act as springs pulling neighbours together, all nodes repel each other, and the layout settles into regional clusters.

## Notes on the data

- `data/borders.csv` has 588 neighbour pairs across 243 countries and territories. It includes some sea neighbours and overseas territories, so a few pairs will look surprising. Check the pairs that matter for your projects.
- Self links in the source data were removed.
- Changes from the first version: the graph is passed in explicitly; a country code missing from the graph can no longer be silently dropped and scored as connected; repeated codes are ignored.

## Run the tests

```
pip install networkx pytest
pytest
```

## Credits

Classification algorithm by a colleague. Packaged, tested and applied to disbursement analysis by Onki Wong. Explainer: [owangie.github.io/writing/neighbours-graph-theory](https://owangie.github.io/writing/neighbours-graph-theory/).
