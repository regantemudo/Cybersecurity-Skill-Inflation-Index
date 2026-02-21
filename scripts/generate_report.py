import pandas as pd
import matplotlib.pyplot as plt
import os

def generate():
    file_path = "data/processed/monthly_index.csv"

    if not os.path.exists(file_path):
        print("No index data available.")
        return

    df = pd.read_csv(file_path)

    os.makedirs("reports", exist_ok=True)

    plt.figure()
    plt.plot(df["month"], df["skill_score"])
    plt.xticks(rotation=45)
    plt.title("Cybersecurity Skill Inflation Trend")
    plt.tight_layout()
    plt.savefig("reports/skill_trend.png")
    plt.close()

    latest = df.iloc[-1]

    report = f"""
# Cybersecurity Skill Inflation Index Report

## Latest Month: {latest['month']}

- Average Years Required: {latest['avg_years']:.2f}
- Average Certifications Required: {latest['avg_certs']:.2f}
- Average Tools Required: {latest['avg_tools']:.2f}
- Skill Inflation Score: {latest['skill_score']:.2f}

See skill_trend.png for visualization.
"""

    with open("reports/Monthly-CSII-Report.md", "w") as f:
        f.write(report)

    print("Report generated.")

if __name__ == "__main__":
    generate()
