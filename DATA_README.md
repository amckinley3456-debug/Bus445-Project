# Data access

We use **Data Science Job Postings & Skills (2024)** by asaniczka on Kaggle:
https://www.kaggle.com/datasets/asaniczka/data-science-job-postings-and-skills

It has 12,217 LinkedIn postings collected in January 2024. Skills were already pulled
out of each posting's text and stored as a comma-separated list.

We only need two of its files:

| file | what it holds |
|---|---|
| `job_skills.csv` | `job_link`, `job_skills` (comma-separated skill list) |
| `job_postings.csv` | `job_link`, title, company, location, level, type, dates |

