import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
import os, re, glob

# ── Theme ─────────────────────────────────────────────────────────────────────
BG=     "#080c10"; SURFACE="#0d1318"; BORDER="#1e2d3a"
ACCENT= "#00e5ff"; RED=    "#ff4560"; GREEN= "#00e676"
YELLOW= "#ffab00"; PURPLE= "#c084fc"; ORANGE="#fb923c"
PINK=   "#f472b6"; TEAL=   "#2dd4bf"; TEXT=  "#e8f0f7"
MUTED=  "#4a6378"

DOMAIN_COLORS = {
    "GRC":                 ACCENT,
    "SOC":                 RED,
    "Penetration Testing": ORANGE,
    "Cloud Security":      TEAL,
    "AppSec":              PURPLE,
    "IAM":                 GREEN,
}

def sf(w=10, h=4):
    fig, ax = plt.subplots(figsize=(w,h), facecolor=BG)
    ax.set_facecolor(SURFACE)
    return fig, ax

def ax_style(ax, title=""):
    for sp in ["top","right"]: ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(BORDER)
    ax.spines["bottom"].set_color(BORDER)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    if title: ax.set_title(title, color=TEXT, fontsize=11, fontweight="bold", pad=12)

def save(path):
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"  ✓ {path}")

# ── 1. Global Trend ───────────────────────────────────────────────────────────
def chart_global_trend(df):
    fig, ax = sf(10, 4)
    ax.plot(df["month"], df["skill_score"], color=ACCENT, lw=2.5, marker="o", ms=6, label="Global Score", zorder=3)
    ax.plot(df["month"], df["avg_years"],   color=RED,    lw=2,   marker="s", ms=5, ls="--", label="Avg Years")
    ax.plot(df["month"], df["avg_certs"],   color=YELLOW, lw=2,   marker="^", ms=5, ls=":",  label="Avg Certs")
    ax.fill_between(df["month"], df["skill_score"], alpha=0.07, color=ACCENT)
    ax.axhline(y=3.0, color=RED, lw=1, ls="--", alpha=0.4)
    ax.text(0.01, 0.96, "Inflation Threshold → 3.0", transform=ax.transAxes,
            color=RED, fontsize=8, alpha=0.7, va="top")
    ax_style(ax, "Cybersecurity Industry — Skill Inflation Trend")
    ax.set_ylabel("Score"); ax.grid(axis="y", color=BORDER, lw=0.5, alpha=0.5)
    plt.xticks(rotation=30, ha="right")
    ax.legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)
    save("reports/skill_trend.png")

# ── 2. Domain Score Comparison ────────────────────────────────────────────────
def chart_domain_comparison(month):
    path = "data/processed/domain_index.csv"
    if not os.path.exists(path): return
    df = pd.read_csv(path)
    df = df[df["month"]==month].sort_values("skill_score", ascending=True)
    if df.empty: return

    fig, axes = plt.subplots(1, 2, figsize=(14, max(4, len(df)*0.7)), facecolor=BG)
    colors = [DOMAIN_COLORS.get(d, MUTED) for d in df["domain"]]

    # Left: Skill Score bars
    axes[0].set_facecolor(SURFACE)
    bars = axes[0].barh(df["domain"], df["skill_score"], color=colors, height=0.55, edgecolor="none")
    axes[0].axvline(x=3.0, color=RED, lw=1.5, ls="--", alpha=0.5)
    for bar, val in zip(bars, df["skill_score"]):
        axes[0].text(bar.get_width()+0.04, bar.get_y()+bar.get_height()/2,
                     f"{val:.2f}", va="center", color=TEXT, fontsize=10, fontweight="bold")
    ax_style(axes[0], "Skill Inflation Score by Domain")
    axes[0].set_xlabel("Score"); axes[0].tick_params(axis="y", colors=TEXT, labelsize=10)
    axes[0].set_xlim(0, max(df["skill_score"].max()*1.25, 4))

    # Right: Grouped bars — years / certs / tools
    x, w = np.arange(len(df)), 0.25
    axes[1].set_facecolor(SURFACE)
    axes[1].bar(x-w,   df["avg_years"].values, w, label="Avg Years", color=ACCENT, edgecolor="none")
    axes[1].bar(x,     df["avg_certs"].values, w, label="Avg Certs", color=YELLOW, edgecolor="none")
    axes[1].bar(x+w,   df["avg_tools"].values, w, label="Avg Tools", color=GREEN,  edgecolor="none")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(df["domain"].str.replace(" ", "\n"), color=TEXT, fontsize=8)
    ax_style(axes[1], "Requirement Breakdown by Domain")
    axes[1].set_ylabel("Count"); axes[1].grid(axis="y", color=BORDER, lw=0.5, alpha=0.4)
    axes[1].legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)

    plt.tight_layout(pad=2)
    plt.savefig("reports/domain_comparison.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(); print("  ✓ reports/domain_comparison.png")

# ── 3. Domain Trend Lines (multi-line) ───────────────────────────────────────
def chart_domain_trend():
    path = "data/processed/domain_index.csv"
    if not os.path.exists(path): return
    df = pd.read_csv(path)
    if df["month"].nunique() < 2: return     # need ≥2 months for trend
    fig, ax = sf(10, 5)
    for domain, grp in df.groupby("domain"):
        grp = grp.sort_values("month")
        color = DOMAIN_COLORS.get(domain, MUTED)
        ax.plot(grp["month"], grp["skill_score"], color=color, lw=2,
                marker="o", ms=5, label=domain)
    ax.axhline(y=3.0, color=RED, lw=1, ls="--", alpha=0.35)
    ax_style(ax, "Inflation Trend — All Domains Over Time")
    ax.set_ylabel("Skill Score"); ax.grid(color=BORDER, lw=0.5, alpha=0.4)
    plt.xticks(rotation=30, ha="right")
    ax.legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=9,
              loc="upper left")
    save("reports/domain_trend.png")

