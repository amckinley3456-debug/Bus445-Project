import json
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import streamlit as st
from skills import clean_skill

CLUSTERS = {
    1: ["Analytics & BI", "rgb(47, 111, 214)"],
    2: ["ML engineering", "rgb(217, 84, 30)"],
    3: ["Data engineering & cloud", "rgb(18, 137, 106)"],
}

st.set_page_config(page_title="AI Skill Network", layout="wide")

nodes = pd.read_csv("nodes.csv").set_index("skill")
edges = pd.read_csv("edges.csv")
with open("summary.json") as f:
    summary = json.load(f)

def top_links(skill):
    links = []
    for row in edges.itertuples():
        if row.source == skill:
            links.append([row.target, row.cooccurrences])
        elif row.target == skill:
            links.append([row.source, row.cooccurrences])
    links = sorted(links, key=lambda x: -x[1])
    return links[:10]

@st.cache_data
def map_positions():
    G = nx.Graph()
    for row in edges.itertuples():
        G.add_edge(row.source, row.target, weight=row.cooccurrences)
    map_links = set()
    for skill in G.nodes():
        strongest = sorted(G[skill], key=lambda other: -G[skill][other]["weight"])[:4]
        for other in strongest:
            map_links.add(tuple(sorted([skill, other])))
    map_links = sorted(map_links)
    H = nx.Graph(map_links)
    return nx.kamada_kawai_layout(H), map_links

pos, map_links = map_positions()

st.title("AI Skill Co-Occurrence in Job Postings")
st.caption("BUS 445 Advanced Business Analytics, Farmingdale State College, Fall 2026")
cols = st.columns(5)
cols[0].metric("Postings", f"{summary['postings_after_dedup']:,}")
cols[1].metric("Postings with an AI skill", f"{summary['postings_with_ai_skill']:,}")
cols[2].metric("Skills", summary["nodes_final"])
cols[3].metric("Links", f"{summary['edges_final']:,}")
cols[4].metric("Modularity", summary["modularity_weighted_seed42"])

st.header("Skill lookup")
text = st.text_input("Skill", "python")

skill = None
if text.strip() != "":
    skill = clean_skill(text)
    if skill not in nodes.index:
        skill = None
        for name in nodes.index:
            if text.strip().lower() in name.lower():
                skill = name
                break
    if skill is None:
        st.write("Not in the network.")

if skill is not None:
    cluster = nodes.loc[skill, "community"]
    st.subheader(skill)
    st.write("Cluster:", CLUSTERS[cluster][0], "| Postings:", int(nodes.loc[skill, "postings"]))
    table = pd.DataFrame(top_links(skill), columns=["Most often listed with", "Shared postings"])
    st.dataframe(table, hide_index=True)

st.header("Top 15 skills")
metric = st.selectbox("Rank by", ["eigenvector", "betweenness", "postings"])
top = nodes.sort_values(metric, ascending=False).head(15)
top = top.iloc[::-1]
bar_colors = [CLUSTERS[c][1] for c in top["community"]]
bar = go.Figure(go.Bar(x=top[metric], y=top.index, orientation="h", marker_color=bar_colors))
bar.update_layout(height=450, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(bar, use_container_width=True)

st.header("Skill clusters (Louvain)")
cols = st.columns(3)
for c in CLUSTERS:
    members = nodes[nodes["community"] == c].sort_values("postings", ascending=False)
    name = CLUSTERS[c][0]
    color = CLUSTERS[c][1]
    cols[c - 1].markdown(f"<h3 style='color:{color}'>{name}</h3>", unsafe_allow_html=True)
    cols[c - 1].write(str(len(members)) + " skills")
    cols[c - 1].write(", ".join(members.index[:12]))

st.header("Network map")
shown = st.multiselect("Clusters", [1, 2, 3], default=[1, 2, 3], format_func=lambda c: CLUSTERS[c][0])

linked = []
if skill is not None:
    for other, shared in top_links(skill):
        linked.append(other)

visible = []
for name in nodes.index:
    if nodes.loc[name, "community"] in shown and name in pos:
        visible.append(name)

big = list(nodes.sort_values("postings", ascending=False).index[:30])

fig = go.Figure()

xs = []
ys = []
for a, b in map_links:
    if a in visible and b in visible and skill not in [a, b]:
        xs = xs + [pos[a][0], pos[b][0], None]
        ys = ys + [pos[a][1], pos[b][1], None]
fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color="rgb(221, 227, 233)", width=1),
                         hoverinfo="skip", showlegend=False))

if skill in visible:
    xs = []
    ys = []
    for other in linked:
        if other in visible:
            xs = xs + [pos[skill][0], pos[other][0], None]
            ys = ys + [pos[skill][1], pos[other][1], None]
    color = CLUSTERS[nodes.loc[skill, "community"]][1]
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=color, width=2),
                             hoverinfo="skip", showlegend=False))

for c in shown:
    group = []
    for name in visible:
        if nodes.loc[name, "community"] == c:
            group.append(name)

    x = []
    y = []
    labels = []
    hover = []
    sizes = []
    fade = []
    for name in group:
        x.append(pos[name][0])
        y.append(pos[name][1])
        hover.append(name + "<br>" + CLUSTERS[c][0] + "<br>" + str(nodes.loc[name, "postings"]) + " postings")
        sizes.append(6 + nodes.loc[name, "postings"] ** 0.5 / 1.5)

        if skill is None or name == skill or name in linked:
            fade.append(0.9)
        else:
            fade.append(0.15)

        show_label = nodes.loc[name, "is_ai_skill"] or name in big
        if skill is not None and name != skill and name not in linked:
            show_label = False
        if name == skill:
            show_label = True
        if show_label and nodes.loc[name, "is_ai_skill"]:
            labels.append(name.upper())
        elif show_label:
            labels.append(name)
        else:
            labels.append("")

    fig.add_trace(go.Scatter(x=x, y=y, mode="markers+text", name=CLUSTERS[c][0],
                             text=labels, textposition="top center", textfont=dict(size=10),
                             hovertext=hover, hoverinfo="text",
                             marker=dict(color=CLUSTERS[c][1], size=sizes, opacity=fade)))

fig.update_layout(height=650, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white",
                  xaxis=dict(visible=False), yaxis=dict(visible=False), legend=dict(orientation="h"))
st.plotly_chart(fig, use_container_width=True)

st.caption("Group: Aidan McKinley, Reina Orellana, Jose Sanchez, Syed Abdul Gillani. "
           "Data: Data Science Job Postings & Skills (2024), LinkedIn, Kaggle.")
