import shutil
from pathlib import Path

import kagglehub

DEST = Path(__file__).resolve().parent
path = Path(kagglehub.dataset_download("asaniczka/data-science-job-postings-and-skills"))
for name in ("job_postings.csv", "job_skills.csv"):
    shutil.copy(path / name, DEST / name)
    print("saved", DEST / name)
