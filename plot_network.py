from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

ROOT = Path(__file__).resolve().parent
G = nx.read_gexf(ROOT / "skill_network.gexf")
top = sorted(G, key=lambda n: -G.degree(n, weight="weight"))[:45]
ai = [n for n in G if G.nodes[n].get("is_ai_skill") in (True, "true", "True")]
H = G.subgraph(set(top) | set(ai)).copy()
keep = set()
for n in H:
    for m, _ in sorted(H[n].items(), key=lambda kv: -kv[1]["weight"])[:4]:
        keep.add(tuple(sorted((n, m))))
H = H.edge_subgraph(keep).copy()

colors = {1: "#2a6fdb", 2: "#d9480f", 3: "#2b8a3e"}
names = {1: "1: Analytics & BI", 2: "2: ML engineering", 3: "3: Data engineering & cloud"}
pos = nx.spring_layout(H, weight="weight", seed=7, k=0.9)
fig, ax = plt.subplots(figsize=(11, 8))
w = [H[u][v]["weight"] for u, v in H.edges()]
nx.draw_networkx_edges(H, pos, ax=ax, width=[0.3 + 3 * x / max(w) for x in w], alpha=0.25, edge_color="#555")
for c, col in colors.items():
    ns = [n for n in H if int(H.nodes[n]["community"]) == c]
    nx.draw_networkx_nodes(H, pos, nodelist=ns, ax=ax, node_color=col, alpha=0.85, label=names[c],
                           node_size=[40 + G.degree(n, weight="weight") / 40 for n in ns],
                           node_shape="o")
nx.draw_networkx_labels(H, pos, ax=ax, font_size=7,
                        labels={n: (n.upper() if n in ai else n) for n in H})
ax.legend(loc="lower left", fontsize=9, frameon=False)
ax.set_title("AI-skill co-occurrence network (top skills plus all AI skills; AI skills in capitals)", fontsize=11)
ax.axis("off")
fig.tight_layout()
fig.savefig(ROOT / "network_baseline.png", dpi=200)
