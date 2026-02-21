import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
import os, re, glob

# ── Theme ─────────────────────────────────────────────────────────────────────
BG      = "#080c10"
SURFACE = "#0d1318"
BORDER  = "#1e2d3a"
ACCENT  = "#00e5ff"
RED     = "#ff4560"
GREEN   = "#00e676"
YELLOW  = "#ffab00"
PURPLE  = "#c084fc"
ORANGE  = "#fb923c"
TEXT    = "#e8f0f7"
MUTED   = "#4a6378"
COLORS  = [ACCENT, RED, YELLOW, GREEN, PURPLE, ORANGE, "#f472b6", "#34d399"]

def styled_fig(w=10, h=4):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=BG)
    ax.set_facecolor(SURFACE)
    return fig, ax

def apply_style(ax, title=""):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(BORDER)
    ax.spines["bottom"].set_color(BORDER)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    if title:
        ax.set_title(title, color=TEXT, fontsize=11, fontweight="bold", pad=12)

def save(path):
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"  ✓ {path}")

# ── 1. Skill Inflation Trend ──────────────────────────────────────────────────
def chart_trend(df):
    fig, ax = styled_fig(10, 4)
    ax.plot(df["month"], df["skill_score"], color=ACCENT,  lw=2.5, marker="o", ms=6, label="Skill Score", zorder=3)
    ax.plot(df["month"], df["avg_years"],   color=RED,     lw=2,   marker="s", ms=5, ls="--", label="Avg Years", zorder=3)
    ax.plot(df["month"], df["avg_certs"],   color=YELLOW,  lw=2,   marker="^", ms=5, ls=":",  label="Avg Certs", zorder=3)
    ax.fill_between(df["month"], df["skill_score"], alpha=0.07, color=ACCENT)
    ax.axhline(y=3.0, color=RED, lw=1, ls="--", alpha=0.4)
    ax.text(df["month"].iloc[-1], 3.05, "Inflation Threshold", color=RED, fontsize=8, alpha=0.7, ha="right")
    apply_style(ax, "Skill Inflation Score — Monthly Trend")
    ax.set_ylabel("Score / Count")
    plt.xticks(rotation=30, ha="right")
    ax.legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)
    ax.grid(axis="y", color=BORDER, lw=0.5, alpha=0.5)
    save("reports/skill_trend.png")

# ── 2. Certification Demand ───────────────────────────────────────────────────
def chart_cert_demand(month):
    files = glob.glob(f"data/raw/{month}/*.txt")
    if not files: return
    text  = " ".join(open(f, encoding="utf-8").read().lower() for f in files)
    certs = {
        "CISSP":       text.count("cissp"),
        "CISA":        text.count("cisa"),
        "CRISC":       text.count("crisc"),
        "CEH":         text.count("ceh"),
        "ISO 27001":   text.count("iso 27001"),
        "Security+":   text.count("security+"),
        "CISM":        text.count("cism"),
        "CCSP":        text.count("ccsp"),
    }
    certs = dict(sorted({k:v for k,v in certs.items() if v>0}.items(), key=lambda x: x[1]))
    if not certs: return
    fig, ax = styled_fig(7, max(4, len(certs)*0.65))
    bars = ax.barh(list(certs.keys()), list(certs.values()),
                   color=[COLORS[i % len(COLORS)] for i in range(len(certs))],
                   height=0.55, edgecolor="none")
    for bar, val in zip(bars, certs.values()):
        ax.text(bar.get_width()+0.05, bar.get_y()+bar.get_height()/2,
                str(val), va="center", color=TEXT, fontsize=9, fontweight="bold")
    apply_style(ax, "Certification Demand — Frequency in Job Descriptions")
    ax.set_xlabel("Mentions")
    ax.tick_params(axis="y", colors=TEXT)
    ax.grid(axis="x", color=BORDER, lw=0.5, alpha=0.5)
    save("reports/cert_demand.png")

