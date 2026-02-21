"""
CSII Automated Job Collector
=============================
Sources:
  1. Adzuna API     — Free. Register at developer.adzuna.com
                      Set secrets: ADZUNA_APP_ID, ADZUNA_APP_KEY
  2. JSearch        — 200 free calls/month via RapidAPI
                      Set secret: JSEARCH_API_KEY
  3. USAJobs.gov    — No key needed. US government roles only.

GitHub Secrets needed (Settings → Secrets → Actions):
  ADZUNA_APP_ID
  ADZUNA_APP_KEY
  JSEARCH_API_KEY   (optional)

Usage:
  python scripts/collect.py               # runs all sources
  python scripts/collect.py --source adzuna
  python scripts/collect.py --source usajobs
  python scripts/collect.py --dry-run     # print without saving
"""

import os, re, time, json, argparse
import requests
from datetime import datetime
from pathlib import Path

# ── Search Queries per Domain ─────────────────────────────────────────────────
DOMAIN_QUERIES = {
    "GRC":                 ["GRC analyst", "governance risk compliance", "cybersecurity compliance",
                            "ISO 27001 analyst", "risk analyst cybersecurity", "IT audit cybersecurity"],
    "SOC":                 ["SOC analyst", "security operations center", "threat detection analyst",
                            "incident response analyst", "threat intelligence analyst"],
    "Penetration Testing": ["penetration tester", "penetration testing", "red team operator",
                            "ethical hacker", "offensive security"],
    "Cloud Security":      ["cloud security engineer", "DevSecOps engineer", "cloud security architect",
                            "AWS security engineer", "Azure security engineer"],
    "AppSec":              ["application security engineer", "AppSec engineer",
                            "secure code review", "SAST DAST security"],
    "IAM":                 ["identity access management", "IAM engineer", "privileged access management",
                            "identity governance", "Okta engineer CyberArk"],
}

# Countries → Adzuna country codes
ADZUNA_COUNTRIES = {
    "gb": "UK",
    "us": "USA",
    "in": "India",
    "sg": "Singapore",
    "au": "Australia",
}

REQUIRED_KEYWORDS = [
    "security", "cyber", "grc", "compliance", "soc", "pentest",
    "penetration", "appsec", "identity", "iam", "cloud security",
    "risk", "audit", "governance", "infosec"
]

def is_cybersecurity(title, description):
    combined = (title + " " + (description or "")).lower()
    return any(kw in combined for kw in REQUIRED_KEYWORDS)

def sanitize(text):
    if not text: return ""
    text = re.sub(r'<[^>]+>', ' ', str(text))
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:4000]

def make_filename(folder, existing_count):
    num = existing_count + 1
    while (folder / f"job_{num:03d}.txt").exists():
        num += 1
    return folder / f"job_{num:03d}.txt"

def count_existing(folder):
    return len(list(folder.glob("job_*.txt")))

def save_job(folder, title, company, location, salary, description, source, domain):
    folder.mkdir(parents=True, exist_ok=True)
    existing = count_existing(folder)
    fpath = make_filename(folder, existing)

    content = f"""Title: {sanitize(title)}
Company: {sanitize(company)}
Location: {sanitize(location)}
Salary: {sanitize(salary) or 'Not Listed'}
Domain: {domain}
Source: {source}
Collected: {datetime.now().strftime('%Y-%m-%d')}

Job Description:
{sanitize(description)}
"""
    fpath.write_text(content, encoding="utf-8")
    return fpath.name

