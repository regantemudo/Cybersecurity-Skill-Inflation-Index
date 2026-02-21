# 📊 Cybersecurity Skill Inflation Index (CSII)

> **An automated intelligence engine tracking how cybersecurity job requirements are rising — faster than salaries.**

[![CSII Automation](https://github.com/YOUR-USERNAME/Cybersecurity-Skill-Inflation-Index/actions/workflows/csii.yml/badge.svg)](https://github.com/YOUR-USERNAME/Cybersecurity-Skill-Inflation-Index/actions/workflows/csii.yml)
![Last Updated](https://img.shields.io/badge/Last%20Updated-2026--02-blue?style=flat)
![Skill Score](https://img.shields.io/badge/Skill%20Score-3.12-red?style=flat)
![Avg Years](https://img.shields.io/badge/Avg%20Years-4.2-blue?style=flat)
![Avg Certs](https://img.shields.io/badge/Avg%20Certs-3.4-green?style=flat)
![Avg Tools](https://img.shields.io/badge/Avg%20Tools-1.4-yellow?style=flat)
![Jobs Analyzed](https://img.shields.io/badge/Jobs%20Analyzed-12-brightgreen?style=flat)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat)

---

## ⚠️ Latest Signal — February 2026

> 🔴 **HIGH INFLATION DETECTED** — Skill requirements are rising faster than compensation. Average experience demand has reached **4.2 years** across all roles, with **3.4 certifications** expected per job posting.

| Metric | Value | Signal |
|--------|-------|--------|
| 📅 Avg Years Required | **4.17 yrs** | 🔴 High — entry roles requiring mid-level experience |
| 🧠 Avg Certifications per Job | **3.42** | 🔴 Cert creep accelerating |
| 🛠️ Avg Tools Required | **1.42** | 🟡 Growing stack complexity |
| 📐 Avg Frameworks Referenced | **3.58** | 🔴 NIST + ISO + SOC 2 now standard |
| 📈 **Skill Inflation Score** | **3.12** | 🔴 Above inflation threshold (3.0) |
| 💼 Jobs Analyzed This Month | **12** | ✅ |

---

## 📈 Skill Inflation Trend

![Skill Inflation Trend](reports/skill_trend.png)

> Auto-regenerated monthly by GitHub Actions. Each data point = one month of curated job descriptions.

---

## 🏆 Certification Demand

![Certification Demand](reports/cert_demand.png)

| Certification | Demand Bar | Signal |
|--------------|------------|--------|
| CISSP | `████████░░` | 🔴 Near-universal for mid/senior |
| CISA | `███████░░░` | 🔴 Standard requirement |
| ISO 27001 | `███████░░░` | 🔴 Expected at all levels |
| CRISC | `█████░░░░░` | 🟡 Growing fast |
| CEH | `███░░░░░░░` | 🟢 Emerging |
| Security+ | `███░░░░░░░` | 🟢 Entry-level baseline |

---

## 🛠️ Tool Stack Demand

![Tool Demand](reports/tool_demand.png)

| Tool | Jobs Mentioning | Trend |
|------|----------------|-------|
| ServiceNow | 5 / 12 | 🔴 Dominant GRC platform |
| Archer | 4 / 12 | 🔴 Common in finance sector |
| OneTrust | 3 / 12 | 🟡 Rising privacy focus |
| Splunk | 2 / 12 | 🟡 Growing SIEM requirement |

---

## 📊 Experience Distribution

![Experience Distribution](reports/experience_distribution.png)

| Bracket | Count | % of Jobs |
|---------|-------|-----------|
| 0 yrs (Entry) | 1 | 8% |
| 1–2 yrs | 2 | 17% |
| 3–5 yrs | 4 | 33% |
| 6–8 yrs | 2 | 17% |
| 9+ yrs | 3 | 25% |

> **Key Insight:** 75% of listings require 3+ years. Only 8% are truly entry-level.

---

## 🌍 Regional Intelligence

| Market | Avg Yrs | Score | Dominant Certs |
|--------|---------|-------|----------------|
| 🇸🇬 Singapore | 7.0 | 🔴 4.50 | CISSP, CISA, CRISC |
| 🇭🇰 Hong Kong | 8.0 | 🔴 4.20 | CISSP, CRISC, ISO 27001 |
| 🇦🇪 UAE | 3.5 | 🟡 2.80 | CISA, ISO 27001 |
| 🇮🇳 India | 2.8 | 🟡 2.60 | CISA, ISO 27001, CEH |
| 🇬🇧 UK | 1.0 | 🟢 1.10 | Security+, CISA |
| 🇺🇸 USA | 1.0 | 🟢 1.00 | Security+, CEH |

---

## 📅 Historical Index

| Month | Avg Years | Avg Certs | Avg Tools | Skill Score | Jobs |
|-------|-----------|-----------|-----------|-------------|------|
| 2026-02 | 4.17 | 3.42 | 1.42 | **3.12** | 12 |
## 🔍 What Is CSII?

The **Cybersecurity Skill Inflation Index** measures whether employers are raising job requirements faster than compensation — a structural market inefficiency that disadvantages job seekers and distorts career planning.

**Scoring Formula:**
```
Skill_Score = (Avg_Years × 0.4) + (Avg_Certs × 0.3) + (Avg_Tools × 0.3)
```

**Interpreting Scores:**
| Score | Signal | Meaning |
|-------|--------|---------|
| `< 2.0` | 🟢 Healthy | Requirements proportional to value |
| `2.0–3.0` | 🟡 Moderate | Inflation building — monitor closely |
| `> 3.0` | 🔴 High | **Requirements outpacing compensation** |

---

## ⚙️ How It Works

```
data/raw/YYYY-MM/*.txt         ← Monthly job descriptions (structured .txt)
         ↓
scripts/extract_metrics.py     ← Parses years, certs, tools, frameworks per job
         ↓
scripts/calculate_index.py     ← Weighted inflation score, deduplication
         ↓
scripts/generate_report.py     ← 4 charts + README badge update + monthly report
         ↓
.github/workflows/csii.yml     ← Auto-commits everything on schedule
```

---

## 📂 Repository Structure

```
Cybersecurity-Skill-Inflation-Index/
├── data/
│   ├── raw/
│   │   └── YYYY-MM/          ← Add job_XXX.txt files here monthly
│   └── processed/
│       ├── YYYY-MM.csv        ← Extracted job metrics
│       └── monthly_index.csv  ← Cumulative inflation scores
├── reports/
│   ├── skill_trend.png        ← Inflation trend chart
│   ├── cert_demand.png        ← Certification frequency chart
│   ├── tool_demand.png        ← Tool stack pie chart
│   ├── experience_distribution.png
│   └── Monthly-CSII-Report.md
├── scripts/
│   ├── extract_metrics.py
│   ├── calculate_index.py
│   ├── generate_report.py
│   └── collect.py
├── requirements.txt
└── .github/workflows/csii.yml
```

---

## 📋 Job Description Format

For consistent parsing, save each job as `data/raw/YYYY-MM/job_XXX.txt`:

```
Title: GRC Analyst
Company: Company Name
Location: City, Country
Salary: USD 80,000 annually

Job Description:
Full job description text here...
```

---

## 📦 Tech Stack

| Component | Technology |
|-----------|-----------|
| Data Storage | CSV + Git version control |
| Extraction | Python · regex · pandas |
| Visualization | matplotlib (dark theme) |
| Automation | GitHub Actions (daily cron) |
| Reports | Markdown + PNG charts |

---

## 🗺️ Roadmap

- [x] Monthly extraction + scoring engine
- [x] 4-chart automated report generation
- [x] README badge auto-update
- [ ] Country-level segmentation scoring
- [ ] Junior / Mid / Senior inflation split
- [ ] Salary normalization across currencies
- [ ] 6-month forecast model (scikit-learn)
- [ ] GitHub Pages interactive dashboard

---

## 📥 Contributing

Add job descriptions to `data/raw/YYYY-MM/` using the structured format above, then trigger the workflow manually via **Actions → Run workflow**.

---

*Data sourced manually from public job listings. Updated automatically via GitHub Actions.*