# ── 3. Tool Demand Pie ────────────────────────────────────────────────────────
def chart_tool_demand(month):
    files = glob.glob(f"data/raw/{month}/*.txt")
    if not files: return
    text = " ".join(open(f, encoding="utf-8").read().lower() for f in files)
    tools = {
        "ServiceNow": text.count("servicenow"),
        "Archer":     text.count("archer"),
        "OneTrust":   text.count("onetrust"),
        "Splunk":     text.count("splunk"),
        "Qualys":     text.count("qualys"),
        "Tenable":    text.count("tenable"),
        "Rapid7":     text.count("rapid7"),
    }
    tools = dict(sorted({k:v for k,v in tools.items() if v>0}.items(), key=lambda x: -x[1]))
    if not tools: return
    fig, ax = styled_fig(7, 5)
    wedges, texts, autotexts = ax.pie(
        tools.values(), labels=tools.keys(), autopct="%1.0f%%",
        colors=COLORS[:len(tools)], startangle=140,
        wedgeprops=dict(edgecolor=BG, linewidth=2))
    for t in texts:     t.set_color(TEXT);  t.set_fontsize(10)
    for a in autotexts: a.set_color(BG);    a.set_fontsize(9);  a.set_fontweight("bold")
    ax.set_title("Tool Stack Demand", color=TEXT, fontsize=11, fontweight="bold")
    fig.patch.set_facecolor(BG)
    save("reports/tool_demand.png")

# ── 4. Experience Distribution ────────────────────────────────────────────────
def chart_experience(month):
    path = f"data/processed/{month}.csv"
    if not os.path.exists(path): return
    df = pd.read_csv(path)
    buckets = {"0 yrs\n(Entry)":0, "1–2 yrs":0, "3–5 yrs":0, "6–8 yrs":0, "9+ yrs":0}
    for y in df["years_required"]:
        if   y == 0:  buckets["0 yrs\n(Entry)"] += 1
        elif y <= 2:  buckets["1–2 yrs"]  += 1
        elif y <= 5:  buckets["3–5 yrs"]  += 1
        elif y <= 8:  buckets["6–8 yrs"]  += 1
        else:         buckets["9+ yrs"]   += 1
    buckets = {k:v for k,v in buckets.items() if v>0}
    fig, ax = styled_fig(7, 4)
    bar_colors = [GREEN, ACCENT, YELLOW, RED, PURPLE]
    bars = ax.bar(buckets.keys(), buckets.values(),
                  color=bar_colors[:len(buckets)], width=0.5, edgecolor="none")
    for bar, val in zip(bars, buckets.values()):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.05,
                str(val), ha="center", color=TEXT, fontsize=11, fontweight="bold")
    apply_style(ax, "Experience Required — Distribution")
    ax.set_ylabel("Job Count")
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.grid(axis="y", color=BORDER, lw=0.5, alpha=0.5)
    save("reports/experience_distribution.png")

# ── 5. NEW: Seniority vs Inflation ───────────────────────────────────────────
def chart_seniority_inflation(month):
    path = f"data/processed/{month}.csv"
    if not os.path.exists(path): return
    df = pd.read_csv(path)
    if "seniority" not in df.columns: return
    order = ["Junior", "Mid", "Senior"]
    data  = {s: df[df["seniority"]==s] for s in order if s in df["seniority"].values}
    if not data: return

    labels  = list(data.keys())
    years   = [data[s]["years_required"].mean() for s in labels]
    certs   = [data[s]["cert_count"].mean()     for s in labels]
    tools   = [data[s]["tool_count"].mean()      for s in labels]
    scores  = [(y*0.4 + c*0.3 + t*0.3) for y,c,t in zip(years, certs, tools)]

    x   = np.arange(len(labels))
    w   = 0.22
    fig, ax = styled_fig(8, 5)
    ax.bar(x - w,   years,  w, label="Avg Years",  color=ACCENT,  edgecolor="none")
    ax.bar(x,       certs,  w, label="Avg Certs",  color=YELLOW,  edgecolor="none")
    ax.bar(x + w,   tools,  w, label="Avg Tools",  color=GREEN,   edgecolor="none")
    ax.plot(x, scores, color=RED, lw=2.5, marker="D", ms=8, label="Skill Score", zorder=5)
    for i, (xi, sc) in enumerate(zip(x, scores)):
        ax.text(xi, sc+0.1, f"{sc:.2f}", ha="center", color=RED, fontsize=9, fontweight="bold")
    apply_style(ax, "Inflation by Seniority Level")
    ax.set_xticks(x); ax.set_xticklabels(labels, color=TEXT, fontsize=11)
    ax.set_ylabel("Score / Count")
    ax.legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)
    ax.grid(axis="y", color=BORDER, lw=0.5, alpha=0.5)
    save("reports/seniority_inflation.png")

