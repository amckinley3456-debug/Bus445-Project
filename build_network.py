import json
import sys
from collections import Counter
from pathlib import Path

import networkx as nx
import pandas as pd
from networkx.algorithms import bipartite

sys.path.insert(0, str(Path(__file__).parent))
from skills import parse_posting, is_ai

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "job_skills.csv"
META = ROOT / "job_postings.csv"
OUT = ROOT

MIN_SUPPORT = 30
MIN_EDGE = 10
SEED = 42


def main():
    df = pd.read_csv(RAW).merge(pd.read_csv(META, usecols=["job_link", "company", "job_title"]), on="job_link")
    n_raw = len(df)
    key = df["company"].str.lower().str.strip() + "|" + df["job_title"].str.lower().str.strip()
    df = df[~key.duplicated()].reset_index(drop=True)
    df["skills"] = df["job_skills"].apply(parse_posting)
    n_total = len(df)
    df["has_ai"] = df["skills"].apply(lambda s: any(is_ai(x) for x in s))
    ai = df[df["has_ai"]].reset_index(drop=True)
    n_ai = len(ai)

    support = Counter(s for skills in ai["skills"] for s in skills)
    keep = sorted(s for s, c in support.items() if c >= MIN_SUPPORT)
    keep_set = set(keep)

    B = nx.Graph()
    B.add_nodes_from((f"p{i}" for i in range(n_ai)), bipartite=0)
    B.add_nodes_from(keep, bipartite=1)
    for i, skills in enumerate(ai["skills"]):
        for s in sorted(skills & keep_set):
            B.add_edge(f"p{i}", s)
    B.remove_nodes_from([n for n, d in B.degree() if d == 0])

    full = bipartite.weighted_projected_graph(B, [n for n in keep if n in B])
    full_density = nx.density(full)

    G = nx.Graph()
    for u, v, d in sorted(full.edges(data=True)):
        w = d["weight"]
        lift = n_ai * w / (support[u] * support[v])
        if w >= MIN_EDGE and lift > 1:
            G.add_edge(u, v, weight=w, lift=round(lift, 3), distance=1 / w)
    G.remove_nodes_from(list(nx.isolates(G)))

    deg_c = nx.degree_centrality(G)
    strength = dict(G.degree(weight="weight"))
    btw = nx.betweenness_centrality(G, weight="distance", normalized=True)
    eig = nx.eigenvector_centrality_numpy(G, weight="weight")

    comms = nx.community.louvain_communities(G, weight="weight", seed=SEED)
    Q = nx.community.modularity(G, comms, weight="weight")
    q_runs = [nx.community.modularity(G, nx.community.louvain_communities(G, weight="weight", seed=s), weight="weight")
              for s in range(10)]

    Gu = nx.Graph(G.edges())
    q_real_u = nx.community.modularity(Gu, nx.community.louvain_communities(Gu, seed=SEED))
    q_null = []
    for s in range(5):
        R = Gu.copy()
        nx.double_edge_swap(R, nswap=10 * R.number_of_edges(), max_tries=10**6, seed=s)
        q_null.append(nx.community.modularity(R, nx.community.louvain_communities(R, seed=SEED)))

    comm_of = {}
    comms = sorted(comms, key=lambda c: -sum(strength[n] for n in c))
    for k, c in enumerate(comms, start=1):
        for n in c:
            comm_of[n] = k

    nodes = pd.DataFrame({
        "skill": list(G.nodes()),
        "is_ai_skill": [is_ai(n) for n in G.nodes()],
        "postings": [support[n] for n in G.nodes()],
        "pct_of_ai_postings": [round(100 * support[n] / n_ai, 1) for n in G.nodes()],
        "degree": [G.degree(n) for n in G.nodes()],
        "degree_centrality": [round(deg_c[n], 4) for n in G.nodes()],
        "weighted_degree": [strength[n] for n in G.nodes()],
        "betweenness": [round(btw[n], 4) for n in G.nodes()],
        "eigenvector": [round(eig[n], 4) for n in G.nodes()],
        "community": [comm_of[n] for n in G.nodes()],
    }).sort_values("eigenvector", ascending=False)
    nodes.to_csv(OUT / "nodes.csv", index=False)

    edges = pd.DataFrame([(u, v, d["weight"], d["lift"]) for u, v, d in G.edges(data=True)],
                         columns=["source", "target", "cooccurrences", "lift"]).sort_values("cooccurrences", ascending=False)
    edges.to_csv(OUT / "edges.csv", index=False)

    comm_rows = []
    for k, c in enumerate(comms, start=1):
        members = sorted(c, key=lambda n: -strength[n])
        comm_rows.append({"community": k, "size": len(c),
                          "ai_skills": ", ".join(m for m in members if is_ai(m)),
                          "top_members": ", ".join(members[:12])})
    pd.DataFrame(comm_rows).to_csv(OUT / "communities.csv", index=False)

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
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    for n in G:
        G.nodes[n]["community"] = comm_of[n]
        G.nodes[n]["is_ai_skill"] = is_ai(n)
    for u, v in G.edges():
        del G[u][v]["distance"]
    nx.write_gexf(G, OUT / "skill_network.gexf")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
