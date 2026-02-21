import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os, re, glob

# ── Style ────────────────────────────────────────────────────────────────────
BG       = "#080c10"
SURFACE  = "#0d1318"
BORDER   = "#1e2d3a"
ACCENT   = "#00e5ff"
RED      = "#ff4560"
GREEN    = "#00e676"
YELLOW   = "#ffab00"
TEXT     = "#e8f0f7"
MUTED    = "#4a6378"
COLORS   = [ACCENT, RED, YELLOW, GREEN, "#c084fc", "#fb923c", "#f472b6", "#34d399"]

def apply_style(ax, title=""):
    ax.set_facecolor(SURFACE)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(BORDER)
    ax.spines["bottom"].set_color(BORDER)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    if title:
        ax.set_title(title, color=TEXT, fontsize=11, fontweight="bold", pad=12)

# ── Chart 1: Skill Inflation Trend ───────────────────────────────────────────
def chart_trend(df):
    fig, ax = plt.subplots(figsize=(10, 4), facecolor=BG)
    ax.plot(df["month"], df["skill_score"],  color=ACCENT,  linewidth=2.5, marker="o", markersize=6, label="Skill Score")
    ax.plot(df["month"], df["avg_years"],    color=RED,     linewidth=2,   marker="s", markersize=5, linestyle="--", label="Avg Years")
    ax.plot(df["month"], df["avg_certs"],    color=YELLOW,  linewidth=2,   marker="^", markersize=5, linestyle=":",  label="Avg Certs")
    ax.fill_between(df["month"], df["skill_score"], alpha=0.08, color=ACCENT)
    apply_style(ax, "Cybersecurity Skill Inflation — Monthly Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Score / Count")
    plt.xticks(rotation=30, ha="right")
    legend = ax.legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)
    plt.tight_layout()
    plt.savefig("reports/skill_trend.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print("Chart saved: skill_trend.png")

# ── Chart 2: Certification Demand ────────────────────────────────────────────
def chart_cert_demand():
    month = pd.Timestamp.now().strftime("%Y-%m")
    path  = f"data/processed/{month}.csv"
    if not os.path.exists(path):
        return

    df   = pd.read_csv(path)
    text = " ".join(open(f, encoding="utf-8").read().lower()
                    for f in glob.glob(f"data/raw/{month}/*.txt"))

    certs = {
        "CISSP": text.count("cissp"),
        "CISA":  text.count("cisa"),
        "CRISC": text.count("crisc"),
        "CEH":   text.count("ceh"),
        "ISO 27001": text.count("iso 27001"),
        "Security+": text.count("security+"),
    }
    certs = {k: v for k, v in sorted(certs.items(), key=lambda x: -x[1]) if v > 0}
    if not certs:
        return

    fig, ax = plt.subplots(figsize=(7, 4), facecolor=BG)
    bars = ax.barh(list(certs.keys()), list(certs.values()),
                   color=[COLORS[i % len(COLORS)] for i in range(len(certs))],
                   height=0.6, edgecolor="none")
    for bar, val in zip(bars, certs.values()):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                str(val), va="center", color=TEXT, fontsize=9)
    apply_style(ax, "Certification Demand — Mentions in Job Descriptions")
    ax.set_xlabel("Mentions")
    ax.invert_yaxis()
    ax.tick_params(axis="y", colors=TEXT)
    plt.tight_layout()
    plt.savefig("reports/cert_demand.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print("Chart saved: cert_demand.png")

# ── Chart 3: Tool Demand ─────────────────────────────────────────────────────
def chart_tool_demand():
    month = pd.Timestamp.now().strftime("%Y-%m")
    text  = " ".join(open(f, encoding="utf-8").read().lower()
                     for f in glob.glob(f"data/raw/{month}/*.txt"))

    tools = {
        "ServiceNow": text.count("servicenow"),
        "Archer":     text.count("archer"),
        "OneTrust":   text.count("onetrust"),
        "Splunk":     text.count("splunk"),
        "Qualys":     text.count("qualys"),
        "Tenable":    text.count("tenable"),
    }
    tools = {k: v for k, v in sorted(tools.items(), key=lambda x: -x[1]) if v > 0}
    if not tools:
        return

    fig, ax = plt.subplots(figsize=(7, 4), facecolor=BG)
    wedges, texts, autotexts = ax.pie(
        tools.values(),
        labels=tools.keys(),
        autopct="%1.0f%%",
        colors=COLORS[:len(tools)],
        startangle=140,
        wedgeprops=dict(edgecolor=BG, linewidth=2)
    )
    for t in texts:      t.set_color(TEXT);  t.set_fontsize(10)
    for a in autotexts:  a.set_color(BG);    a.set_fontsize(9); a.set_fontweight("bold")
    ax.set_title("Tool Stack Demand — Share of Mentions", color=TEXT, fontsize=11, fontweight="bold")
    fig.patch.set_facecolor(BG)
    plt.tight_layout()
    plt.savefig("reports/tool_demand.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print("Chart saved: tool_demand.png")

# ── Chart 4: Experience Distribution ─────────────────────────────────────────
def chart_experience():
    month = pd.Timestamp.now().strftime("%Y-%m")
    path  = f"data/processed/{month}.csv"
    if not os.path.exists(path):
        return

    df = pd.read_csv(path)
    buckets = {"0 (Entry)": 0, "1–2 yrs": 0, "3–5 yrs": 0, "6–8 yrs": 0, "9+ yrs": 0}
    for y in df["years_required"]:
        if y == 0:    buckets["0 (Entry)"] += 1
        elif y <= 2:  buckets["1–2 yrs"]  += 1
        elif y <= 5:  buckets["3–5 yrs"]  += 1
        elif y <= 8:  buckets["6–8 yrs"]  += 1
        else:         buckets["9+ yrs"]   += 1

    buckets = {k: v for k, v in buckets.items() if v > 0}
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=BG)
    bars = ax.bar(buckets.keys(), buckets.values(),
                  color=[GREEN, ACCENT, YELLOW, RED, "#c084fc"][:len(buckets)],
                  width=0.5, edgecolor="none")
    for bar, val in zip(bars, buckets.values()):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                str(val), ha="center", color=TEXT, fontsize=10, fontweight="bold")
    apply_style(ax, "Experience Required — Distribution of Job Postings")
    ax.set_ylabel("Job Count")
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    plt.tight_layout()
    plt.savefig("reports/experience_distribution.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print("Chart saved: experience_distribution.png")

# ── README Badge Updater ──────────────────────────────────────────────────────
def update_readme(df):
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        return

    latest    = df.iloc[-1]
    month     = latest["month"]
    score     = f"{latest['skill_score']:.2f}"
    years     = f"{latest['avg_years']:.1f}"
    certs     = f"{latest['avg_certs']:.1f}"
    tools     = f"{latest['avg_tools']:.1f}"
    job_count = int(latest.get("job_count", 0))
    total     = int(df["job_count"].sum()) if "job_count" in df.columns else job_count

    # Build history table rows
    history_rows = ""
    for _, row in df.iterrows():
        jc = int(row.get("job_count", 0))
        history_rows += f"| {row['month']} | {row['avg_years']:.2f} | {row['avg_certs']:.2f} | {row['avg_tools']:.2f} | **{row['skill_score']:.2f}** | {jc} |\n"

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    def replace_badge(content, label, value, color):
        pattern = rf'!\[{re.escape(label)}\]\(https://img\.shields\.io/badge/[^)]*\)'
        encoded_val = str(value).replace("-", "--").replace("_", "__").replace(" ", "%20")
        encoded_label = label.replace("-", "--").replace("_", "__").replace(" ", "%20")
        new_badge = f"![{label}](https://img.shields.io/badge/{encoded_label}-{encoded_val}-{color}?style=flat)"
        result = re.sub(pattern, new_badge, content)
        return result

    content = replace_badge(content, "Skill Score",    score,            "red")
    content = replace_badge(content, "Avg Years",      years,            "blue")
    content = replace_badge(content, "Avg Certs",      certs,            "green")
    content = replace_badge(content, "Avg Tools",      tools,            "yellow")
    content = replace_badge(content, "Jobs Analyzed",  total,            "brightgreen")
    content = replace_badge(content, "Last Updated",   month,            "blue")

    # Replace history table block
    history_block = (
        "| Month | Avg Years | Avg Certs | Avg Tools | Skill Score | Jobs |\n"
        "|-------|-----------|-----------|-----------|-------------|------|\n"
        + history_rows
    )
    content = re.sub(
        r'\| Month \| Avg Years.*?(?=\n##|\Z)',
        history_block.rstrip(),
        content,
        flags=re.DOTALL
    )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"README.md updated with latest data for {month}")