# ── 6. NEW: Country Comparison ────────────────────────────────────────────────
def chart_country_comparison():
    path = "data/processed/country_index.csv"
    if not os.path.exists(path): return
    df = pd.read_csv(path)
    latest_month = df["month"].max()
    df = df[df["month"] == latest_month].sort_values("skill_score", ascending=True)
    if df.empty: return

    fig, axes = plt.subplots(1, 2, figsize=(12, max(4, len(df)*0.6)), facecolor=BG)
    bar_colors = [RED if s >= 3.0 else YELLOW if s >= 2.0 else GREEN for s in df["skill_score"]]

    # Left: Skill Score
    axes[0].set_facecolor(SURFACE)
    bars = axes[0].barh(df["country"], df["skill_score"], color=bar_colors, height=0.5, edgecolor="none")
    for bar, val in zip(bars, df["skill_score"]):
        axes[0].text(bar.get_width()+0.05, bar.get_y()+bar.get_height()/2,
                     f"{val:.2f}", va="center", color=TEXT, fontsize=9, fontweight="bold")
    axes[0].axvline(x=3.0, color=RED, lw=1, ls="--", alpha=0.5)
    apply_style(axes[0], "Skill Inflation Score by Country")
    axes[0].set_xlabel("Score")
    axes[0].tick_params(axis="y", colors=TEXT)

    # Right: Avg Years Required
    axes[1].set_facecolor(SURFACE)
    axes[1].barh(df["country"], df["avg_years"], color=ACCENT, height=0.5, edgecolor="none", alpha=0.8)
    for i, (val, cnt) in enumerate(zip(df["avg_years"], df["job_count"])):
        axes[1].text(val+0.05, i, f"{val:.1f} yrs  ({cnt} jobs)", va="center", color=TEXT, fontsize=9)
    apply_style(axes[1], "Avg Experience Required by Country")
    axes[1].set_xlabel("Years")
    axes[1].tick_params(axis="y", colors=TEXT)

    # Legend
    legend_elements = [
        mpatches.Patch(color=RED,    label="High ≥ 3.0"),
        mpatches.Patch(color=YELLOW, label="Moderate 2.0–3.0"),
        mpatches.Patch(color=GREEN,  label="Healthy < 2.0"),
    ]
    axes[0].legend(handles=legend_elements, facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)
    plt.tight_layout(pad=2)
    plt.savefig("reports/country_comparison.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print("  ✓ reports/country_comparison.png")

# ── 7. NEW: Anomaly / Exploitation Heatmap ────────────────────────────────────
def chart_anomalies(month):
    path = f"data/processed/{month}.csv"
    if not os.path.exists(path): return
    df = pd.read_csv(path)
    if "anomaly_flags" not in df.columns: return

    all_flags = ["EXPERIENCE_INFLATION", "CERT_OVERLOAD", "TOOL_STACK_ABUSE",
                 "UNDERPAID_EXPERIENCED", "SENIOR_EXPLOITATION"]
    counts = {f: df["anomaly_flags"].str.contains(f, na=False).sum() for f in all_flags}
    counts = {k:v for k,v in counts.items() if v > 0}
    if not counts: return

    labels  = [k.replace("_", " ").title() for k in counts.keys()]
    values  = list(counts.values())
    total   = len(df)

    fig, ax = styled_fig(8, 4)
    bar_colors = [RED if v/total > 0.4 else YELLOW if v/total > 0.2 else ORANGE for v in values]
    bars = ax.barh(labels, values, color=bar_colors, height=0.5, edgecolor="none")
    for bar, val in zip(bars, values):
        pct = val/total*100
        ax.text(bar.get_width()+0.05, bar.get_y()+bar.get_height()/2,
                f"{val} jobs ({pct:.0f}%)", va="center", color=TEXT, fontsize=9)
    apply_style(ax, f"Exploitation Signal Detector — {month}")
    ax.set_xlabel("Jobs Flagged")
    ax.tick_params(axis="y", colors=TEXT)
    ax.set_xlim(0, max(values) * 1.5)
    ax.grid(axis="x", color=BORDER, lw=0.5, alpha=0.5)
    save("reports/anomaly_flags.png")

# ── 8. NEW: Salary vs Experience Scatter ─────────────────────────────────────
def chart_salary_scatter(month):
    path = f"data/processed/{month}.csv"
    if not os.path.exists(path): return
    df = pd.read_csv(path)
    df = df[df["salary_usd"].notna()].copy()
    if len(df) < 2: return

    seniority_colors = {"Junior": GREEN, "Mid": YELLOW, "Senior": RED}
    fig, ax = styled_fig(8, 5)
    for seniority, grp in df.groupby("seniority"):
        color = seniority_colors.get(seniority, ACCENT)
        ax.scatter(grp["years_required"], grp["salary_usd"]/1000,
                   color=color, s=80, alpha=0.85, label=seniority, zorder=3, edgecolors="none")
        for _, row in grp.iterrows():
            ax.annotate(row["company"][:12], (row["years_required"], row["salary_usd"]/1000),
                        textcoords="offset points", xytext=(6, 4),
                        fontsize=7.5, color=MUTED)

    # Trend line
    if len(df) >= 3:
        z = np.polyfit(df["years_required"], df["salary_usd"]/1000, 1)
        p = np.poly1d(z)
        xline = np.linspace(df["years_required"].min(), df["years_required"].max(), 100)
        ax.plot(xline, p(xline), color=MUTED, lw=1.5, ls="--", alpha=0.5, label="Trend")

    apply_style(ax, "Salary (USD) vs Experience Required")
    ax.set_xlabel("Years Required")
    ax.set_ylabel("Annual Salary (USD thousands)")
    ax.legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)
    ax.grid(color=BORDER, lw=0.5, alpha=0.4)
    save("reports/salary_vs_experience.png")

