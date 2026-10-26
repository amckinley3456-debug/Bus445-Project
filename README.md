# Mapping AI-Skill Co-Occurrence in Job Postings

BUS 445 Advanced Business Analytics, Fall 2026, Farmingdale State College
Group: Aidan McKinley, Reina Orellana, Jose Sanchez, Syed Abdul Gillani

We build a network of skills from real job postings. Two skills are linked when the
same posting asks for both. Centrality tells us which AI skills employers lean on most,
and community detection shows which skills travel together as career tracks.

## Files

```
README.md                   this file
DATA_README.md              how to get the dataset
requirements.txt            Python packages
skills.py                   cleaning rules: AI-skill dictionary, aliases, stoplist
build_network.py            bipartite graph -> skill network -> centrality + Louvain
query_skill.py              live demo: type a skill, see its strongest ties and cluster
plot_network.py             network figure
download_data.py            pulls the dataset from Kaggle
01_baseline_network.ipynb   notebook that runs the baseline and shows the tables
```

## Run it

All files sit in one folder. Put the two Kaggle CSVs in the same folder, then:

```
pip install -r requirements.txt
python download_data.py
python build_network.py
python plot_network.py
python query_skill.py pytorch
```

`build_network.py` writes nodes.csv, edges.csv, communities.csv, summary.json and
skill_network.gexf into the same folder.

## Baseline settings

| setting | value |
|---|---|
| dedup | one posting per company + job title |
| AI posting | lists at least one skill from the AI dictionary in `skills.py` |
| node filter | skill appears in 30 or more AI postings |
| edge filter | 10 or more shared postings and lift > 1 |
| community detection | Louvain, weighted, seed 42 |
