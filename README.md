# Mapping AI-Skill Co-Occurrence in Job Postings

BUS 445 Advanced Business Analytics, Fall 2026, Farmingdale State College
Group: Aidan McKinley, Reina Orellana, Jose Sanchez, Syed Abdul Gillani

Our group decided to build a network that would connect AI skills from real Job Listings. It shows how one AI skill 
can appear in multiple listings and potential jobs. We measured the centrality of each skill to see which ones can help
get you a job.

Live Dashboard
https://amckinley3456-debug.github.io/Bus445-Project/

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