# ── README Auto-Updater ───────────────────────────────────────────────────────
def update_readme(df, month):
    readme_path = "README.md"
    if not os.path.exists(readme_path): return

    latest = df[df["month"] == month].iloc[-1]

    def replace_badge(content, label, value, color):
        pattern = rf'!\[{re.escape(label)}\]\(https://img\.shields\.io/badge/[^)]*\)'
        val_enc = str(value).replace("-","--").replace(" ","%20")
        lbl_enc = label.replace("-","--").replace(" ","%20")
        new_badge = f"![{label}](https://img.shields.io/badge/{lbl_enc}-{val_enc}-{color}?style=flat)"
        return re.sub(pattern, new_badge, content)

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = replace_badge(content, "Skill Score",   f"{latest['skill_score']:.2f}",            "red")
    content = replace_badge(content, "Avg Years",     f"{latest['avg_years']:.1f}",               "blue")
    content = replace_badge(content, "Avg Certs",     f"{latest['avg_certs']:.1f}",               "green")
    content = replace_badge(content, "Avg Tools",     f"{latest['avg_tools']:.1f}",               "yellow")
    content = replace_badge(content, "Jobs Analyzed", int(df["job_count"].sum()),                  "brightgreen")
    content = replace_badge(content, "Last Updated",  month,                                       "blue")
    if "exploitation_rate" in latest:
        expl = f"{latest['exploitation_rate']:.0f}%25"
        content = replace_badge(content, "Exploitation Rate", f"{latest['exploitation_rate']:.0f}%25", "orange")

    # History table
    rows = ""
    for _, row in df.iterrows():
        rows += (f"| {row['month']} | {row['avg_years']:.2f} | {row['avg_certs']:.2f} | "
                 f"{row['avg_tools']:.2f} | **{row['skill_score']:.2f}** | "
                 f"{int(row.get('job_count',0))} |\n")

    history_block = (
        "| Month | Avg Years | Avg Certs | Avg Tools | Skill Score | Jobs |\n"
        "|-------|-----------|-----------|-----------|-------------|------|\n"
        + rows
    )
    content = re.sub(
        r'\| Month \| Avg Years.*?(?=\n##|\Z)',
        history_block.rstrip(), content, flags=re.DOTALL
    )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  ✓ README.md badges + history table updated")