# ── Source 1: Adzuna ──────────────────────────────────────────────────────────
def collect_adzuna(folder, dry_run=False, max_per_query=5):
    app_id  = os.environ.get("ADZUNA_APP_ID", "")
    app_key = os.environ.get("ADZUNA_APP_KEY", "")
    if not app_id or not app_key:
        print("  ⚠  Adzuna: ADZUNA_APP_ID / ADZUNA_APP_KEY not set. Skipping.")
        print("     Register free at: https://developer.adzuna.com/")
        return 0

    saved = 0
    for country_code, country_name in ADZUNA_COUNTRIES.items():
        for domain, queries in DOMAIN_QUERIES.items():
            for query in queries[:2]:   # top 2 queries per domain per country
                url = (f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
                       f"?app_id={app_id}&app_key={app_key}"
                       f"&results_per_page={max_per_query}"
                       f"&what={requests.utils.quote(query)}"
                       f"&content-type=application/json"
                       f"&sort_by=date")
                try:
                    r = requests.get(url, timeout=15)
                    if r.status_code != 200:
                        continue
                    data = r.json()
                    for job in data.get("results", []):
                        title   = job.get("title", "")
                        company = job.get("company", {}).get("display_name", "Unknown")
                        loc     = job.get("location", {}).get("display_name", country_name)
                        desc    = job.get("description", "")
                        sal_min = job.get("salary_min")
                        sal_max = job.get("salary_max")
                        salary  = (f"${sal_min:,.0f} - ${sal_max:,.0f} annually"
                                   if sal_min and sal_max else "Not Listed")

                        if not is_cybersecurity(title, desc):
                            continue
                        if dry_run:
                            print(f"  [DRY] {domain} | {title} @ {company} ({country_name})")
                            saved += 1
                            continue
                        fname = save_job(folder, title, company, loc, salary, desc, "Adzuna", domain)
                        print(f"  ✓ {fname} — {title[:45]} @ {company[:25]} [{domain}]")
                        saved += 1
                    time.sleep(0.5)
                except Exception as e:
                    print(f"  ✗ Adzuna error ({country_code}/{query}): {e}")
    return saved

