import pandas as pd
from datetime import datetime
import os

def calculate():
    month     = datetime.now().strftime("%Y-%m")
    file_path = f"data/processed/{month}.csv"
    if not os.path.exists(file_path):
        print(f"No data for {month}. Run extract_metrics.py first."); return

    df = pd.read_csv(file_path)

    def score(grp):
        return round((grp["years_required"].mean()*0.4) +
                     (grp["cert_count"].mean()*0.3) +
                     (grp["tool_count"].mean()*0.3), 4)

    # ── Global Index ──────────────────────────────────────────────────────────
    g_sal   = df["salary_usd"].dropna()
    g_sen   = df["seniority"].value_counts().to_dict() if "seniority" in df.columns else {}
    g_expl  = round(len(df[df["anomaly_flags"]!="CLEAN"])/len(df)*100, 1) if "anomaly_flags" in df.columns else 0

    global_rec = pd.DataFrame([{
        "month":             month,
        "avg_years":         round(df["years_required"].mean(), 2),
        "avg_certs":         round(df["cert_count"].mean(), 2),
        "avg_tools":         round(df["tool_count"].mean(), 2),
        "avg_frameworks":    round(df["framework_count"].mean(), 2),
        "skill_score":       score(df),
        "job_count":         len(df),
        "avg_salary_usd":    round(g_sal.mean(), 0) if not g_sal.empty else None,
        "salary_listed_pct": round(len(g_sal)/len(df)*100, 1),
        "exploitation_rate": g_expl,
        "junior_count":      g_sen.get("Junior", 0),
        "mid_count":         g_sen.get("Mid", 0),
        "senior_count":      g_sen.get("Senior", 0),
    }])
    _upsert(global_rec, "data/processed/monthly_index.csv", month)
    print(f"✓ Global  score={global_rec['skill_score'].iloc[0]} | jobs={len(df)} | exploit={g_expl}%")

    # ── Domain Index ──────────────────────────────────────────────────────────
    domain_records = []
    if "domain" in df.columns:
        for domain, grp in df.groupby("domain"):
            d_sal = grp["salary_usd"].dropna()
            d_expl = round(len(grp[grp["anomaly_flags"]!="CLEAN"])/len(grp)*100, 1)
            domain_records.append({
                "month":             month,
                "domain":            domain,
                "job_count":         len(grp),
                "avg_years":         round(grp["years_required"].mean(), 2),
                "avg_certs":         round(grp["cert_count"].mean(), 2),
                "avg_tools":         round(grp["tool_count"].mean(), 2),
                "skill_score":       score(grp),
                "avg_salary_usd":    round(d_sal.mean(), 0) if not d_sal.empty else None,
                "exploitation_rate": d_expl,
            })
        d_df = pd.DataFrame(domain_records)
        _upsert(d_df, "data/processed/domain_index.csv", month)
        print("  Domain scores:")
        for r in domain_records:
            print(f"    {r['domain']:<25} score={r['skill_score']:.2f}  jobs={r['job_count']}")

    # ── Country Index ─────────────────────────────────────────────────────────
    if "country" in df.columns:
        c_records = []
        for country, grp in df.groupby("country"):
            c_sal = grp["salary_usd"].dropna()
            c_records.append({
                "month":      month, "country": country,
                "job_count":  len(grp),
                "avg_years":  round(grp["years_required"].mean(), 2),
                "avg_certs":  round(grp["cert_count"].mean(), 2),
                "avg_tools":  round(grp["tool_count"].mean(), 2),
                "skill_score":score(grp),
                "avg_sal_usd":round(c_sal.mean(), 0) if not c_sal.empty else None,
            })
        _upsert(pd.DataFrame(c_records), "data/processed/country_index.csv", month)
        print(f"  ✓ Country index: {len(c_records)} markets")

def _upsert(new_df, path, month):
    if os.path.exists(path):
        existing = pd.read_csv(path)
        existing = existing[existing["month"] != month]
        combined = pd.concat([existing, new_df], ignore_index=True)
        combined.to_csv(path, index=False)
    else:
        new_df.to_csv(path, index=False)

if __name__ == "__main__":
    calculate()