# ── 4. Domain Donut — share of jobs ──────────────────────────────────────────
def chart_domain_donut(month):
    path = f"data/processed/{month}.csv"
    if not os.path.exists(path): return
    df = pd.read_csv(path)
    counts = df["domain"].value_counts()
    colors = [DOMAIN_COLORS.get(d, MUTED) for d in counts.index]
    fig, ax = plt.subplots(figsize=(6,6), facecolor=BG)
    wedges, texts, autotexts = ax.pie(
        counts.values, labels=counts.index, autopct="%1.0f%%",
        colors=colors, startangle=90, pctdistance=0.78,
        wedgeprops=dict(width=0.55, edgecolor=BG, linewidth=3))
    for t in texts:     t.set_color(TEXT); t.set_fontsize(10)
    for a in autotexts: a.set_color(BG);   a.set_fontsize(9); a.set_fontweight("bold")
    ax.set_title("Job Distribution by Domain", color=TEXT, fontsize=12, fontweight="bold")
    fig.patch.set_facecolor(BG)
    plt.tight_layout()
    plt.savefig("reports/domain_donut.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(); print("  ✓ reports/domain_donut.png")

# ── 5. Exploitation Rate by Domain ───────────────────────────────────────────
def chart_exploitation_by_domain(month):
    path = "data/processed/domain_index.csv"
    if not os.path.exists(path): return
    df = pd.read_csv(path)
    df = df[df["month"]==month].sort_values("exploitation_rate", ascending=True)
    if df.empty or "exploitation_rate" not in df.columns: return
    fig, ax = sf(8, max(4, len(df)*0.65))
    bar_colors = [RED if v>=50 else YELLOW if v>=25 else GREEN for v in df["exploitation_rate"]]
    bars = ax.barh(df["domain"], df["exploitation_rate"], color=bar_colors, height=0.5, edgecolor="none")
    for bar, val in zip(bars, df["exploitation_rate"]):
        ax.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2,
                f"{val:.0f}%", va="center", color=TEXT, fontsize=9, fontweight="bold")
    ax.axvline(x=50, color=RED, lw=1, ls="--", alpha=0.4)
    ax_style(ax, "Exploitation Rate by Domain")
    ax.set_xlabel("% Jobs Flagged"); ax.tick_params(axis="y", colors=TEXT)
    ax.set_xlim(0, 110)
    legend_els = [mpatches.Patch(color=RED, label="High ≥50%"),
                  mpatches.Patch(color=YELLOW, label="Moderate 25–50%"),
                  mpatches.Patch(color=GREEN, label="Low <25%")]
    ax.legend(handles=legend_els, facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)
    save("reports/exploitation_by_domain.png")

