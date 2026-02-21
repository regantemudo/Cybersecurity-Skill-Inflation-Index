import os, re
import pandas as pd
from datetime import datetime

# ── Keyword Lists ─────────────────────────────────────────────────────────────
CERTIFICATIONS = [
    "cissp", "cisa", "crisc", "ceh", "iso 27001", "security+", "cysa+",
    "comptia", "pci-dss", "lead auditor", "lead implementer", "cism",
    "giac", "gsec", "oscp", "ccsp", "sscp"
]
TOOLS = [
    "servicenow", "archer", "onetrust", "splunk", "qualys", "tenable",
    "jira", "confluence", "rapid7", "crowdstrike", "sentinel", "defender",
    "nessus", "metasploit", "burp suite", "wireshark"
]
FRAMEWORKS = [
    "nist", "soc 2", "gdpr", "hipaa", "pci-dss", "mas trm", "hkma",
    "pdpo", "nist csf", "iso/iec 27001", "cobit", "itil", "cis controls",
    "mitre att&ck", "dora", "cbuae"
]

# ── Seniority Classifier ──────────────────────────────────────────────────────
SENIOR_KEYWORDS = ["senior", "lead", "principal", "manager", "director", "head of", "vp ", "ciso", "chief"]
JUNIOR_KEYWORDS = ["junior", "entry", "associate", "apprentice", "graduate", "intern", "trainee", "0-1", "0-2"]

def classify_seniority(title, years, text):
    title_lower = title.lower()
    text_lower  = text.lower()
    if any(k in title_lower for k in SENIOR_KEYWORDS) or years >= 6:
        return "Senior"
    if any(k in title_lower for k in JUNIOR_KEYWORDS) or years <= 1:
        return "Junior"
    return "Mid"

# ── Salary Normalizer → USD ───────────────────────────────────────────────────
FX = {
    "AED": 0.272,
    "SGD": 0.742,
    "HKD": 0.128,
    "INR": 0.012,
    "GBP": 1.270,
    "USD": 1.000,
    "EUR": 1.080,
    "AUD": 0.645,
}

def normalize_salary_usd(salary_str):
    """Convert any salary string to annual USD. Returns float or None."""
    if not salary_str or salary_str.strip().lower() in ("not listed", ""):
        return None
    s = salary_str.replace(",", "").upper()

    # Detect currency
    currency = None
    for code in FX:
        if code in s:
            currency = code
            break
    if currency is None:
        return None

    # Extract numbers
    nums = re.findall(r"[\d]+(?:\.\d+)?", s)
    if not nums:
        return None
    nums = [float(n) for n in nums]
    mid  = sum(nums) / len(nums)

    # Per month → annual
    if "month" in salary_str.lower() or "monthly" in salary_str.lower():
        mid *= 12

    return round(mid * FX[currency], 0)

# ── Anomaly Detector ──────────────────────────────────────────────────────────
EXPLOITATION_SIGNALS = [
    ("high_years_entry",   lambda years, title, _: years >= 5 and any(k in title.lower() for k in JUNIOR_KEYWORDS)),
    ("cert_overload",      lambda years, _, certs: certs >= 5),
    ("unpaid_senior",      lambda years, __, ___: years >= 5),  # refined below with salary
    ("excessive_stack",    lambda _, __, tools: tools >= 4),
]

def detect_anomalies(title, years, certs, tools, salary_usd):
    flags = []
    title_lower = title.lower()

    if years >= 5 and any(k in title_lower for k in JUNIOR_KEYWORDS):
        flags.append("EXPERIENCE_INFLATION")
    if certs >= 5:
        flags.append("CERT_OVERLOAD")
    if tools >= 4:
        flags.append("TOOL_STACK_ABUSE")
    if salary_usd and salary_usd < 30000 and years >= 3:
        flags.append("UNDERPAID_EXPERIENCED")
    if years >= 8 and certs >= 3 and tools >= 2:
        flags.append("SENIOR_EXPLOITATION")

    return "|".join(flags) if flags else "CLEAN"

# ── Country Extractor ─────────────────────────────────────────────────────────
COUNTRY_MAP = {
    "singapore": "Singapore", "sg": "Singapore",
    "hong kong": "Hong Kong", "hk": "Hong Kong",
    "india": "India", "mumbai": "India", "bengaluru": "India",
    "bangalore": "India", "hyderabad": "India", "pune": "India",
    "uae": "UAE", "dubai": "UAE", "abu dhabi": "UAE",
    "united kingdom": "UK", "london": "UK", "uk": "UK",
    "united states": "USA", "remote": "USA", "usa": "USA",
    "australia": "Australia", "sydney": "Australia",
    "germany": "Germany", "frankfurt": "Germany",
}

def extract_country(location):
    loc = location.lower()
    for key, country in COUNTRY_MAP.items():
        if key in loc:
            return country
    return "Other"

# ── Field Extractors ──────────────────────────────────────────────────────────
def extract_years(text):
    matches = re.findall(r'(\d+)\+?\s*years?', text.lower())
    nums = [int(m) for m in matches if int(m) <= 20]
    return max(nums) if nums else 0

def count_keywords(text, keywords):
    return sum(1 for k in keywords if k in text.lower())

def extract_field(text, field):
    match = re.search(rf'{field}:\s*(.*)', text)
    return match.group(1).strip() if match else "Unknown"

# ── Main Process ──────────────────────────────────────────────────────────────
def process_month():
    month    = datetime.now().strftime("%Y-%m")
    raw_path = f"data/raw/{month}"

    if not os.path.exists(raw_path):
        print(f"No raw data folder for {month}. Skipping.")
        return

    txt_files = [f for f in os.listdir(raw_path) if f.endswith(".txt")]
    if not txt_files:
        print(f"No .txt files in {raw_path}. Skipping.")
        return

    records = []
    for file in sorted(txt_files):
        with open(os.path.join(raw_path, file), "r", encoding="utf-8") as f:
            text = f.read()

        title      = extract_field(text, "Title")
        company    = extract_field(text, "Company")
        location   = extract_field(text, "Location")
        salary_raw = extract_field(text, "Salary")

        years      = extract_years(text)
        certs      = count_keywords(text, CERTIFICATIONS)
        tools      = count_keywords(text, TOOLS)
        frameworks = count_keywords(text, FRAMEWORKS)

        salary_usd = normalize_salary_usd(salary_raw)
        seniority  = classify_seniority(title, years, text)
        country    = extract_country(location)
        anomaly    = detect_anomalies(title, years, certs, tools, salary_usd)

        records.append({
            "file":           file,
            "title":          title,
            "company":        company,
            "location":       location,
            "country":        country,
            "seniority":      seniority,
            "years_required": years,
            "cert_count":     certs,
            "tool_count":     tools,
            "framework_count":frameworks,
            "salary_raw":     salary_raw,
            "salary_usd":     salary_usd,
            "anomaly_flags":  anomaly,
        })

    os.makedirs("data/processed", exist_ok=True)
    df = pd.DataFrame(records)
    df.to_csv(f"data/processed/{month}.csv", index=False)
    print(f"✓ Extracted {len(records)} jobs → data/processed/{month}.csv")

    # Print anomaly summary
    flagged = df[df["anomaly_flags"] != "CLEAN"]
    if not flagged.empty:
        print(f"⚠  {len(flagged)} exploitation flags detected:")
        for _, row in flagged.iterrows():
            print(f"   [{row['anomaly_flags']}] {row['title']} @ {row['company']}")

if __name__ == "__main__":
    process_month()
