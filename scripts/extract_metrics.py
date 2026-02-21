import os, re
import pandas as pd
from datetime import datetime

# ── Domain Classifier ─────────────────────────────────────────────────────────
DOMAIN_RULES = {
    "GRC": [
        "grc", "governance", "risk", "compliance", "audit", "iso 27001",
        "soc 2", "gdpr", "hipaa", "pci", "nist", "regulatory", "policy",
        "crisc", "cisa", "archer", "onetrust", "risk manager", "risk analyst",
        "compliance analyst", "compliance manager", "it audit", "internal audit"
    ],
    "SOC": [
        "soc analyst", "threat detection", "incident response", "siem",
        "splunk", "sentinel", "defender", "crowdstrike", "threat intel",
        "security operations", "blue team", "malware analysis", "forensics",
        "edr", "xdr", "soar", "threat hunt", "ioc", "ttp"
    ],
    "Penetration Testing": [
        "penetration test", "pentest", "red team", "ethical hack",
        "vulnerability assessment", "oscp", "offensive security", "exploit",
        "burp suite", "metasploit", "kali", "ceh", "bug bounty",
        "web application testing", "network penetration"
    ],
    "Cloud Security": [
        "cloud security", "devsecops", "aws security", "azure security",
        "gcp security", "container security", "kubernetes security",
        "terraform", "iac security", "cspm", "cwpp", "cloud architect",
        "cloud compliance", "zero trust", "cnapp"
    ],
    "AppSec": [
        "application security", "appsec", "sast", "dast", "secure sdlc",
        "code review", "secure coding", "owasp", "software security",
        "devsecops", "api security", "software composition analysis",
        "threat modeling", "security champion", "sca"
    ],
    "IAM": [
        "identity", "access management", "iam", "privileged access", "pam",
        "okta", "active directory", "azure ad", "single sign-on", "sso",
        "mfa", "zero trust", "identity governance", "sailpoint", "cyberark",
        "ldap", "oauth", "saml", "identity security"
    ],
}

def classify_domain(title, text):
    combined = (title + " " + text).lower()
    scores = {}
    for domain, keywords in DOMAIN_RULES.items():
        scores[domain] = sum(1 for kw in keywords if kw in combined)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "GRC"  # default fallback

# ── Keyword Lists ─────────────────────────────────────────────────────────────
CERTS_BY_DOMAIN = {
    "GRC":                ["cissp", "cisa", "crisc", "cism", "iso 27001", "lead auditor",
                           "lead implementer", "pci-dss", "cobit", "grcp"],
    "SOC":                ["cissp", "ceh", "giac", "gcih", "gcia", "gcfe", "security+",
                           "cysa+", "splunk certified", "microsoft sc-200"],
    "Penetration Testing":["oscp", "osep", "oswe", "ceh", "gpen", "gwapt", "ecppt",
                           "cpent", "pnpt", "eJPT"],
    "Cloud Security":     ["ccsp", "aws certified", "azure security", "google professional",
                           "cissp", "ccsk", "csp"],
    "AppSec":             ["csslp", "gweb", "cissp", "gwapt", "oswe", "security+"],
    "IAM":                ["cissp", "sailpoint", "cyberark defender", "okta certified",
                           "microsoft sc-300", "ciam", "identity+"],
}

TOOLS_BY_DOMAIN = {
    "GRC":                ["servicenow", "archer", "onetrust", "lockpath", "riskonnect",
                           "metricstream", "vanta", "drata", "tugboat logic"],
    "SOC":                ["splunk", "sentinel", "crowdstrike", "defender", "qradar",
                           "elastic", "chronicle", "exabeam", "cortex xsoar", "demisto"],
    "Penetration Testing":["burp suite", "metasploit", "nmap", "nessus", "cobalt strike",
                           "bloodhound", "responder", "impacket", "kali", "nuclei"],
    "Cloud Security":     ["wiz", "prisma cloud", "aqua security", "lacework", "orca",
                           "terraform", "checkov", "snyk", "bridgecrew", "cloudtrail"],
    "AppSec":             ["snyk", "checkmarx", "veracode", "fortify", "sonarqube",
                           "burp suite", "semgrep", "contrast security", "black duck"],
    "IAM":                ["okta", "cyberark", "sailpoint", "beyondtrust", "ping identity",
                           "azure ad", "active directory", "saviynt", "delinea"],
}

FRAMEWORKS_BY_DOMAIN = {
    "GRC":                ["iso 27001", "nist", "soc 2", "gdpr", "hipaa", "pci-dss",
                           "cobit", "itil", "cis controls", "dora", "mas trm"],
    "SOC":                ["mitre att&ck", "nist", "cyber kill chain", "d3fend",
                           "diamond model", "stride"],
    "Penetration Testing":["owasp", "ptes", "osstmm", "nist", "mitre att&ck"],
    "Cloud Security":     ["csa ccm", "aws well-architected", "nist", "cis benchmarks",
                           "soc 2", "iso 27017", "gdpr"],
    "AppSec":             ["owasp", "samm", "bsimm", "nist", "sast", "dast"],
    "IAM":                ["nist", "zero trust", "iso 27001", "soc 2", "gdpr", "hipaa"],
}

SENIORITY_SENIOR = ["senior", "lead", "principal", "manager", "director",
                    "head of", "vp ", "ciso", "chief", "staff"]
SENIORITY_JUNIOR = ["junior", "entry", "associate", "apprentice", "graduate",
                    "intern", "trainee", "analyst i ", "level 1"]