# ── 6. Seniority by Domain ────────────────────────────────────────────────────
def chart_seniority_by_domain(month):
    path = f"data/processed/{month}.csv"
    if not os.path.exists(path): return
    df = pd.read_csv(path)
    if "seniority" not in df.columns or "domain" not in df.columns: return
    pivot = df.groupby(["domain","seniority"]).size().unstack(fill_value=0)
    for col in ["Junior","Mid","Senior"]:
        if col not in pivot.columns: pivot[col] = 0
    pivot = pivot[["Junior","Mid","Senior"]]
    fig, ax = sf(10, max(4, len(pivot)*0.7))
    x = np.arange(len(pivot)); w = 0.25
    ax.bar(x-w, pivot["Junior"], w, label="Junior", color=GREEN,  edgecolor="none")
    ax.bar(x,   pivot["Mid"],    w, label="Mid",    color=YELLOW, edgecolor="none")
    ax.bar(x+w, pivot["Senior"], w, label="Senior", color=RED,    edgecolor="none")
    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index.str.replace(" ", "\n"), color=TEXT, fontsize=9)
    ax_style(ax, "Seniority Distribution by Domain")
    ax.set_ylabel("Job Count"); ax.grid(axis="y", color=BORDER, lw=0.5, alpha=0.4)
    ax.legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    save("reports/seniority_by_domain.png")

# ── 7. Salary vs Score (bubble chart) ────────────────────────────────────────
def chart_salary_bubble(month):
    path = "data/processed/domain_index.csv"
    if not os.path.exists(path): return
    df = pd.read_csv(path)
    df = df[df["month"]==month].dropna(subset=["avg_salary_usd"])
    if df.empty: return
    fig, ax = sf(9, 6)
    for _, row in df.iterrows():
        color = DOMAIN_COLORS.get(row["domain"], MUTED)
        size  = row["job_count"] * 80
        ax.scatter(row["skill_score"], row["avg_salary_usd"]/1000,
                   s=size, color=color, alpha=0.8, edgecolors="none", zorder=3)
        ax.annotate(row["domain"],
                    (row["skill_score"], row["avg_salary_usd"]/1000),
                    textcoords="offset points", xytext=(8, 4),
                    color=TEXT, fontsize=9)
    ax.axvline(x=3.0, color=RED, lw=1, ls="--", alpha=0.4)
    ax_style(ax, "Salary (USD) vs Inflation Score — By Domain\n(bubble size = job count)")
    ax.set_xlabel("Skill Inflation Score"); ax.set_ylabel("Avg Annual Salary (USD thousands)")
    ax.grid(color=BORDER, lw=0.5, alpha=0.4)
    save("reports/salary_vs_score.png")

# ── 8. Cert Demand ────────────────────────────────────────────────────────────
def chart_cert_demand(month):
    files = glob.glob(f"data/raw/{month}/*.txt")
    if not files: return
    text = " ".join(open(f, encoding="utf-8").read().lower() for f in files)
    certs = {
        "CISSP":text.count("cissp"), "CISA":text.count("cisa"),
        "CRISC":text.count("crisc"), "CEH":text.count("ceh"),
        "ISO 27001":text.count("iso 27001"), "Security+":text.count("security+"),
        "OSCP":text.count("oscp"), "CCSP":text.count("ccsp"),
        "CISM":text.count("cism"), "GIAC":text.count("giac"),
    }
    certs = dict(sorted({k:v for k,v in certs.items() if v>0}.items(), key=lambda x:x[1]))
    if not certs: return
    fig, ax = sf(7, max(4, len(certs)*0.6))
    colors = [ACCENT if v==max(certs.values()) else YELLOW if v>=3 else MUTED for v in certs.values()]
    bars = ax.barh(list(certs.keys()), list(certs.values()), color=colors, height=0.55, edgecolor="none")
    for bar, val in zip(bars, certs.values()):
        ax.text(bar.get_width()+0.05, bar.get_y()+bar.get_height()/2,
                str(val), va="center", color=TEXT, fontsize=9, fontweight="bold")
    ax_style(ax, "Certification Demand — Industry-Wide")
    ax.set_xlabel("Mentions"); ax.tick_params(axis="y", colors=TEXT)
    ax.grid(axis="x", color=BORDER, lw=0.5, alpha=0.5)
    save("reports/cert_demand.png")

