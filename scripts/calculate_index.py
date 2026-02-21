import pandas as pd
from datetime import datetime
import os

def calculate():
    month = datetime.now().strftime("%Y-%m")
    file_path = f"data/processed/{month}.csv"

    if not os.path.exists(file_path):
        print(f"Processed data not found for {month}. Run extract_metrics.py first.")
        return

    df = pd.read_csv(file_path)

    avg_years      = round(df["years_required"].mean(), 2)
    avg_certs      = round(df["cert_count"].mean(), 2)
    avg_tools      = round(df["tool_count"].mean(), 2)
    avg_frameworks = round(df["framework_count"].mean(), 2)
    job_count      = len(df)

    skill_score = round((avg_years * 0.4) + (avg_certs * 0.3) + (avg_tools * 0.3), 4)

    new_record = pd.DataFrame([{
        "month": month,
        "avg_years": avg_years,
        "avg_certs": avg_certs,
        "avg_tools": avg_tools,
        "avg_frameworks": avg_frameworks,
        "skill_score": skill_score,
        "job_count": job_count
    }])

    output_file = "data/processed/monthly_index.csv"

    if os.path.exists(output_file):
        existing = pd.read_csv(output_file)
        # Remove any existing rows for this month to avoid duplicates
        existing = existing[existing["month"] != month]
        combined = pd.concat([existing, new_record], ignore_index=True)
        combined.to_csv(output_file, index=False)
    else:
        new_record.to_csv(output_file, index=False)

    print(f"Index calculated for {month}: score={skill_score} | years={avg_years} | certs={avg_certs} | tools={avg_tools} | jobs={job_count}")

if __name__ == "__main__":
    calculate()