FX = {"AED":0.272,"SGD":0.742,"HKD":0.128,"INR":0.012,"GBP":1.27,
      "USD":1.0,"EUR":1.08,"AUD":0.645,"CAD":0.74,"MYR":0.21}

COUNTRY_MAP = {
    "singapore":"Singapore","hong kong":"Hong Kong","india":"India",
    "mumbai":"India","bengaluru":"India","bangalore":"India",
    "hyderabad":"India","pune":"India","chennai":"India",
    "uae":"UAE","dubai":"UAE","abu dhabi":"UAE",
    "united kingdom":"UK","london":"UK","manchester":"UK",
    "united states":"USA","new york":"USA","remote":"USA",
    "australia":"Australia","sydney":"Australia","melbourne":"Australia",
    "germany":"Germany","frankfurt":"Germany","berlin":"Germany",
    "canada":"Canada","toronto":"Canada","malaysia":"Malaysia",
    "kuala lumpur":"Malaysia",
}

def extract_years(text):
    matches = re.findall(r'(\d+)\+?\s*years?', text.lower())
    nums = [int(m) for m in matches if 0 < int(m) <= 25]
    return max(nums) if nums else 0

def count_keywords(text, keywords):
    return sum(1 for k in keywords if k in text.lower())

def classify_seniority(title, years):
    t = title.lower()
    if any(k in t for k in SENIORITY_SENIOR) or years >= 6: return "Senior"
    if any(k in t for k in SENIORITY_JUNIOR) or years <= 1: return "Junior"
    return "Mid"

def normalize_salary(s):
    if not s or s.strip().lower() in ("not listed","unknown",""): return None
    raw = s.replace(",","").upper()
    cur = next((c for c in FX if c in raw), None)
    if not cur: return None
    nums = [float(n) for n in re.findall(r"[\d]+(?:\.\d+)?", raw)]
    if not nums: return None
    mid = sum(nums)/len(nums)
    if "month" in s.lower(): mid *= 12
    return round(mid * FX[cur], 0)

def extract_country(location):
    loc = location.lower()
    return next((v for k,v in COUNTRY_MAP.items() if k in loc), "Other")

def extract_field(text, field):
    m = re.search(rf'{field}:\s*(.*)', text)
    return m.group(1).strip() if m else "Unknown"

def detect_anomalies(title, years, certs, tools, salary_usd):
    flags = []
    tl = title.lower()
    if years >= 5 and any(k in tl for k in SENIORITY_JUNIOR): flags.append("EXPERIENCE_INFLATION")
    if certs >= 5:  flags.append("CERT_OVERLOAD")
    if tools >= 4:  flags.append("TOOL_STACK_ABUSE")
    if salary_usd and salary_usd < 30000 and years >= 3: flags.append("UNDERPAID_EXPERIENCED")
    if years >= 8 and certs >= 3 and tools >= 2: flags.append("SENIOR_EXPLOITATION")
    return "|".join(flags) if flags else "CLEAN"

def process_month():
    month    = datetime.now().strftime("%Y-%m")
    raw_path = f"data/raw/{month}"
    if not os.path.exists(raw_path):
        print(f"No raw data folder for {month}."); return
    files = [f for f in os.listdir(raw_path) if f.endswith(".txt")]
    if not files:
        print(f"No .txt files in {raw_path}."); return

    records = []
    domain_counts = {}

    for fname in sorted(files):
        with open(os.path.join(raw_path, fname), encoding="utf-8") as f:
            text = f.read()

        title      = extract_field(text, "Title")
        company    = extract_field(text, "Company")
        location   = extract_field(text, "Location")
        salary_raw = extract_field(text, "Salary")
        domain     = extract_field(text, "Domain")
        if domain == "Unknown":
            domain = classify_domain(title, text)

        years      = extract_years(text)
        certs      = count_keywords(text, CERTS_BY_DOMAIN.get(domain, CERTS_BY_DOMAIN["GRC"]))
        tools      = count_keywords(text, TOOLS_BY_DOMAIN.get(domain, TOOLS_BY_DOMAIN["GRC"]))
        frameworks = count_keywords(text, FRAMEWORKS_BY_DOMAIN.get(domain, FRAMEWORKS_BY_DOMAIN["GRC"]))

        salary_usd = normalize_salary(salary_raw)
        seniority  = classify_seniority(title, years)
        country    = extract_country(location)
        anomaly    = detect_anomalies(title, years, certs, tools, salary_usd)

        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        records.append({
            "file": fname, "title": title, "company": company,
            "location": location, "country": country,
            "domain": domain, "seniority": seniority,
            "years_required": years, "cert_count": certs,
            "tool_count": tools, "framework_count": frameworks,
            "salary_raw": salary_raw, "salary_usd": salary_usd,
            "anomaly_flags": anomaly,
        })

    os.makedirs("data/processed", exist_ok=True)
    df = pd.DataFrame(records)
    df.to_csv(f"data/processed/{month}.csv", index=False)
    print(f"✓ {len(records)} jobs extracted → data/processed/{month}.csv")
    print(f"  Domains: {dict(sorted(domain_counts.items(), key=lambda x:-x[1]))}")
    flagged = df[df["anomaly_flags"] != "CLEAN"]
    if not flagged.empty:
        print(f"  ⚠  {len(flagged)} exploitation flags:")
        for _, r in flagged.iterrows():
            print(f"     [{r['anomaly_flags']}] {r['title']} @ {r['company']}")

if __name__ == "__main__":
    process_month()