# ── Monthly Report Markdown ───────────────────────────────────────────────────
def write_report(df, month):
    latest = df[df["month"] == month].iloc[-1]
    score  = float(latest["skill_score"])
    signal = ("🔴 **HIGH INFLATION** — Requirements significantly outpacing market value."
               if score > 3.0 else
               "🟡 **MODERATE INFLATION** — Monitor closely."
               if score > 2.0 else
               "🟢 **HEALTHY MARKET** — Requirements proportional.")

    expl_rate = latest.get("exploitation_rate", "N/A")
    sal_usd   = latest.get("avg_salary_usd", None)
    sal_str   = f"${sal_usd:,.0f}" if sal_usd else "N/A"

    report = f"""# CSII Monthly Report — {month}

## Signal
{signal}

## Key Metrics
| Metric | Value |
|--------|-------|
| Avg Years Required | {latest['avg_years']:.2f} |
| Avg Certifications | {latest['avg_certs']:.2f} |
| Avg Tools | {latest['avg_tools']:.2f} |
| Avg Frameworks | {latest['avg_frameworks']:.2f} |
| **Skill Inflation Score** | **{score:.2f}** |
| Jobs Analyzed | {int(latest['job_count'])} |
| Avg Salary (USD) | {sal_str} |
| Exploitation Rate | {expl_rate}% |
| Junior / Mid / Senior | {int(latest.get('junior_count',0))} / {int(latest.get('mid_count',0))} / {int(latest.get('senior_count',0))} |

## Charts
![Trend](skill_trend.png)
![Certs](cert_demand.png)
![Tools](tool_demand.png)
![Experience](experience_distribution.png)
![Seniority](seniority_inflation.png)
![Country](country_comparison.png)
![Anomalies](anomaly_flags.png)
![Salary](salary_vs_experience.png)
"""
    with open("reports/Monthly-CSII-Report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("  ✓ reports/Monthly-CSII-Report.md")

# ── Main ──────────────────────────────────────────────────────────────────────
def generate():
    idx_path = "data/processed/monthly_index.csv"
    if not os.path.exists(idx_path):
        print("No monthly_index.csv. Run calculate_index.py first.")
        return

    df    = pd.read_csv(idx_path)
    month = pd.Timestamp.now().strftime("%Y-%m")
    os.makedirs("reports", exist_ok=True)

    print("Generating charts...")
    chart_trend(df)
    chart_cert_demand(month)
    chart_tool_demand(month)
    chart_experience(month)
    chart_seniority_inflation(month)
    chart_country_comparison()
    chart_anomalies(month)
    chart_salary_scatter(month)
    update_readme(df, month)
    write_report(df, month)
    print("✓ All done.")

if __name__ == "__main__":
    generate()
