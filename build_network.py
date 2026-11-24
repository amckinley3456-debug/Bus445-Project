import json
import pandas as pd
import networkx as nx
from networkx.algorithms import bipartite
from skills import parse_posting, is_ai

MIN_SUPPORT = 30
MIN_EDGE = 10
SEED = 42

skills_df = pd.read_csv("job_skills.csv")
postings_df = pd.read_csv("job_postings.csv", usecols=["job_link", "company", "job_title"])

df = skills_df.merge(postings_df, on="job_link")
n_raw = len(df)

df["key"] = df["company"].str.lower().str.strip() + "|" + df["job_title"].str.lower().str.strip()
df = df.drop_duplicates(subset="key").reset_index(drop=True)
n_total = len(df)

df["skills"] = df["job_skills"].apply(parse_posting)

has_ai = []
for skills in df["skills"]:
    found = False
    for skill in skills:
        if is_ai(skill):
            found = True
    has_ai.append(found)
df["has_ai"] = has_ai
ai = df[df["has_ai"]].reset_index(drop=True)
n_ai = len(ai)
print("postings:", n_raw, "after removing duplicates:", n_total, "with an AI skill:", n_ai)

support = {}
for skills in ai["skills"]:
    for skill in skills:
        if skill in support:
            support[skill] = support[skill] + 1
        else:
            support[skill] = 1

keep = []
for skill in support:
    if support[skill] >= MIN_SUPPORT:
        keep.append(skill)
keep = sorted(keep)

B = nx.Graph()
for i in range(n_ai):
    B.add_node("p" + str(i), bipartite=0)
for skill in keep:
    B.add_node(skill, bipartite=1)
for i in range(n_ai):
    for skill in sorted(ai["skills"][i]):
        if skill in keep:
            B.add_edge("p" + str(i), skill)

B.remove_nodes_from(list(nx.isolates(B)))

skill_nodes = []
for skill in keep:
    if skill in B:
        skill_nodes.append(skill)
full = bipartite.weighted_projected_graph(B, skill_nodes)
full_density = nx.density(full)

G = nx.Graph()
for u, v, d in sorted(full.edges(data=True)):
    shared = d["weight"]
    lift = n_ai * shared / (support[u] * support[v])
    if shared >= MIN_EDGE and lift > 1:
        G.add_edge(u, v, weight=shared, lift=round(lift, 3), distance=1 / shared)
G.remove_nodes_from(list(nx.isolates(G)))
print("skills:", G.number_of_nodes(), "links:", G.number_of_edges())

degree_c = nx.degree_centrality(G)
strength = dict(G.degree(weight="weight"))
betweenness = nx.betweenness_centrality(G, weight="distance", normalized=True)
eigenvector = nx.eigenvector_centrality_numpy(G, weight="weight")

comms = nx.community.louvain_communities(G, weight="weight", seed=SEED)
Q = nx.community.modularity(G, comms, weight="weight")
print("clusters:", len(comms), "modularity:", round(Q, 4))

q_runs = []
for s in range(10):
    c = nx.community.louvain_communities(G, weight="weight", seed=s)
    q_runs.append(nx.community.modularity(G, c, weight="weight"))

Gu = nx.Graph(G.edges())
q_real_u = nx.community.modularity(Gu, nx.community.louvain_communities(Gu, seed=SEED))
q_null = []
for s in range(5):
    R = Gu.copy()
    nx.double_edge_swap(R, nswap=10 * R.number_of_edges(), max_tries=10**6, seed=s)
    q_null.append(nx.community.modularity(R, nx.community.louvain_communities(R, seed=SEED)))
print("modularity real:", round(q_real_u, 4), "random:", round(sum(q_null) / len(q_null), 4))

comms = sorted(comms, key=lambda c: -sum(strength[n] for n in c))
comm_of = {}
for k in range(len(comms)):
    for skill in comms[k]:
        comm_of[skill] = k + 1

rows = []
for skill in G.nodes():
    rows.append({
        "skill": skill,
        "is_ai_skill": is_ai(skill),
        "postings": support[skill],
        "pct_of_ai_postings": round(100 * support[skill] / n_ai, 1),
        "degree": G.degree(skill),
        "degree_centrality": round(degree_c[skill], 4),
        "weighted_degree": strength[skill],
        "betweenness": round(betweenness[skill], 4),
        "eigenvector": round(eigenvector[skill], 4),
        "community": comm_of[skill],
    })
nodes = pd.DataFrame(rows).sort_values("eigenvector", ascending=False)
nodes.to_csv("nodes.csv", index=False)

rows = []
for u, v, d in G.edges(data=True):
    rows.append({"source": u, "target": v, "cooccurrences": d["weight"], "lift": d["lift"]})
edges = pd.DataFrame(rows).sort_values("cooccurrences", ascending=False)
edges.to_csv("edges.csv", index=False)

rows = []
for k in range(len(comms)):
    members = sorted(comms[k], key=lambda n: -strength[n])
    ai_members = []
    for m in members:
        if is_ai(m):
            ai_members.append(m)
    rows.append({
        "community": k + 1,
        "size": len(members),
        "ai_skills": ", ".join(ai_members),
        "top_members": ", ".join(members[:12]),
    })
pd.DataFrame(rows).to_csv("communities.csv", index=False)

summary = {
    "postings_raw": n_raw,
    "postings_after_dedup": n_total,
    "postings_with_ai_skill": n_ai,
    "pct_with_ai_skill": round(100 * n_ai / n_total, 1),
    "distinct_skills_in_ai_postings": len(support),
    "nodes_after_support_filter": full.number_of_nodes(),
    "edges_unfiltered_projection": full.number_of_edges(),
    "density_unfiltered_projection": round(full_density, 4),
    "nodes_final": G.number_of_nodes(),
    "ai_skill_nodes_final": int(nodes["is_ai_skill"].sum()),
    "edges_final": G.number_of_edges(),
    "density_final": round(nx.density(G), 4),
    "connected_components": nx.number_connected_components(G),
    "avg_clustering_weighted": round(nx.average_clustering(G, weight="weight"), 4),
    "louvain_communities": len(comms),
    "modularity_weighted_seed42": round(Q, 4),
    "modularity_range_10_seeds": [round(min(q_runs), 4), round(max(q_runs), 4)],
    "modularity_unweighted_real": round(q_real_u, 4),
    "modularity_unweighted_rewired_mean": round(sum(q_null) / len(q_null), 4),
    "params": {"MIN_SUPPORT": MIN_SUPPORT, "MIN_EDGE": MIN_EDGE, "lift_threshold": 1, "seed": SEED},
}
with open("summary.json", "w") as f:
    json.dump(summary, f, indent=2)

for skill in G.nodes():
    G.nodes[skill]["community"] = comm_of[skill]
    G.nodes[skill]["is_ai_skill"] = is_ai(skill)
for u, v in G.edges():
    del G[u][v]["distance"]
nx.write_gexf(G, "skill_network.gexf")
print("saved nodes.csv, edges.csv, communities.csv, summary.json, skill_network.gexf")