# ── Source 2: JSearch (RapidAPI) ──────────────────────────────────────────────
def collect_jsearch(folder, dry_run=False, max_per_query=5):
    api_key = os.environ.get("JSEARCH_API_KEY", "")
    if not api_key:
        print("  ⚠  JSearch: JSEARCH_API_KEY not set. Skipping.")
        print("     Get free key at: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch")
        return 0

    headers = {
        "X-RapidAPI-Key":  api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    saved = 0
    for domain, queries in DOMAIN_QUERIES.items():
        for query in queries[:1]:   # 1 query per domain (conserve free tier)
            params = {"query": query, "num_pages": "1", "page": "1", "date_posted": "month"}
            try:
                r = requests.get("https://jsearch.p.rapidapi.com/search",
                                 headers=headers, params=params, timeout=15)
                if r.status_code != 200:
                    continue
                for job in r.json().get("data", [])[:max_per_query]:
                    title   = job.get("job_title", "")
                    company = job.get("employer_name", "Unknown")
                    city    = job.get("job_city", "")
                    country = job.get("job_country", "")
                    loc     = f"{city}, {country}".strip(", ")
                    desc    = job.get("job_description", "")
                    sal_min = job.get("job_min_salary")
                    sal_max = job.get("job_max_salary")
                    salary  = (f"${sal_min:,.0f} - ${sal_max:,.0f} annually"
                               if sal_min and sal_max else "Not Listed")

                    if not is_cybersecurity(title, desc):
                        continue
                    if dry_run:
                        print(f"  [DRY] {domain} | {title} @ {company}")
                        saved += 1
                        continue
                    fname = save_job(folder, title, company, loc, salary, desc, "JSearch", domain)
                    print(f"  ✓ {fname} — {title[:45]} @ {company[:25]} [{domain}]")
                    saved += 1
                time.sleep(1)
            except Exception as e:
                print(f"  ✗ JSearch error ({query}): {e}")
    return saved

# ── Source 3: USAJobs.gov ─────────────────────────────────────────────────────
def collect_usajobs(folder, dry_run=False, max_results=30):
    """No API key required for basic search."""
    headers = {
        "Host":             "data.usajobs.gov",
        "User-Agent":       "csii-collector/1.0",
        "Authorization-Key": os.environ.get("USAJOBS_API_KEY", ""),
    }
    keywords = ["cybersecurity", "information security", "GRC analyst",
                 "SOC analyst", "penetration tester", "cloud security"]
    saved = 0
    for kw in keywords:
        params = {
            "Keyword":          kw,
            "ResultsPerPage":   10,
            "Fields":           "min",
        }
        try:
            r = requests.get("https://data.usajobs.gov/api/search",
                             headers=headers, params=params, timeout=15)
            if r.status_code != 200:
                continue
            items = r.json().get("SearchResult", {}).get("SearchResultItems", [])
            for item in items:
                m       = item.get("MatchedObjectDescriptor", {})
                title   = m.get("PositionTitle", "")
                company = m.get("OrganizationName", "US Government")
                loc_list= m.get("PositionLocation", [{}])
                loc     = loc_list[0].get("LocationName", "USA") if loc_list else "USA"
                desc    = m.get("UserArea", {}).get("Details", {}).get("JobSummary", "")
                sal_min = m.get("PositionRemuneration", [{}])[0].get("MinimumRange", "")
                sal_max = m.get("PositionRemuneration", [{}])[0].get("MaximumRange", "")
                salary  = f"${float(sal_min):,.0f} - ${float(sal_max):,.0f} annually" if sal_min and sal_max else "Not Listed"

                if not is_cybersecurity(title, desc):
                    continue
                domain = classify_domain_simple(title, desc)
                if dry_run:
                    print(f"  [DRY] {domain} | {title} @ {company}")
                    saved += 1
                    continue
                fname = save_job(folder, title, company, loc, salary, desc, "USAJobs", domain)
                print(f"  ✓ {fname} — {title[:45]} @ {company[:25]} [{domain}]")
                saved += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ USAJobs error ({kw}): {e}")
    return saved

def classify_domain_simple(title, text):
    combined = (title + " " + text).lower()
    if any(k in combined for k in ["soc", "threat", "incident", "siem", "detection"]): return "SOC"
    if any(k in combined for k in ["pentest", "penetration", "red team", "offensive"]): return "Penetration Testing"
    if any(k in combined for k in ["cloud", "devsecops", "aws", "azure security"]): return "Cloud Security"
    if any(k in combined for k in ["appsec", "application security", "owasp", "sast"]): return "AppSec"
    if any(k in combined for k in ["identity", "iam", "access management", "okta", "cyberark"]): return "IAM"
    return "GRC"

# ── Deduplication ─────────────────────────────────────────────────────────────
def deduplicate(folder):
    """Remove duplicate jobs (same title + company in same month)."""
    files = list(folder.glob("job_*.txt"))
    seen  = set()
    removed = 0
    for fpath in files:
        text    = fpath.read_text(encoding="utf-8")
        title   = re.search(r'Title:\s*(.*)', text)
        company = re.search(r'Company:\s*(.*)', text)
        key = (
            (title.group(1).lower().strip() if title else ""),
            (company.group(1).lower().strip() if company else ""),
        )
        if key in seen and key != ("", ""):
            fpath.unlink()
            removed += 1
        else:
            seen.add(key)
    if removed:
        print(f"  ✓ Deduplication: removed {removed} duplicate(s)")
    return removed

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="CSII Job Collector")
    parser.add_argument("--source",  choices=["adzuna","jsearch","usajobs","all"], default="all")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max",     type=int, default=5, help="Max jobs per query")
    args = parser.parse_args()

    month  = datetime.now().strftime("%Y-%m")
    folder = Path(f"data/raw/{month}")
    before = count_existing(folder)

    print(f"\n{'='*55}")
    print(f"  CSII Job Collector — {month}")
    print(f"  Mode: {'DRY RUN' if args.dry_run else 'LIVE'} | Source: {args.source}")
    print(f"  Folder: {folder}  (existing: {before} jobs)")
    print(f"{'='*55}\n")

    total = 0
    if args.source in ("adzuna", "all"):
        print("[ Adzuna ]")
        total += collect_adzuna(folder, args.dry_run, args.max)
    if args.source in ("jsearch", "all"):
        print("\n[ JSearch / Google Jobs ]")
        total += collect_jsearch(folder, args.dry_run, args.max)
    if args.source in ("usajobs", "all"):
        print("\n[ USAJobs.gov ]")
        total += collect_usajobs(folder, args.dry_run, args.max)

    if not args.dry_run:
        print(f"\n[ Deduplication ]")
        deduplicate(folder)
        after = count_existing(folder)
        print(f"\n{'='*55}")
        print(f"  Done. Added {after - before} new jobs. Total: {after}")
        print(f"{'='*55}\n")
    else:
        print(f"\n[DRY RUN] Would collect ~{total} jobs.")

if __name__ == "__main__":
    main()
