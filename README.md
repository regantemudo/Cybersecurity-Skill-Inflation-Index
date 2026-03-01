# 📊 Cybersecurity Skill Inflation Index (CSII)

> **Industry-wide intelligence engine tracking skill inflation across all cybersecurity domains — powered by real job listings, updated automatically.**

[![CSII Automation](https://github.com/regantemudo/Cybersecurity-Skill-Inflation-Index/actions/workflows/csii.yml/badge.svg)](https://github.com/regantemudo/Cybersecurity-Skill-Inflation-Index/actions/workflows/csii.yml)
![Last Updated](https://img.shields.io/badge/Last%20Updated-2026--03-blue?style=flat)
![Skill Score](https://img.shields.io/badge/Skill%20Score-3.33-red?style=flat)
![Avg Years](https://img.shields.io/badge/Avg%20Years-4.2-blue?style=flat)
![Avg Certs](https://img.shields.io/badge/Avg%20Certs-2.7-green?style=flat)
![Avg Tools](https://img.shields.io/badge/Avg%20Tools-2.8-yellow?style=flat)
![Jobs Analyzed](https://img.shields.io/badge/Jobs%20Analyzed-51-brightgreen?style=flat)
![Exploitation Rate](https://img.shields.io/badge/Exploitation%20Rate-50%25-orange?style=flat)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat)

> Scores measure industry-wide requirement trends from public job data. No editorial judgement is made about any individual employer.

---

## ⚠️ Industry Signal — February 2026

> 🔴 **HIGH INFLATION** — Global score **3.14**, above the 3.0 threshold. IAM and SOC are the highest-scoring domains. **49% of all listings** flagged for requirement signals.

| Metric | Value | Signal |
|--------|-------|--------|
| 📈 Global Skill Inflation Score | **3.14** | 🔴 High — above threshold |
| 📅 Avg Years Required | **4.2 yrs** | 🔴 Rising across all domains |
| 🧠 Avg Certifications Demanded | **2.6** | 🟡 Cert creep industry-wide |
| 🛠️ Avg Tools Required | **2.4** | 🔴 High tool complexity |
| ⚠️ Requirement Signal Rate | **49%** | 🟡 Nearly half of listings flagged |
| 💰 Avg Salary (USD) | **~$71,134** | 🟡 Varies significantly by market |
| 💼 Total Jobs Analyzed | **41** | ✅ 6 domains · 6 countries |

---

## 📈 Global Inflation Trend

![Skill Trend](reports/skill_trend.png)

---

## 🏛️ Domain Intelligence

### Inflation Score by Domain

![Domain Comparison](reports/domain_comparison.png)

| Domain | Avg Years | Avg Certs | Score | Signal | Jobs |
|--------|-----------|-----------|-------|--------|------|
| IAM | 4.7 | 2.2 | 🔴 **3.57** | Identity platform complexity rising | 6 |
| SOC | 4.1 | 2.8 | 🔴 **3.26** | SIEM + EDR + SOAR now baseline | 8 |
| AppSec | 4.0 | 2.5 | 🔴 **3.17** | Secure SDLC ownership expanding | 4 |
| Penetration Testing | 4.3 | 2.1 | 🔴 **3.09** | OSCP alone no longer sufficient | 7 |
| Cloud Security | 3.2 | 3.2 | 🔴 **3.02** | Multi-cloud cert stacking | 4 |
| GRC | 4.2 | 2.8 | 🟡 **2.92** | High experience, lower tool demand | 12 |

---

### Job Distribution by Domain

![Domain Donut](reports/domain_donut.png)

---

### Exploitation Signal Rate by Domain

![Exploitation by Domain](reports/exploitation_by_domain.png)

---

### Seniority Distribution by Domain

![Seniority by Domain](reports/seniority_by_domain.png)

---

### Salary vs Inflation Score

![Salary vs Score](reports/salary_vs_score.png)

> Domains in the top-left (high salary, low score) represent better market value. Bottom-right (low salary, high score) indicates high requirement pressure relative to compensation.

---

## 🌍 Country Intelligence

![Country Comparison](reports/country_comparison.png)

---

## 🏆 Certification Demand — Industry-Wide

![Cert Demand](reports/cert_demand.png)

---

## 🛠️ Tool Demand — Industry-Wide

![Tool Demand](reports/tool_demand.png)

---

## ⚠️ Requirement Signal Flags

![Anomaly Flags](reports/anomaly_flags.png)

| Flag | Triggered When |
|------|---------------|
| `EXPERIENCE_INFLATION` | Junior title + 5+ years demanded |
| `CERT_OVERLOAD` | 5+ certifications in one posting |
| `TOOL_STACK_ABUSE` | 4+ tools demanded simultaneously |
| `UNDERPAID_EXPERIENCED` | 3+ yrs required + salary < $30K USD |
| `SENIOR_EXPLOITATION` | 8+ yrs + 3+ certs + 2+ tools |

---

## 💰 Salary vs Experience

![Salary vs Experience](reports/salary_vs_experience.png)

---

## 📅 Historical Index

| Month | Avg Years | Avg Certs | Avg Tools | Skill Score | Jobs |
|-------|-----------|-----------|-----------|-------------|------|
| 2026-02 | 4.15 | 2.59 | 2.37 | **3.14** | 41 |
| 2026-03 | 4.20 | 2.70 | 2.80 | **3.33** | 10 |
## 🔍 What Is CSII?

The **Cybersecurity Skill Inflation Index** measures whether employers across cybersecurity domains are raising job requirements faster than compensation — a structural market trend that affects career planning, hiring, and salary benchmarking.

**Domains Tracked:**

| Domain | Focus |
|--------|-------|
| 🔵 GRC | Governance, Risk, Compliance, Audit |
| 🔴 SOC | Threat Detection, Incident Response, SIEM |
| 🟠 Penetration Testing | Offensive Security, Red Team, Vulnerability Assessment |
| 🩵 Cloud Security | AWS/Azure/GCP Security, DevSecOps, CSPM |
| 🟣 AppSec | Secure SDLC, SAST/DAST, Code Review |
| 🟢 IAM | Identity Governance, PAM, SSO, Zero Trust |

**Scoring Formula:**
```
Skill_Score = (Avg_Years × 0.4) + (Avg_Certs × 0.3) + (Avg_Tools × 0.3)
```

| Score | Signal |
|-------|--------|
| `< 2.0` | 🟢 Healthy market |
| `2.0 – 3.0` | 🟡 Moderate inflation |
| `> 3.0` | 🔴 High inflation — requirements rising faster than value |

---

## ⚙️ Pipeline

```
data/raw/YYYY-MM/*.txt
        ↓ extract_metrics.py
          → Domain auto-classifier (6 domains)
          → Seniority classifier (Junior / Mid / Senior)
          → Salary normalizer (→ USD)
          → Country extractor (20+ markets)
          → Requirement signal detector (5 flags)
        ↓ calculate_index.py
          → Global index
          → Domain index (per-domain scores)
          → Country index (per-market scores)
        ↓ generate_report.py
          → 12 charts (dark theme, auto-generated)
          → README badges auto-updated
          → Monthly report committed
        ↓ GitHub Actions (daily 6am UTC)
```

---

## 📂 Structure

```
Cybersecurity-Skill-Inflation-Index/
├── data/
│   ├── raw/YYYY-MM/              ← Job listings (auto-collected + manual)
│   └── processed/
│       ├── YYYY-MM.csv           ← Per-job metrics
│       ├── monthly_index.csv     ← Global scores over time
│       ├── domain_index.csv      ← Per-domain scores over time
│       └── country_index.csv     ← Per-country scores over time
├── reports/                      ← 12 auto-generated charts + monthly report
├── scripts/
│   ├── collect.py                ← Multi-source job collector (Adzuna, JSearch, Remotive, Arbeitnow)
│   ├── extract_metrics.py        ← Domain-aware extraction engine
│   ├── calculate_index.py        ← Global + domain + country scoring
│   └── generate_report.py        ← 12-chart report generator
├── requirements.txt
└── .github/workflows/csii.yml    ← Daily automation
```

---

## 📋 Job File Format

```
Title: SOC Analyst Level 2
Company: Company Name
Location: City, Country
Salary: USD 90,000 annually
Domain: SOC
Source: Adzuna
Collected: 2026-02-24

Job Description:
Full text here.
```

**Supported domains:** `GRC` · `SOC` · `Penetration Testing` · `Cloud Security` · `AppSec` · `IAM`

---

## 🗺️ Roadmap

- [x] 6-domain tracking engine
- [x] Domain auto-classifier
- [x] Seniority classifier (Junior / Mid / Senior)
- [x] Salary normalizer (→ USD, multi-currency)
- [x] Country segmentation (20+ markets)
- [x] Requirement signal detector (5 flags)
- [x] 12 automated dark-theme charts
- [x] README badge auto-update
- [x] Daily automated collection (Adzuna + JSearch + Remotive + Arbeitnow)
- [ ] 6-month trend forecast model
- [ ] GitHub Pages live dashboard
- [ ] Domain-specific cert ROI scoring

---

*Built by [Regan Temudo](https://linkedin.com/in/regan-temudo) · Tracking the cybersecurity job market · Auto-updated daily via GitHub Actions*
