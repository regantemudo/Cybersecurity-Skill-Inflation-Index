"""
CSII Automated Job Collector
=============================
Sources:
  1. Adzuna API  — Free. Register at developer.adzuna.com
                   Secrets: ADZUNA_APP_ID, ADZUNA_APP_KEY
  2. JSearch     — 200 free calls/month via RapidAPI
                   Secret: JSEARCH_API_KEY
  3. USAJobs.gov — No key needed. US government roles only.

Usage:
  python scripts/collect.py               # runs all sources
  python scripts/collect.py --source adzuna
  python scripts/collect.py --dry-run     # print without saving
"""

import os, re, time, argparse
import requests
from datetime import datetime
from pathlib import Path

# ── Domain Queries ────────────────────────────────────────────────────────────
DOMAIN_QUERIES = {
    "GRC":                 ["GRC analyst", "governance risk compliance",
                            "cybersecurity compliance", "IT audit cybersecurity",
                            "ISO 27001 analyst", "risk analyst cybersecurity"],
    "SOC":                 ["SOC analyst", "security operations center analyst",
                            "incident response analyst", "threat detection analyst",
                            "threat intelligence analyst"],
    "Penetration Testing": ["penetration tester", "penetration testing",
                            "red team operator", "ethical hacker", "offensive security"],
    "Cloud Security":      ["cloud security engineer", "DevSecOps engineer",
                            "AWS security engineer", "Azure security engineer",
                            "cloud security architect"],
    "AppSec":              ["application security engineer", "AppSec engineer",
                            "SAST DAST security", "secure code review"],
    "IAM":                 ["identity access management engineer", "IAM engineer",
                            "privileged access management", "identity governance"],
}

ADZUNA_COUNTRIES = {
    "gb": "UK", "us": "USA", "in": "India",
    "sg": "Singapore", "au": "Australia",
}

# ── Cybersecurity Filter ──────────────────────────────────────────────────────
# Must match at least one of these to be saved
CYBER_REQUIRED = [
    "security", "cyber", "grc", "soc analyst", "pentest", "penetration",
    "appsec", "identity access", "iam", "infosec", "threat intel",
    "incident response", "vulnerability", "ethical hack", "forensic",
    "compliance analyst", "risk analyst", "audit", "devsecops",
]

# If title matches any of these → not cybersecurity → skip
EXCLUDE_TITLES = [
    "electrical engineer", "power system", "energy market", "marketing analyst",
    "sales", "recruiter", "hr ", "human resource", "accountant", "finance analyst",
    "data scientist", "machine learning", "software developer", "frontend",
    "backend developer", "devops engineer", "product manager", "scrum master",
]

def is_cybersecurity(title, description):
    combined = (title + " " + (description or "")).lower()
    title_lower = title.lower()
    # Reject non-cyber roles
    if any(kw in title_lower for kw in EXCLUDE_TITLES):
        return False
    # Must contain at least one cyber keyword
    return any(kw in combined for kw in CYBER_REQUIRED)

# ── Text Cleaning ─────────────────────────────────────────────────────────────
def clean(text, max_len=4000):
    """Strip HTML tags, extra whitespace, profile insight noise from scraped text."""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', str(text))
    # Remove common scraper noise
    noise = [
        r'Profile insights.*?(?=Job details|Requirements|About|Responsibilities|\Z)',
        r'Here\'s how the job qualifications.*?(?=\n\n|\Z)',
        r'Do you have experience.*?\n',
        r'Do you have a valid.*?\n',
        r'Job details\n.*?Full job description',
        r'&nbsp;',
        r'\d+\.\d+\s*out of \d+ stars',
        r'\d+\s*reviews?·View all jobs',
        r'Add expected salary to your profile.*?\n',
    ]
    for pattern in noise:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
    # Collapse whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()[:max_len]

