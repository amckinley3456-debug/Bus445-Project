import shutil
import kagglehub

path = kagglehub.dataset_download("asaniczka/data-science-job-postings-and-skills")

shutil.copy(path + "/job_postings.csv", "job_postings.csv")
shutil.copy(path + "/job_skills.csv", "job_skills.csv")
print("saved job_postings.csv and job_skills.csv")