# ── 9. Tool Demand ────────────────────────────────────────────────────────────
def chart_tool_demand(month):
    files = glob.glob(f"data/raw/{month}/*.txt")
    if not files: return
    text = " ".join(open(f, encoding="utf-8").read().lower() for f in files)
    tools_all = [
        ("ServiceNow",text.count("servicenow")), ("Splunk",text.count("splunk")),
        ("Archer",text.count("archer")),         ("Burp Suite",text.count("burp suite")),
        ("CrowdStrike",text.count("crowdstrike")),("Wiz",text.count(" wiz ")),
        ("OneTrust",text.count("onetrust")),      ("Okta",text.count("okta")),
        ("Metasploit",text.count("metasploit")),  ("Snyk",text.count("snyk")),
        ("Tenable",text.count("tenable")),        ("CyberArk",text.count("cyberark")),
    ]
    tools = dict(sorted([(k,v) for k,v in tools_all if v>0], key=lambda x:-x[1]))
    if not tools: return
    fig, ax = sf(8, max(4, len(tools)*0.55))
    colors = [DOMAIN_COLORS.get("GRC" if i<3 else "SOC" if i<6 else "Penetration Testing", ACCENT)
              for i in range(len(tools))]
    bars = ax.barh(list(tools.keys()), list(tools.values()), color=colors, height=0.55, edgecolor="none")
    for bar, val in zip(bars, tools.values()):
        ax.text(bar.get_width()+0.05, bar.get_y()+bar.get_height()/2,
                str(val), va="center", color=TEXT, fontsize=9, fontweight="bold")
    ax_style(ax, "Tool Demand — Industry-Wide")
    ax.set_xlabel("Mentions"); ax.tick_params(axis="y", colors=TEXT); ax.invert_yaxis()
    ax.grid(axis="x", color=BORDER, lw=0.5, alpha=0.5)
    save("reports/tool_demand.png")

