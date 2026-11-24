import matplotlib.pyplot as plt
import networkx as nx

G = nx.read_gexf("skill_network.gexf")

top = sorted(G.nodes(), key=lambda n: -G.degree(n, weight="weight"))[:45]
ai = []
for n in G.nodes():
    if str(G.nodes[n]["is_ai_skill"]) in ["True", "true"]:
        ai.append(n)
H = G.subgraph(set(top) | set(ai)).copy()

keep = set()
for n in H.nodes():
    strongest = sorted(H[n], key=lambda m: -H[n][m]["weight"])[:4]
    for m in strongest:
        keep.add(tuple(sorted([n, m])))
H = H.edge_subgraph(keep).copy()

colors = {1: "royalblue", 2: "orangered", 3: "seagreen"}
names = {1: "1: Analytics & BI", 2: "2: ML engineering", 3: "3: Data engineering & cloud"}

pos = nx.spring_layout(H, weight="weight", seed=7, k=0.9)

fig, ax = plt.subplots(figsize=(11, 8))
weights = [H[u][v]["weight"] for u, v in H.edges()]
widths = [0.3 + 3 * w / max(weights) for w in weights]
nx.draw_networkx_edges(H, pos, ax=ax, width=widths, alpha=0.25, edge_color="dimgray")

for c in colors:
    cluster_nodes = [n for n in H.nodes() if int(H.nodes[n]["community"]) == c]
    sizes = [40 + G.degree(n, weight="weight") / 40 for n in cluster_nodes]
    nx.draw_networkx_nodes(H, pos, nodelist=cluster_nodes, ax=ax, node_color=colors[c],
                           alpha=0.85, label=names[c], node_size=sizes)

labels = {}
for n in H.nodes():
    if n in ai:
        labels[n] = n.upper()
    else:
        labels[n] = n
nx.draw_networkx_labels(H, pos, ax=ax, font_size=7, labels=labels)

ax.legend(loc="lower left", fontsize=9, frameon=False)
ax.set_title("AI-skill co-occurrence network (top skills plus all AI skills; AI skills in capitals)", fontsize=11)
ax.axis("off")
fig.tight_layout()
fig.savefig("network_baseline.png", dpi=200)
plt.show()
