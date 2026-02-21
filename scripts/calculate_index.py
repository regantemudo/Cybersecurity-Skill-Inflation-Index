import pandas as pd
from datetime import datetime
import os

def calculate():
    month     = datetime.now().strftime("%Y-%m")
    file_path = f"data/processed/{month}.csv"

    if not os.path.exists(file_path):
        print(f"Processed data not found for {month}. Run extract_metrics.py first.")
        return

    df = pd.read_csv(file_path)

    # ── Global Metrics ────────────────────────────────────────────────────────
    avg_years      = round(df["years_required"].mean(), 2)
    avg_certs      = round(df["cert_count"].mean(), 2)
    avg_tools      = round(df["tool_count"].mean(), 2)
    avg_frameworks = round(df["framework_count"].mean(), 2)
    job_count      = len(df)
    skill_score    = round((avg_years * 0.4) + (avg_certs * 0.3) + (avg_tools * 0.3), 4)

    # ── Salary Stats (USD) ────────────────────────────────────────────────────
    salary_df   = df[df["salary_usd"].notna()]
    avg_sal_usd = round(salary_df["salary_usd"].mean(), 0) if not salary_df.empty else None
    listed_pct  = round(len(salary_df) / job_count * 100, 1)

    # ── Anomaly Stats ─────────────────────────────────────────────────────────
    flagged_count = len(df[df["anomaly_flags"] != "CLEAN"]) if "anomaly_flags" in df.columns else 0
    exploitation_rate = round(flagged_count / job_count * 100, 1)

    # ── Seniority Breakdown ───────────────────────────────────────────────────
    seniority_counts = df["seniority"].value_counts().to_dict() if "seniority" in df.columns else {}

    # ── Country Segmentation Scores ───────────────────────────────────────────
    country_records = []
    if "country" in df.columns:
        for country, grp in df.groupby("country"):
            c_score = round((grp["years_required"].mean() * 0.4) +
                            (grp["cert_count"].mean()     * 0.3) +
                            (grp["tool_count"].mean()     * 0.3), 2)
            c_sal   = round(grp["salary_usd"].dropna().mean(), 0) if not grp["salary_usd"].dropna().empty else None
            country_records.append({
                "month":        month,
                "country":      country,
                "job_count":    len(grp),
                "avg_years":    round(grp["years_required"].mean(), 2),
                "avg_certs":    round(grp["cert_count"].mean(), 2),
                "avg_tools":    round(grp["tool_count"].mean(), 2),
                "skill_score":  c_score,
                "avg_sal_usd":  c_sal,
            })

    # ── Write Global Index ────────────────────────────────────────────────────
    new_record = pd.DataFrame([{
        "month":              month,
        "avg_years":          avg_years,
        "avg_certs":          avg_certs,
        "avg_tools":          avg_tools,
        "avg_frameworks":     avg_frameworks,
        "skill_score":        skill_score,
        "job_count":          job_count,
        "avg_salary_usd":     avg_sal_usd,
        "salary_listed_pct":  listed_pct,
        "exploitation_rate":  exploitation_rate,
        "junior_count":       seniority_counts.get("Junior", 0),
        "mid_count":          seniority_counts.get("Mid", 0),
        "senior_count":       seniority_counts.get("Senior", 0),
    }])

    idx_file = "data/processed/monthly_index.csv"
    if os.path.exists(idx_file):
        existing = pd.read_csv(idx_file)
        existing = existing[existing["month"] != month]
        combined = pd.concat([existing, new_record], ignore_index=True)
        combined.to_csv(idx_file, index=False)
    else:
        new_record.to_csv(idx_file, index=False)

    # ── Write Country Index ───────────────────────────────────────────────────
    if country_records:
        c_df     = pd.DataFrame(country_records)
        c_file   = "data/processed/country_index.csv"
        if os.path.exists(c_file):
            c_existing = pd.read_csv(c_file)
            c_existing = c_existing[c_existing["month"] != month]
            c_combined = pd.concat([c_existing, c_df], ignore_index=True)
            c_combined.to_csv(c_file, index=False)
        else:
            c_df.to_csv(c_file, index=False)
        print(f"✓ Country index updated → {len(country_records)} markets")

    print(f"✓ Global index: score={skill_score} | years={avg_years} | certs={avg_certs} | tools={avg_tools}")
    print(f"  Salary (USD avg): ${avg_sal_usd:,.0f} ({listed_pct}% listed) | Exploitation rate: {exploitation_rate}%")
    print(f"  Seniority: Junior={seniority_counts.get('Junior',0)} Mid={seniority_counts.get('Mid',0)} Senior={seniority_counts.get('Senior',0)}")

if __name__ == "__main__":
    calculate()
