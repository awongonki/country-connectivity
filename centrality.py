"""Centrality and communities in the neighbour graph.

Betweenness centrality (Freeman 1977), Louvain communities (Blondel et al. 2008)
and modularity, drawn as one figure. Run: python centrality.py
"""
from pathlib import Path
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

plt.rcParams["font.family"] = "Georgia"
INK, GREY = "#1b1b1b", "#8a8a8a"
PALETTE = ["#1f3a5f", "#b08d57", "#2f5d50", "#8c3b3b", "#5b6fa3", "#c9a56b", "#6b8f71", "#9a6a8f", "#3f7f8f", "#a0794e"]

G = nx.Graph()
with open(Path(__file__).parent / "data" / "borders.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["iso3_a"] != r["iso3_b"]:
            G.add_edge(r["iso3_a"], r["iso3_b"])

comps = sorted(nx.connected_components(G), key=len, reverse=True)
H = G.subgraph(comps[0]).copy()
print("nodes", G.number_of_nodes(), "edges", G.number_of_edges(), "components", len(comps), "largest", H.number_of_nodes())

deg = dict(H.degree())
btw = nx.betweenness_centrality(H)
pr = nx.pagerank(H)
comms = sorted(nx.community.louvain_communities(H, seed=7), key=len, reverse=True)
Q = nx.community.modularity(H, comms)
cid = {n: i for i, c in enumerate(comms) for n in c}
print("communities", len(comms), "modularity", round(Q, 3), [len(c) for c in comms])
print("diameter", nx.diameter(H), "avg path", round(nx.average_shortest_path_length(H), 2))

top_b = sorted(btw, key=btw.get, reverse=True)[:10]
top_d = sorted(deg, key=deg.get, reverse=True)[:10]
print("top betweenness", [(n, round(btw[n], 3), deg[n]) for n in top_b])
print("top degree", [(n, deg[n]) for n in top_d])

pos = nx.spring_layout(H, seed=11, k=0.18, iterations=400)

fig = plt.figure(figsize=(13, 8.2), dpi=200)
ax = fig.add_axes([0.0, 0.06, 0.68, 0.84]); ax.axis("off")
colors = [PALETTE[cid[n]] if cid[n] < len(PALETTE) else "#bbbbbb" for n in H]
sizes = [20 + 2600 * btw[n] for n in H]
nx.draw_networkx_edges(H, pos, ax=ax, edge_color="#c9c9c9", width=0.6)
nx.draw_networkx_nodes(H, pos, ax=ax, node_color=colors, node_size=sizes, linewidths=0.6, edgecolors="white")
for n in top_b:
    dx = {"GRC": -0.06, "FRA": 0.05}.get(n, 0)
    ax.text(pos[n][0] + dx, pos[n][1] + 0.035, n, ha="center", fontsize=8.5, color=INK, weight="bold")

fig.text(0.02, 0.955, "Which countries hold the neighbour network together?", fontsize=18, color=INK)
fig.text(0.02, 0.918, f"{H.number_of_nodes()} countries and territories linked by shared borders. Colour = community (Louvain, modularity {Q:.2f}); size = betweenness centrality.",
         fontsize=10, color=GREY, style="italic")

# side table: betweenness vs degree
tx = fig.add_axes([0.70, 0.12, 0.28, 0.74]); tx.axis("off")
tx.text(0, 1.0, "Bridges, not just hubs", fontsize=12.5, color=INK, va="top")
tx.text(0, 0.955, "Top 10 by betweenness: the share of shortest\npaths between other countries that pass through it", fontsize=8.8, color=GREY, style="italic", va="top")
tx.text(0.02, 0.86, "Country", fontsize=9, color=GREY); tx.text(0.45, 0.86, "Betweenness", fontsize=9, color=GREY); tx.text(0.82, 0.86, "Borders", fontsize=9, color=GREY)
for i, n in enumerate(top_b):
    y = 0.80 - i * 0.068
    tx.add_patch(plt.Rectangle((0.45, y - 0.012), 0.24 * btw[n] / btw[top_b[0]], 0.035, color=PALETTE[cid[n]] if cid[n] < len(PALETTE) else "#bbbbbb"))
    tx.text(0.02, y, n, fontsize=10, color=INK)
    tx.text(0.80, y, f"{btw[n]:.2f}", fontsize=9, color=INK, ha="right")
    tx.text(0.9, y, str(deg[n]), fontsize=10, color=INK, ha="center")
fig.text(0.02, 0.025, "All 238 countries and territories form one connected network, because the data also includes some sea neighbours (for example the United States and Russia across the Bering Strait). "
         "Data and code: github.com/awongonki/country-connectivity. networkx 3; Blondel et al. (2008) for Louvain; Freeman (1977) for betweenness.",
         fontsize=7.8, color=GREY, style="italic", wrap=True)
fig.savefig(Path(__file__).parent / "docs" / "neighbour_network_centrality.png", facecolor="white")
print("saved")
