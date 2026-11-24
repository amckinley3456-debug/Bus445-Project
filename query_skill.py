import networkx as nx
from skills import clean_skill

G = nx.read_gexf("skill_network.gexf")

while True:
    text = input("\nskill (blank to quit): ").strip()
    if text == "":
        break

    skill = clean_skill(text)

    if skill not in G:
        skill = None
        for name in G.nodes():
            if text.lower() in name.lower():
                skill = name
                break
    if skill is None:
        print(text, "is not in the network")
        continue

    links = []
    for other in G[skill]:
        links.append([other, int(G[skill][other]["weight"]), float(G[skill][other]["lift"])])
    links = sorted(links, key=lambda x: -x[1])

    cluster = G.nodes[skill]["community"]
    print("\n" + skill, "| cluster", cluster, "|", G.degree(skill), "links")
    print(f"{'skill':32}{'shared postings':>16}{'lift':>8}")
    for other, shared, lift in links[:10]:
        print(f"{other:32}{shared:>16}{lift:>8.2f}")

    same = []
    for name in G.nodes():
        if G.nodes[name]["community"] == cluster and name != skill:
            same.append(name)
    same = sorted(same, key=lambda n: -G.degree(n, weight="weight"))
    print("\nother skills in its cluster:", ", ".join(same[:15]))