# ── 10. Country Heatmap ───────────────────────────────────────────────────────
def chart_country_comparison():
    path = "data/processed/country_index.csv"
    if not os.path.exists(path): return
    df = pd.read_csv(path)
    latest = df["month"].max()
    df = df[df["month"]==latest].sort_values("skill_score", ascending=True)
    if df.empty: return
    fig, axes = plt.subplots(1, 2, figsize=(12, max(4, len(df)*0.6)), facecolor=BG)
    bar_colors = [RED if s>=3 else YELLOW if s>=2 else GREEN for s in df["skill_score"]]
    axes[0].set_facecolor(SURFACE)
    bars = axes[0].barh(df["country"], df["skill_score"], color=bar_colors, height=0.5, edgecolor="none")
    for bar, val in zip(bars, df["skill_score"]):
        axes[0].text(bar.get_width()+0.04, bar.get_y()+bar.get_height()/2,
                     f"{val:.2f}", va="center", color=TEXT, fontsize=9, fontweight="bold")
    axes[0].axvline(x=3.0, color=RED, lw=1, ls="--", alpha=0.5)
    ax_style(axes[0], "Inflation Score by Country")
    axes[0].set_xlabel("Score"); axes[0].tick_params(axis="y", colors=TEXT)
    axes[1].set_facecolor(SURFACE)
    axes[1].barh(df["country"], df["avg_years"], color=ACCENT, height=0.5, edgecolor="none", alpha=0.8)
    for i, (yr, cnt) in enumerate(zip(df["avg_years"], df["job_count"])):
        axes[1].text(yr+0.05, i, f"{yr:.1f} yrs ({cnt} jobs)", va="center", color=TEXT, fontsize=9)
    ax_style(axes[1], "Avg Experience by Country")
    axes[1].set_xlabel("Years"); axes[1].tick_params(axis="y", colors=TEXT)
    legend_els = [mpatches.Patch(color=RED,label="High ≥3.0"),
                  mpatches.Patch(color=YELLOW,label="Moderate 2–3"),
                  mpatches.Patch(color=GREEN,label="Healthy <2")]
    axes[0].legend(handles=legend_els, facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)
    plt.tight_layout(pad=2)
    plt.savefig("reports/country_comparison.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(); print("  ✓ reports/country_comparison.png")

# ── 11. Anomaly Flags ─────────────────────────────────────────────────────────
def chart_anomalies(month):
    path = f"data/processed/{month}.csv"
    if not os.path.exists(path): return
    df = pd.read_csv(path)
    if "anomaly_flags" not in df.columns: return
    all_flags = ["EXPERIENCE_INFLATION","CERT_OVERLOAD","TOOL_STACK_ABUSE",
                 "UNDERPAID_EXPERIENCED","SENIOR_EXPLOITATION"]
    counts = {f: df["anomaly_flags"].str.contains(f, na=False).sum() for f in all_flags}
    counts = {k.replace("_"," ").title():v for k,v in counts.items() if v>0}
    if not counts: return
    total = len(df)
    fig, ax = sf(8, max(4, len(counts)*0.7))
    bar_colors = [RED if v/total>=0.4 else YELLOW if v/total>=0.2 else ORANGE for v in counts.values()]
    bars = ax.barh(list(counts.keys()), list(counts.values()), color=bar_colors, height=0.5, edgecolor="none")
    for bar, val in zip(bars, counts.values()):
        ax.text(bar.get_width()+0.05, bar.get_y()+bar.get_height()/2,
                f"{val} jobs ({val/total*100:.0f}%)", va="center", color=TEXT, fontsize=9)
    ax_style(ax, f"Exploitation Signal Detector — {month}")
    ax.set_xlabel("Jobs Flagged"); ax.tick_params(axis="y", colors=TEXT)
    ax.set_xlim(0, max(counts.values())*1.55); ax.grid(axis="x", color=BORDER, lw=0.5, alpha=0.5)
    save("reports/anomaly_flags.png")

# ── 12. Salary vs Experience Scatter ─────────────────────────────────────────
def chart_salary_scatter(month):
    path = f"data/processed/{month}.csv"
    if not os.path.exists(path): return
    df = pd.read_csv(path).dropna(subset=["salary_usd"])
    if len(df)<2: return
    fig, ax = sf(9, 5)
    for domain, grp in df.groupby("domain"):
        color = DOMAIN_COLORS.get(domain, MUTED)
        ax.scatter(grp["years_required"], grp["salary_usd"]/1000,
                   color=color, s=70, alpha=0.85, label=domain, zorder=3, edgecolors="none")
    if len(df)>=3:
        z = np.polyfit(df["years_required"], df["salary_usd"]/1000, 1)
        xl = np.linspace(df["years_required"].min(), df["years_required"].max(), 100)
        ax.plot(xl, np.poly1d(z)(xl), color=MUTED, lw=1.5, ls="--", alpha=0.5, label="Trend")
    ax_style(ax, "Salary (USD) vs Experience — Colored by Domain")
    ax.set_xlabel("Years Required"); ax.set_ylabel("Annual Salary (USD thousands)")
    ax.legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=8,
              loc="upper left", ncol=2)
    ax.grid(color=BORDER, lw=0.5, alpha=0.4)
    save("reports/salary_vs_experience.png")

