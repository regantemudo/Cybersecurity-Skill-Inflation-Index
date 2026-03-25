# 📊 Cybersecurity Skill Inflation Index (CSII)

> **Industry-wide intelligence engine tracking skill inflation across all cybersecurity domains — powered by real job listings, updated automatically.**

[![CSII Automation](https://github.com/regantemudo/Cybersecurity-Skill-Inflation-Index/actions/workflows/csii.yml/badge.svg)](https://github.com/regantemudo/Cybersecurity-Skill-Inflation-Index/actions/workflows/csii.yml)
![Last Updated](https://img.shields.io/badge/Last%20Updated-2026--03-blue?style=flat)
![Skill Score](https://img.shields.io/badge/Skill%20Score-3.41-red?style=flat)
![Avg Years](https://img.shields.io/badge/Avg%20Years-4.3-blue?style=flat)
![Avg Certs](https://img.shields.io/badge/Avg%20Certs-3.1-green?style=flat)
![Avg Tools](https://img.shields.io/badge/Avg%20Tools-2.5-yellow?style=flat)
![Jobs Analyzed](https://img.shields.io/badge/Jobs%20Analyzed-75-brightgreen?style=flat)
![Exploitation Rate](https://img.shields.io/badge/Exploitation%20Rate-62%25-orange?style=flat)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat)

> Scores measure industry-wide requirement trends from public job data. No editorial judgement is made about any individual employer.

---

## ⚠️ Industry Signal — March 2026

> 🔴 **HIGH INFLATION** — Global score **3.41**, above the 3.0 threshold. **62% of all listings** flagged for requirement signals.

| Metric | Value | Signal |
|--------|-------|--------|
| 📈 Global Skill Inflation Score | **3.41** | 🔴 High — above threshold |
| 📅 Avg Years Required | **4.3 yrs** | 🔴 Rising across all domains |
| 🧠 Avg Certifications Demanded | **3.1** | 🟡 Cert creep industry-wide |
| 🛠️ Avg Tools Required | **2.5** | 🔴 High tool complexity |
| ⚠️ Requirement Signal Rate | **62%** | 🔴 Majority of listings flagged |
| 💰 Avg Salary (USD) | **~$58,627** | 🟡 Varies significantly by market |
| 💼 Total Jobs Analyzed | **76** | ✅ 10 domains · 6 countries |
---

## 📈 Global Inflation Trend

![Skill Trend](reports/skill_trend.png)

---

## 🏛️ Domain Intelligence

### Inflation Score by Domain

![Domain Comparison](reports/domain_comparison.png)

| Domain | Avg Years | Avg Certs | Score | Signal | Jobs |
|--------|-----------|-----------|-------|--------|------|
| Network Security | 6.0 | 3.0 | 🔴 **4.65** | every listing flagged; 4.5 avg tools per listing | 2 |
| DFIR | 4.5 | 4.0 | 🔴 **4.35** | every listing flagged; 4.0 avg certs — above market norm | 2 |
| Data Privacy | 5.0 | 5.0 | 🔴 **4.25** | $39,000 avg vs 5+ yrs — below market; 5.0 certs avg — extreme stacking | 2 |
| IAM | 4.8 | 2.2 | 🔴 **3.57** | 5 yrs + 2.2 certs now baseline | 10 |
| OT/ICS Security | 4.7 | 3.0 | 🔴 **3.37** | $49,500 avg vs 5+ yrs — below market | 3 |
| Cloud Security | 3.9 | 3.4 | 🔴 **3.35** | 4 yrs + 3.4 certs now baseline | 8 |
| AppSec | 4.2 | 2.5 | 🔴 **3.20** | 4 yrs + 2.5 certs now baseline | 8 |
| GRC | 4.2 | 3.3 | 🔴 **3.09** | $51,812 avg vs 4+ yrs — below market | 16 |
| SOC | 3.8 | 2.7 | 🔴 **3.03** | 4 yrs + 2.7 certs now baseline | 12 |
| Penetration Testing | 3.8 | 2.1 | 🟡 **2.88** | most balanced — 4 yrs avg, 2.1 certs | 12 |

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
| 2026-03 | 4.32 | 3.12 | 2.50 | **3.41** | 34 |
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
| 🔶 Network Security | Firewall, IDS/IPS, SASE, Network Architecture |
| 🟤 DFIR | Digital Forensics, Malware Analysis, Incident Response |
| ⚫ OT/ICS Security | SCADA, Industrial Control Systems, Critical Infrastructure |
| 🩷 Data Privacy | GDPR, DPDP Act, DLP, Data Governance |

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

**Supported domains:** `GRC` · `SOC` · `Penetration Testing` · `Cloud Security` · `AppSec` · `IAM` · `Network Security` · `DFIR` · `OT/ICS Security` · `Data Privacy`

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