def extract_salary(text):
    """Try to find salary info in raw text."""
    patterns = [
        r'\$[\d,]+\s*[-–]\s*\$[\d,]+',
        r'[\d,]+\s*[-–]\s*[\d,]+\s*(USD|GBP|SGD|AED|INR|AUD)',
        r'(USD|GBP|SGD|AED|INR|AUD)\s*[\d,]+',
        r'[\d,]+\s*per\s*(month|year|annum)',
        r'salary[:\s]+[\d,\$£€]+',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(0).strip()
    return "Not Listed"

# ── File Helpers ──────────────────────────────────────────────────────────────
def count_existing(folder):
    return len(list(Path(folder).glob("job_*.txt"))) if Path(folder).exists() else 0

def next_filename(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    num = 1
    while (folder / f"job_{num:03d}.txt").exists():
        num += 1
    return folder / f"job_{num:03d}.txt"

def save_job(folder, title, company, location, salary, description, source, domain):
    """Always writes a clean structured job file."""
    fpath = next_filename(folder)
    content = (
        f"Title: {title.strip()}\n"
        f"Company: {company.strip()}\n"
        f"Location: {location.strip()}\n"
        f"Salary: {salary.strip() or 'Not Listed'}\n"
        f"Domain: {domain}\n"
        f"Source: {source}\n"
        f"Collected: {datetime.now().strftime('%Y-%m-%d')}\n"
        f"\nJob Description:\n{description.strip()}\n"
    )
    fpath.write_text(content, encoding="utf-8")
    return fpath.name

# ── Deduplication ─────────────────────────────────────────────────────────────
def deduplicate(folder):
    """Remove files with identical title+company."""
    files = sorted(Path(folder).glob("job_*.txt"))
    seen, removed = set(), 0
    for fpath in files:
        text    = fpath.read_text(encoding="utf-8", errors="ignore")
        t_match = re.search(r'Title:\s*(.*)', text)
        c_match = re.search(r'Company:\s*(.*)', text)
        key = (
            t_match.group(1).lower().strip() if t_match else "",
            c_match.group(1).lower().strip() if c_match else "",
        )
        if key in seen and key != ("", ""):
            fpath.unlink()
            removed += 1
        else:
            seen.add(key)
    if removed:
        print(f"  ✓ Deduplication removed {removed} duplicate(s)")
    return removed

# ── Source 1: Adzuna ──────────────────────────────────────────────────────────
def collect_adzuna(folder, dry_run=False, max_per_query=5):
    app_id  = os.environ.get("ADZUNA_APP_ID", "")
    app_key = os.environ.get("ADZUNA_APP_KEY", "")
    if not app_id or not app_key:
        print("  ⚠  Adzuna: ADZUNA_APP_ID / ADZUNA_APP_KEY not set.")
        print("     Register free at: https://developer.adzuna.com/")
        return 0

    saved = 0
    for country_code, country_name in ADZUNA_COUNTRIES.items():
        for domain, queries in DOMAIN_QUERIES.items():
            for query in queries[:2]:
                url = (
                    f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
                    f"?app_id={app_id}&app_key={app_key}"
                    f"&results_per_page={max_per_query}"
                    f"&what={requests.utils.quote(query)}"
                    f"&content-type=application/json&sort_by=date"
                )
                try:
                    r = requests.get(url, timeout=15)
                    if r.status_code != 200:
                        continue
                    for job in r.json().get("results", []):
                        title   = clean(job.get("title", ""))
                        company = clean(job.get("company", {}).get("display_name", "Unknown"))
                        loc     = clean(job.get("location", {}).get("display_name", country_name))
                        desc    = clean(job.get("description", ""))
                        sal_min = job.get("salary_min")
                        sal_max = job.get("salary_max")
                        salary  = (f"${sal_min:,.0f} - ${sal_max:,.0f} annually"
                                   if sal_min and sal_max else "Not Listed")

                        if not title or not is_cybersecurity(title, desc):
                            continue
                        if dry_run:
                            print(f"  [DRY] [{domain}] {title[:50]} @ {company[:25]}")
                            saved += 1
                            continue
                        fname = save_job(folder, title, company, loc, salary, desc, "Adzuna", domain)
                        print(f"  ✓ {fname} — {title[:45]} @ {company[:25]} [{domain}]")
                        saved += 1
                    time.sleep(0.5)
                except Exception as e:
                    print(f"  ✗ Adzuna ({country_code}/{query[:20]}): {e}")
    return saved

# ── Source 2: JSearch ─────────────────────────────────────────────────────────
def collect_jsearch(folder, dry_run=False, max_per_query=5):
    api_key = os.environ.get("JSEARCH_API_KEY", "")
    if not api_key:
        print("  ⚠  JSearch: JSEARCH_API_KEY not set.")
        print("     Get free key at: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch")
        return 0

    headers = {
        "X-RapidAPI-Key":  api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }
    saved = 0
    for domain, queries in DOMAIN_QUERIES.items():
        for query in queries[:1]:   # 1 query per domain — conserve free tier
            try:
                r = requests.get(
                    "https://jsearch.p.rapidapi.com/search",
                    headers=headers,
                    params={"query": query, "num_pages": "1", "date_posted": "month"},
                    timeout=15,
                )
                if r.status_code != 200:
                    continue
                for job in r.json().get("data", [])[:max_per_query]:
                    title   = clean(job.get("job_title", ""))
                    company = clean(job.get("employer_name", "Unknown"))
                    city    = job.get("job_city", "")
                    country = job.get("job_country", "")
                    loc     = f"{city}, {country}".strip(", ")
                    desc    = clean(job.get("job_description", ""))
                    sal_min = job.get("job_min_salary")
                    sal_max = job.get("job_max_salary")
                    salary  = (f"${sal_min:,.0f} - ${sal_max:,.0f} annually"
                               if sal_min and sal_max else extract_salary(desc))

                    if not title or not is_cybersecurity(title, desc):
                        continue
                    if dry_run:
                        print(f"  [DRY] [{domain}] {title[:50]} @ {company[:25]}")
                        saved += 1
                        continue
                    fname = save_job(folder, title, company, loc, salary, desc, "JSearch", domain)
                    print(f"  ✓ {fname} — {title[:45]} @ {company[:25]} [{domain}]")
                    saved += 1
                time.sleep(1)
            except Exception as e:
                print(f"  ✗ JSearch ({query[:20]}): {e}")
    return saved

# ── Source 3: USAJobs.gov ─────────────────────────────────────────────────────
def collect_usajobs(folder, dry_run=False):
    headers = {
        "Host":              "data.usajobs.gov",
        "User-Agent":        "csii-collector/1.0",
        "Authorization-Key": os.environ.get("USAJOBS_API_KEY", ""),
    }
    keywords = ["cybersecurity analyst", "information security", "SOC analyst",
                "penetration tester", "cloud security", "GRC analyst"]
    saved = 0
    for kw in keywords:
        try:
            r = requests.get(
                "https://data.usajobs.gov/api/search",
                headers=headers,
                params={"Keyword": kw, "ResultsPerPage": 8},
                timeout=15,
            )
            if r.status_code != 200:
                continue
            for item in r.json().get("SearchResult", {}).get("SearchResultItems", []):
                m       = item.get("MatchedObjectDescriptor", {})
                title   = clean(m.get("PositionTitle", ""))
                company = clean(m.get("OrganizationName", "US Government"))
                locs    = m.get("PositionLocation", [{}])
                loc     = locs[0].get("LocationName", "USA") if locs else "USA"
                desc    = clean(m.get("UserArea", {}).get("Details", {}).get("JobSummary", ""))
                rem     = m.get("PositionRemuneration", [{}])
                sal_min = rem[0].get("MinimumRange", "") if rem else ""
                sal_max = rem[0].get("MaximumRange", "") if rem else ""
                salary  = (f"${float(sal_min):,.0f} - ${float(sal_max):,.0f} annually"
                           if sal_min and sal_max else "Not Listed")
                domain  = _classify(title, desc)

                if not title or not is_cybersecurity(title, desc):
                    continue
                if dry_run:
                    print(f"  [DRY] [{domain}] {title[:50]} @ {company[:25]}")
                    saved += 1
                    continue
                fname = save_job(folder, title, company, loc, salary, desc, "USAJobs", domain)
                print(f"  ✓ {fname} — {title[:45]} @ {company[:25]} [{domain}]")
                saved += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ USAJobs ({kw}): {e}")
    return saved

def _classify(title, text):
    c = (title + " " + text).lower()
    if any(k in c for k in ["soc", "threat", "incident", "siem", "detection"]): return "SOC"
    if any(k in c for k in ["pentest", "penetration", "red team", "offensive"]): return "Penetration Testing"
    if any(k in c for k in ["cloud security", "devsecops", "aws security"]): return "Cloud Security"
    if any(k in c for k in ["appsec", "application security", "sast", "owasp"]): return "AppSec"
    if any(k in c for k in ["identity", "iam", "okta", "cyberark", "access management"]): return "IAM"
    return "GRC"

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="CSII Job Collector")
    parser.add_argument("--source",  choices=["adzuna","jsearch","usajobs","all"], default="all")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max",     type=int, default=5)
    args = parser.parse_args()

    month  = datetime.now().strftime("%Y-%m")
    folder = Path(f"data/raw/{month}")
    before = count_existing(folder)

    print(f"\n{'='*55}")
    print(f"  CSII Job Collector — {month}")
    print(f"  Mode: {'DRY RUN' if args.dry_run else 'LIVE'} | Source: {args.source}")
    print(f"  Existing: {before} jobs")
    print(f"{'='*55}\n")

    total = 0
    if args.source in ("adzuna", "all"):
        print("[ Adzuna ]")
        total += collect_adzuna(folder, args.dry_run, args.max)
    if args.source in ("jsearch", "all"):
        print("\n[ JSearch ]")
        total += collect_jsearch(folder, args.dry_run, args.max)
    if args.source in ("usajobs", "all"):
        print("\n[ USAJobs ]")
        total += collect_usajobs(folder, args.dry_run)

    if not args.dry_run:
        print(f"\n[ Deduplication ]")
        deduplicate(folder)
        after = count_existing(folder)
        print(f"\n{'='*55}")
        print(f"  Done. New jobs added: {after - before}  |  Total: {after}")
        print(f"{'='*55}\n")
    else:
        print(f"\n  [DRY RUN] Would collect ~{total} jobs.\n")

if __name__ == "__main__":
    main()