# ── README Updater ────────────────────────────────────────────────────────────
def update_readme(df, month):
    readme = "README.md"
    if not os.path.exists(readme): return
    rows_for_month = df[df["month"]==month]
    if rows_for_month.empty:
        rows_for_month = df[df["month"]==df["month"].max()]
    latest = rows_for_month.iloc[-1]
    with open(readme,"r",encoding="utf-8") as f: content = f.read()

    # ── Badges ────────────────────────────────────────────────────────────────
    def rb(content, label, value, color):
        pat = rf'!\[{re.escape(label)}\]\(https://img\.shields\.io/badge/[^)]*\)'
        v = str(value).replace("-","--").replace(" ","%20")
        l = label.replace("-","--").replace(" ","%20")
        return re.sub(pat, f"![{label}](https://img.shields.io/badge/{l}-{v}-{color}?style=flat)", content)

    content = rb(content, "Skill Score",      f"{latest['skill_score']:.2f}", "red")
    content = rb(content, "Avg Years",        f"{latest['avg_years']:.1f}",   "blue")
    content = rb(content, "Avg Certs",        f"{latest['avg_certs']:.1f}",   "green")
    content = rb(content, "Avg Tools",        f"{latest['avg_tools']:.1f}",   "yellow")
    content = rb(content, "Jobs Analyzed",    int(df["job_count"].sum()),      "brightgreen")
    content = rb(content, "Last Updated",     month,                           "blue")
    if pd.notna(latest.get("exploitation_rate")):
        content = rb(content, "Exploitation Rate", f"{latest['exploitation_rate']:.0f}%25", "orange")

    # ── Industry Signal section ───────────────────────────────────────────────
    score     = float(latest["skill_score"])
    sig_emoji = "🔴 **HIGH INFLATION**" if score > 3.0 else "🟡 **MODERATE INFLATION**" if score > 2.0 else "🟢 **HEALTHY**"
    exploit   = float(latest.get("exploitation_rate", 0))
    sal       = latest.get("avg_salary_usd", 0)
    sal_str   = f"~${float(sal):,.0f}" if pd.notna(sal) and sal else "N/A"
    jobs_total= int(df["job_count"].sum())

    signal_block = f"""## ⚠️ Industry Signal — {pd.to_datetime(month+'-01').strftime('%B %Y')}

> {sig_emoji} — Global score **{score:.2f}**, {'above' if score > 3.0 else 'below'} the 3.0 threshold. **{exploit:.0f}% of all listings** flagged for requirement signals.

| Metric | Value | Signal |
|--------|-------|--------|
| 📈 Global Skill Inflation Score | **{score:.2f}** | {'🔴 High — above threshold' if score > 3.0 else '🟡 Moderate'} |
| 📅 Avg Years Required | **{float(latest['avg_years']):.1f} yrs** | 🔴 Rising across all domains |
| 🧠 Avg Certifications Demanded | **{float(latest['avg_certs']):.1f}** | 🟡 Cert creep industry-wide |
| 🛠️ Avg Tools Required | **{float(latest['avg_tools']):.1f}** | 🔴 High tool complexity |
| ⚠️ Requirement Signal Rate | **{exploit:.0f}%** | {'🔴 Majority of listings flagged' if exploit > 50 else '🟡 Nearly half of listings flagged'} |
| 💰 Avg Salary (USD) | **{sal_str}** | 🟡 Varies significantly by market |
| 💼 Total Jobs Analyzed | **{jobs_total}** | ✅ 6 domains · 6 countries |"""

    content = re.sub(
        r'## ⚠️ Industry Signal.*?(?=\n---\n)',
        signal_block,
        content, flags=re.DOTALL
    )

    # ── Domain Intelligence table ─────────────────────────────────────────────
    dpath = "data/processed/domain_index.csv"
    if os.path.exists(dpath):
        ddf = pd.read_csv(dpath)
        dm  = ddf[ddf["month"]==month]
        if dm.empty:
            dm = ddf[ddf["month"]==ddf["month"].max()]
        dm = dm.sort_values("skill_score", ascending=False)

        # ── Dynamic insight generator from actual job data ────────────────────
        def derive_insight(row, job_df):
            domain   = row["domain"]
            score    = float(row["skill_score"])
            years    = float(row["avg_years"])
            certs    = float(row["avg_certs"])
            tools    = float(row["avg_tools"])
            exploit  = float(row.get("exploitation_rate", 0))
            sal      = float(row["avg_salary_usd"]) if pd.notna(row.get("avg_salary_usd")) else 0
            jobs_d   = job_df[job_df["domain"] == domain] if job_df is not None else pd.DataFrame()

            parts = []

            # ── Salary vs requirement pressure ────────────────────────────────
            if sal > 0 and years >= 4:
                # Only flag as underpaid if salary is genuinely low for the years demanded
                # Use $50K USD as the "reasonable minimum" for 4+ years of specialized cyber work
                threshold = 45000 + (years * 5000)   # scales with experience demanded
                if sal < threshold * 0.55:
                    parts.append(f"${sal:,.0f} avg salary for {years:.0f}+ yrs demanded — pay gap critical")
                elif sal < threshold * 0.80:
                    parts.append(f"${sal:,.0f} avg salary vs {years:.0f}+ yrs required — below market")

            # ── Exploitation rate ─────────────────────────────────────────────
            if exploit == 100:
                parts.append("every listing flagged for requirement signals")
            elif exploit >= 75:
                parts.append(f"{exploit:.0f}% of listings flagged")

            # ── Cert stacking ─────────────────────────────────────────────────
            if certs >= 5:
                parts.append(f"{certs:.1f} certs demanded on average — extreme stacking")
            elif certs >= 4:
                parts.append(f"{certs:.1f} avg certs per role — above market norm")

            # ── Tool overload ─────────────────────────────────────────────────
            if tools >= 5:
                parts.append(f"{tools:.1f} tools required simultaneously")
            elif tools >= 4:
                parts.append(f"{tools:.1f} avg tools per listing")

            # ── Seniority exploitation ────────────────────────────────────────
            if not jobs_d.empty and "seniority" in jobs_d.columns:
                senior_pct = (jobs_d["seniority"] == "Senior").mean() * 100
                if senior_pct >= 50 and years >= 6:
                    parts.append(f"{years:.0f}+ yrs avg for {senior_pct:.0f}% senior roles")

            # ── Specific worst offender ───────────────────────────────────────
            if not jobs_d.empty:
                flagged = jobs_d[jobs_d["anomaly_flags"] != "CLEAN"]
                if not flagged.empty:
                    worst = flagged.sort_values(
                        ["cert_count", "tool_count"], ascending=False
                    ).iloc[0]
                    flags = worst["anomaly_flags"]
                    if "CERT_OVERLOAD" in flags and "TOOL_STACK_ABUSE" in flags:
                        parts.append(
                            f"{worst['company'].split()[0]} demands "
                            f"{int(worst['cert_count'])} certs + {int(worst['tool_count'])} tools"
                        )
                    elif "UNDERPAID_EXPERIENCED" in flags and pd.notna(worst.get("salary_usd")) and worst["salary_usd"] > 0:
                        parts.append(
                            f"{worst['company'].split()[0]} pays "
                            f"${worst['salary_usd']:,.0f} for {int(worst['years_required'])}+ yrs"
                        )

            # ── Fallback if no signals found ──────────────────────────────────
            if not parts:
                if score >= 4.0:
                    parts.append(f"score {score:.2f} — highest requirement pressure")
                elif score >= 3.0:
                    parts.append(f"{years:.0f} yrs + {certs:.1f} certs now baseline expectation")
                else:
                    parts.append(f"most balanced domain — {years:.0f} yrs avg, {certs:.1f} certs")

            return "; ".join(parts[:2])   # cap at 2 signals to keep table readable

        # ── Load per-job data for insight derivation ──────────────────────────
        job_csv = f"data/processed/{month}.csv"
        if not os.path.exists(job_csv):
            job_csv_path = f"data/processed/{ddf['month'].max()}.csv"
        else:
            job_csv_path = job_csv
        per_job_df = pd.read_csv(job_csv_path) if os.path.exists(job_csv_path) else None

        domain_rows = ""
        for _, r in dm.iterrows():
            icon    = "🔴" if r["skill_score"] >= 3.0 else "🟡" if r["skill_score"] >= 2.0 else "🟢"
            insight = derive_insight(r, per_job_df)
            domain_rows += (
                f"| {r['domain']} | {r['avg_years']:.1f} | {r['avg_certs']:.1f} | "
                f"{icon} **{r['skill_score']:.2f}** | {insight} | {int(r['job_count'])} |\n"
            )

        domain_table = (
            "| Domain | Avg Years | Avg Certs | Score | Signal | Jobs |\n"
            "|--------|-----------|-----------|-------|--------|------|\n"
            + domain_rows
        )
        content = re.sub(
            r'\| Domain \| Avg Years \| Avg Certs \| Score \| Signal \| Jobs \|.*?(?=\n---\n|\n\n---)',
            domain_table.rstrip(),
            content, flags=re.DOTALL
        )

    # ── Historical index table ────────────────────────────────────────────────
    hist_rows = "".join(
        f"| {r['month']} | {r['avg_years']:.2f} | {r['avg_certs']:.2f} | "
        f"{r['avg_tools']:.2f} | **{r['skill_score']:.2f}** | {int(r.get('job_count',0))} |\n"
        for _, r in df.iterrows()
    )
    hist_block = (
        "| Month | Avg Years | Avg Certs | Avg Tools | Skill Score | Jobs |\n"
        "|-------|-----------|-----------|-----------|-------------|------|\n"
        + hist_rows
    )
    content = re.sub(
        r'\| Month \| Avg Years.*?(?=\n##|\Z)',
        hist_block.rstrip(), content, flags=re.DOTALL
    )

    with open(readme,"w",encoding="utf-8") as f: f.write(content)
    print("  ✓ README.md updated")

