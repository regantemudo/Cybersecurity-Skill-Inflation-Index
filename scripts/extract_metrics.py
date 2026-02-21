import os
import re
import pandas as pd
from datetime import datetime

CERTIFICATIONS = ["cissp", "cisa", "crisc", "ceh", "iso 27001"]
TOOLS = ["servicenow", "archer", "onetrust", "splunk"]
FRAMEWORKS = ["nist", "soc 2", "gdpr", "hipaa"]

def extract_years(text):
    matches = re.findall(r'(\d+)\+?\s*years', text.lower())
    return max([int(m) for m in matches]) if matches else 0

def count_keywords(text, keywords):
    return sum(1 for k in keywords if k in text.lower())

def process_month():
    month = datetime.now().strftime("%Y-%m")
    raw_path = f"data/raw/{month}"

    if not os.path.exists(raw_path):
        print("No raw data for this month.")
        return

    records = []

    for file in os.listdir(raw_path):
        with open(os.path.join(raw_path, file), "r", encoding="utf-8") as f:
            text = f.read()

        years = extract_years(text)
        certs = count_keywords(text, CERTIFICATIONS)
        tools = count_keywords(text, TOOLS)
        frameworks = count_keywords(text, FRAMEWORKS)

        salary_match = re.search(r'Salary:\s*(.*)', text)
        salary = salary_match.group(1).strip() if salary_match else "Not Listed"

        records.append({
            "years_required": years,
            "cert_count": certs,
            "tool_count": tools,
            "framework_count": frameworks,
            "salary": salary
        })

   os.makedirs("data/processed", exist_ok=True)

if not job_data:
    df = pd.DataFrame(columns=[
        "date",
        "years_required",
        "certification",
        "tool",
        "salary_mean"
    ])
else:
    df = pd.DataFrame(job_data)

df.to_csv("data/processed/extracted_data.csv", index=False)

if __name__ == "__main__":
    process_month()
