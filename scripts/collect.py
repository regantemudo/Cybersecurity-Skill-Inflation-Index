import os
from datetime import datetime

def create_job_file(title, company, location, salary, description):
    month = datetime.now().strftime("%Y-%m")
    folder = f"data/raw/{month}"
    os.makedirs(folder, exist_ok=True)

    existing = len(os.listdir(folder)) + 1
    filename = f"{folder}/job_{existing:03d}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Title: {title}\n")
        f.write(f"Company: {company}\n")
        f.write(f"Location: {location}\n")
        f.write(f"Salary: {salary}\n")
        f.write("Job Description:\n")
        f.write(description)

    print(f"Saved {filename}")

if __name__ == "__main__":
    print("Use this script manually to create structured job entries.")