# ── Monthly Report ────────────────────────────────────────────────────────────
def write_report(gdf, ddf, month):
    rows_for_month = gdf[gdf["month"]==month]
    if rows_for_month.empty:
        rows_for_month = gdf[gdf["month"]==gdf["month"].max()]
    latest = rows_for_month.iloc[-1]
    score  = float(latest["skill_score"])
    sig    = ("🔴 **HIGH INFLATION**" if score>3.0 else
              "🟡 **MODERATE INFLATION**" if score>2.0 else "🟢 **HEALTHY**")

    domain_table = ""
    if ddf is not None and not ddf.empty:
        dm = ddf[ddf["month"]==month].sort_values("skill_score", ascending=False)
        for _, r in dm.iterrows():
            icon = "🔴" if r["skill_score"]>=3 else "🟡" if r["skill_score"]>=2 else "🟢"
            domain_table += f"| {r['domain']} | {r['avg_years']:.1f} | {r['avg_certs']:.1f} | {r['skill_score']:.2f} | {icon} | {int(r['job_count'])} |\n"

    report = f"""# CSII Monthly Report — {month}

## Signal: {sig}

## Global Metrics
| Metric | Value |
|--------|-------|
| Avg Years Required | {latest['avg_years']:.2f} |
| Avg Certifications | {latest['avg_certs']:.2f} |
| Avg Tools | {latest['avg_tools']:.2f} |
| **Skill Inflation Score** | **{score:.2f}** |
| Avg Salary (USD) | ${latest.get('avg_salary_usd', 'N/A'):,} |
| Exploitation Rate | {latest.get('exploitation_rate','N/A')}% |
| Jobs Analyzed | {int(latest['job_count'])} |

## Domain Breakdown
| Domain | Avg Years | Avg Certs | Score | Signal | Jobs |
|--------|-----------|-----------|-------|--------|------|
{domain_table}
## Charts
![Global Trend](skill_trend.png) ![Domains](domain_comparison.png)
![Domain Donut](domain_donut.png) ![Exploitation](exploitation_by_domain.png)
![Seniority](seniority_by_domain.png) ![Country](country_comparison.png)
![Certs](cert_demand.png) ![Tools](tool_demand.png)
![Anomalies](anomaly_flags.png) ![Salary](salary_vs_experience.png)
"""
    with open("reports/Monthly-CSII-Report.md","w",encoding="utf-8") as f: f.write(report)
    print("  ✓ reports/Monthly-CSII-Report.md")

