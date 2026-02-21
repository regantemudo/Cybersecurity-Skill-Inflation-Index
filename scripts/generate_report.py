import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load processed data
df = pd.read_csv("data/processed/extracted_data.csv")
history = pd.read_csv("data/processed/index_history.csv")

# ---------------------------
# 1. Skill Inflation Trend
# ---------------------------
plt.figure()
plt.fill_between(history["date"], history["skill_score"])
plt.xticks(rotation=45)
plt.title("Cybersecurity Skill Inflation Trend")
plt.xlabel("Date")
plt.ylabel("Skill Inflation Score")
plt.tight_layout()
plt.savefig("reports/skill_trend.png")
plt.close()

# ---------------------------
# 2. Certification Demand
# ---------------------------
cert_counts = df["certification"].value_counts().head(10)

plt.figure()
cert_counts.plot(kind="bar")
plt.title("Top Certifications in Demand")
plt.xlabel("Certification")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("reports/cert_demand.png")
plt.close()

# ---------------------------
# 3. Tool Demand
# ---------------------------
tool_counts = df["tool"].value_counts().head(10)

plt.figure()
tool_counts.plot(kind="barh")
plt.title("Top Tools in Demand")
plt.xlabel("Frequency")
plt.tight_layout()
plt.savefig("reports/tool_demand.png")
plt.close()

# ---------------------------
# 4. Experience Distribution
# ---------------------------
plt.figure()
plt.hist(df["years_required"], bins=10)
plt.title("Experience Requirement Distribution")
plt.xlabel("Years Required")
plt.ylabel("Number of Jobs")
plt.tight_layout()
plt.savefig("reports/experience_distribution.png")
plt.close()

# ---------------------------
# 5. Salary vs Experience
# ---------------------------
if "salary_mean" in df.columns:
    plt.figure()
    plt.scatter(df["years_required"], df["salary_mean"])
    plt.title("Salary vs Experience")
    plt.xlabel("Years Required")
    plt.ylabel("Salary")
    plt.tight_layout()
    plt.savefig("reports/salary_vs_experience.png")
    plt.close()
