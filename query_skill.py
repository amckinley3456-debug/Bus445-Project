import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).parent))
from skills import clean_skill

G = nx.read_gexf(Path(__file__).resolve().parent / "skill_network.gexf")
comm = {n: int(d["community"]) for n, d in G.nodes(data=True)}


def lookup(text, k=10):
    label, _ = clean_skill(text)
    if label not in G:
        hits = [n for n in G if text.lower() in n.lower()]
        if not hits:
            print(f"'{text}' is not in the network (it may be below the 30-posting cutoff).")
            return
        label = hits[0]
    nbrs = sorted(G[label].items(), key=lambda kv: -kv[1]["weight"])[:k]
    print(f"\n{label}  (community {comm[label]}, {G.degree(label)} connections)")
    print(f"{'skill':32}{'shared postings':>16}{'lift':>8}")
    for n, d in nbrs:
        print(f"{n:32}{int(d['weight']):>16}{float(d['lift']):>8.2f}")
    same = [n for n in G if comm[n] == comm[label] and n != label]
    print(f"\nOther skills in its cluster: {', '.join(sorted(same, key=lambda n: -G.degree(n, weight='weight'))[:15])}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        lookup(" ".join(sys.argv[1:]))
    else:
        while (q := input("\nskill (blank to quit): ").strip()):
            lookup(q)
