import os
import re
import pandas as pd
from datetime import datetime

CERTIFICATIONS = ["cissp", "cisa", "crisc", "ceh", "iso 27001", "security+", "cysa+", "comptia", "pci-dss", "lead auditor", "lead implementer"]
TOOLS = ["servicenow", "archer", "onetrust", "splunk", "qualys", "tenable", "jira", "confluence"]
FRAMEWORKS = ["nist", "soc 2", "gdpr", "hipaa", "pci-dss", "mas trm", "hkma", "pdpo", "nist csf", "iso/iec 27001"]

def extract_years(text):
    matches = re.findall(r'(\d+)\+?\s*years?', text.lower())
    nums = [int(m) for m in matches if int(m) <= 20]
    return max(nums) if nums else 0

def count_keywords(text, keywords):
    return sum(1 for k in keywords if k in text.lower())

def extract_title(text):
    match = re.search(r'Title:\s*(.*)', text)
    return match.group(1).strip() if match else "Unknown"

def extract_company(text):
    match = re.search(r'Company:\s*(.*)', text)
    return match.group(1).strip() if match else "Unknown"

def extract_location(text):
    match = re.search(r'Location:\s*(.*)', text)
    return match.group(1).strip() if match else "Unknown"

def process_month():
    month = datetime.now().strftime("%Y-%m")
    raw_path = f"data/raw/{month}"

    if not os.path.exists(raw_path):
        print(f"No raw data folder found for {month}. Skipping.")
        return

    txt_files = [f for f in os.listdir(raw_path) if f.endswith(".txt")]
    if not txt_files:
        print(f"No .txt files found in {raw_path}. Skipping.")
        return

    records = []
    for file in sorted(txt_files):
        filepath = os.path.join(raw_path, file)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        years   = extract_years(text)
        certs   = count_keywords(text, CERTIFICATIONS)
        tools   = count_keywords(text, TOOLS)
        frameworks = count_keywords(text, FRAMEWORKS)

        salary_match = re.search(r'Salary:\s*(.*)', text)
        salary = salary_match.group(1).strip() if salary_match else "Not Listed"

        records.append({
            "file": file,
            "title": extract_title(text),
            "company": extract_company(text),
            "location": extract_location(text),
            "years_required": years,
            "cert_count": certs,
            "tool_count": tools,
            "framework_count": frameworks,
            "salary": salary
        })

    os.makedirs("data/processed", exist_ok=True)
    df = pd.DataFrame(records)
    df.to_csv(f"data/processed/{month}.csv", index=False)
    print(f"Extracted metrics for {len(records)} jobs → data/processed/{month}.csv")

if __name__ == "__main__":
    process_month()
