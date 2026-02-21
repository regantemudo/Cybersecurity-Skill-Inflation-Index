import pandas as pd
from datetime import datetime
import os

def calculate():
    month = datetime.now().strftime("%Y-%m")
    file_path = f"data/processed/{month}.csv"

    if not os.path.exists(file_path):
        print("Processed data not found.")
        return

    df = pd.read_csv(file_path)

    avg_years = df["years_required"].mean()
    avg_certs = df["cert_count"].mean()
    avg_tools = df["tool_count"].mean()

    skill_score = (avg_years * 0.4) + (avg_certs * 0.3) + (avg_tools * 0.3)

    index_record = pd.DataFrame([{
        "month": month,
        "avg_years": avg_years,
        "avg_certs": avg_certs,
        "avg_tools": avg_tools,
        "skill_score": skill_score
    }])

    output_file = "data/processed/monthly_index.csv"

    if os.path.exists(output_file):
        existing = pd.read_csv(output_file)
        combined = pd.concat([existing, index_record])
        combined.to_csv(output_file, index=False)
    else:
        index_record.to_csv(output_file, index=False)

    print("Index calculated.")

if __name__ == "__main__":
    calculate()