# ── Main ──────────────────────────────────────────────────────────────────────
def generate():
    index_path = "data/processed/monthly_index.csv"
    if not os.path.exists(index_path):
        print("No monthly_index.csv found. Run calculate_index.py first.")
        return

    df = pd.read_csv(index_path)
    os.makedirs("reports", exist_ok=True)

    chart_trend(df)
    chart_cert_demand()
    chart_tool_demand()
    chart_experience()
    update_readme(df)

    latest = df.iloc[-1]
    report = f"""# Cybersecurity Skill Inflation Index — Monthly Report

**Month:** {latest['month']}

## Key Metrics

| Metric | Value |
|--------|-------|
| Average Years Required | {latest['avg_years']:.2f} |
| Average Certifications | {latest['avg_certs']:.2f} |
| Average Tools | {latest['avg_tools']:.2f} |
| Average Frameworks | {latest.get('avg_frameworks', 'N/A')} |
| **Skill Inflation Score** | **{latest['skill_score']:.2f}** |
| Jobs Analyzed | {int(latest.get('job_count', 0))} |

## Signal

{"🔴 HIGH INFLATION — Requirements significantly outpacing market value." if float(latest['skill_score']) > 3.0
 else "🟡 MODERATE INFLATION — Monitor closely." if float(latest['skill_score']) > 2.0
 else "🟢 HEALTHY MARKET — Requirements proportional."}

## Charts

![Trend](skill_trend.png)
![Certs](cert_demand.png)
![Tools](tool_demand.png)
![Experience](experience_distribution.png)
"""
    with open("reports/Monthly-CSII-Report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("Report saved: reports/Monthly-CSII-Report.md")

if __name__ == "__main__":
    generate()