# ── Main ──────────────────────────────────────────────────────────────────────
def generate():
    gpath = "data/processed/monthly_index.csv"
    dpath = "data/processed/domain_index.csv"
    if not os.path.exists(gpath):
        print("No monthly_index.csv. Run calculate_index.py first."); return

    gdf   = pd.read_csv(gpath)
    ddf   = pd.read_csv(dpath) if os.path.exists(dpath) else None

    current_month = pd.Timestamp.now().strftime("%Y-%m")
    # Fall back to latest available month if current month has no data yet
    if current_month in gdf["month"].values:
        month = current_month
    else:
        month = gdf["month"].max()
        print(f"  ℹ  No data for {current_month} yet — using latest available month: {month}")

    os.makedirs("reports", exist_ok=True)
    print("Generating charts...")

    chart_global_trend(gdf)
    chart_domain_comparison(month)
    chart_domain_trend()
    chart_domain_donut(month)
    chart_exploitation_by_domain(month)
    chart_seniority_by_domain(month)
    chart_salary_bubble(month)
    chart_cert_demand(month)
    chart_tool_demand(month)
    chart_country_comparison()
    chart_anomalies(month)
    chart_salary_scatter(month)
    update_readme(gdf, month)
    write_report(gdf, ddf, month)
    print("✓ All done.")

if __name__ == "__main__":
    generate()
