import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
import os, re, glob

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
    "Network Security":    "#facc15",
    "DFIR":                "#f87171",
    "OT/ICS Security":     "#34d399",
    "Data Privacy":        "#e879f9",
}

def sf(w=10,h=4):
    fig,ax = plt.subplots(figsize=(w,h),facecolor=BG)
    ax.set_facecolor(SURFACE); return fig,ax

def ax_style(ax, title=""):
    for sp in ["top","right"]: ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(BORDER); ax.spines["bottom"].set_color(BORDER)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(MUTED); ax.yaxis.label.set_color(MUTED)
    if title: ax.set_title(title, color=TEXT, fontsize=11, fontweight="bold", pad=12)

def save(path):
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(); print(f"  ✓ {path}")

def load_all_jobs():
    frames = []
    for p in sorted(glob.glob("data/processed/20??-??.csv")):
        try:
            df = pd.read_csv(p)
            df["month"] = os.path.basename(p).replace(".csv","")
            frames.append(df)
        except Exception: pass
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def aggregate_domains(all_df):
    if all_df.empty or "domain" not in all_df.columns: return pd.DataFrame()
    records = []
    for domain, grp in all_df.groupby("domain"):
        sal  = grp["salary_usd"].dropna()
        expl = round(len(grp[grp["anomaly_flags"]!="CLEAN"])/len(grp)*100, 1) if "anomaly_flags" in grp.columns else 0
        records.append({
            "domain": domain, "job_count": len(grp),
            "avg_years":  round(grp["years_required"].mean(), 2),
            "avg_certs":  round(grp["cert_count"].mean(), 2),
            "avg_tools":  round(grp["tool_count"].mean(), 2),
            "skill_score":round(grp["years_required"].mean()*0.4+grp["cert_count"].mean()*0.3+grp["tool_count"].mean()*0.3,4),
            "avg_salary_usd":    round(sal.mean(),0) if not sal.empty else None,
            "exploitation_rate": expl,
        })
    return pd.DataFrame(records).sort_values("skill_score",ascending=False)

def all_raw_text():
    files = sorted(glob.glob("data/raw/20??-??/*.txt"))
    return " ".join(open(f,encoding="utf-8",errors="ignore").read().lower() for f in files)

# 1. Global Trend
def chart_global_trend(df):
    fig, ax = sf(10,4)
    ax.plot(df["month"], df["skill_score"], color=ACCENT, lw=2.5, marker="o", ms=6, label="Global Score", zorder=3)
    ax.plot(df["month"], df["avg_years"],   color=RED,    lw=2,   marker="s", ms=5, ls="--", label="Avg Years")
    ax.plot(df["month"], df["avg_certs"],   color=YELLOW, lw=2,   marker="^", ms=5, ls=":",  label="Avg Certs")
    ax.fill_between(df["month"], df["skill_score"], alpha=0.07, color=ACCENT)
    ax.axhline(y=3.0, color=RED, lw=1, ls="--", alpha=0.4)
    ax.text(0.01, 0.96, "Inflation Threshold → 3.0", transform=ax.transAxes, color=RED, fontsize=8, alpha=0.7, va="top")
    ax_style(ax, "Cybersecurity Industry — Skill Inflation Trend")
    ax.set_ylabel("Score"); ax.grid(axis="y", color=BORDER, lw=0.5, alpha=0.5)
    plt.xticks(rotation=30, ha="right")
    ax.legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)
    save("reports/skill_trend.png")

# 2. Domain Comparison — ALL jobs
def chart_domain_comparison(agg_df):
    if agg_df.empty: return
    df = agg_df.sort_values("skill_score", ascending=True)
    n  = len(df)
    fig, axes = plt.subplots(1,2, figsize=(16, max(5,n*0.8)), facecolor=BG)
    colors = [DOMAIN_COLORS.get(d,MUTED) for d in df["domain"]]

    axes[0].set_facecolor(SURFACE)
    bars = axes[0].barh(df["domain"], df["skill_score"], color=colors, height=0.55, edgecolor="none")
    axes[0].axvline(x=3.0, color=RED, lw=1.5, ls="--", alpha=0.5)
    for bar,val,jobs in zip(bars, df["skill_score"], df["job_count"]):
        axes[0].text(bar.get_width()+0.04, bar.get_y()+bar.get_height()/2,
                     f"{val:.2f}  ({int(jobs)} jobs)", va="center", color=TEXT, fontsize=9, fontweight="bold")
    ax_style(axes[0], f"Skill Inflation Score — All {int(df['job_count'].sum())} Jobs")
    axes[0].set_xlabel("Score"); axes[0].tick_params(axis="y", colors=TEXT, labelsize=10)
    axes[0].set_xlim(0, max(df["skill_score"].max()*1.38, 5))

    x, w = np.arange(n), 0.25
    axes[1].set_facecolor(SURFACE)
    axes[1].bar(x-w, df["avg_years"].values, w, label="Avg Years", color=ACCENT, edgecolor="none")
    axes[1].bar(x,   df["avg_certs"].values, w, label="Avg Certs", color=YELLOW, edgecolor="none")
    axes[1].bar(x+w, df["avg_tools"].values, w, label="Avg Tools", color=GREEN,  edgecolor="none")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([d.replace(" ","\n").replace("/","/\n") for d in df["domain"]], color=TEXT, fontsize=8)
    ax_style(axes[1], "Requirement Breakdown — All Jobs")
    axes[1].set_ylabel("Count"); axes[1].grid(axis="y", color=BORDER, lw=0.5, alpha=0.4)
    axes[1].legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)
    plt.tight_layout(pad=2)
    plt.savefig("reports/domain_comparison.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(); print("  ✓ reports/domain_comparison.png")

# 3. Domain Trend
def chart_domain_trend():
    path = "data/processed/domain_index.csv"
    if not os.path.exists(path): return
    df = pd.read_csv(path)
    if df["month"].nunique() < 2: return
    fig, ax = sf(10,5)
    for domain, grp in df.groupby("domain"):
        grp = grp.sort_values("month")
        ax.plot(grp["month"], grp["skill_score"], color=DOMAIN_COLORS.get(domain,MUTED),
                lw=2, marker="o", ms=5, label=domain)
    ax.axhline(y=3.0, color=RED, lw=1, ls="--", alpha=0.35)
    ax_style(ax, "Inflation Trend — All Domains Over Time")
    ax.set_ylabel("Skill Score"); ax.grid(color=BORDER, lw=0.5, alpha=0.4)
    plt.xticks(rotation=30, ha="right")
    ax.legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=9, loc="upper left", ncol=2)
    save("reports/domain_trend.png")

# 4. Domain Donut — ALL jobs
def chart_domain_donut(all_df):
    if all_df.empty or "domain" not in all_df.columns: return
    counts = all_df["domain"].value_counts()
    colors = [DOMAIN_COLORS.get(d,MUTED) for d in counts.index]
    fig, ax = plt.subplots(figsize=(7,7), facecolor=BG)
    wedges, texts, autotexts = ax.pie(
        counts.values, labels=counts.index, autopct="%1.0f%%",
        colors=colors, startangle=90, pctdistance=0.78,
        wedgeprops=dict(width=0.55, edgecolor=BG, linewidth=3))
    for t in texts:     t.set_color(TEXT); t.set_fontsize(10)
    for a in autotexts: a.set_color(BG);   a.set_fontsize(9); a.set_fontweight("bold")
    ax.set_title(f"Job Distribution — All {len(all_df)} Jobs", color=TEXT, fontsize=12, fontweight="bold")
    fig.patch.set_facecolor(BG)
    plt.tight_layout()
    plt.savefig("reports/domain_donut.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(); print("  ✓ reports/domain_donut.png")

# 5. Exploitation Rate — ALL jobs
def chart_exploitation_by_domain(agg_df):
    if agg_df.empty or "exploitation_rate" not in agg_df.columns: return
    df = agg_df.sort_values("exploitation_rate", ascending=True)
    fig, ax = sf(10, max(4,len(df)*0.72))
    bar_colors = [RED if v>=50 else YELLOW if v>=25 else GREEN for v in df["exploitation_rate"]]
    bars = ax.barh(df["domain"], df["exploitation_rate"], color=bar_colors, height=0.5, edgecolor="none")
    for bar,val,jobs in zip(bars, df["exploitation_rate"], df["job_count"]):
        ax.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2,
                f"{val:.0f}%  ({int(jobs)} jobs)", va="center", color=TEXT, fontsize=9, fontweight="bold")
    ax.axvline(x=50, color=RED, lw=1, ls="--", alpha=0.4)
    ax_style(ax, f"Exploitation Signal Rate — All {int(df['job_count'].sum())} Jobs")
    ax.set_xlabel("% Jobs Flagged"); ax.tick_params(axis="y", colors=TEXT); ax.set_xlim(0,125)
    ax.legend(handles=[mpatches.Patch(color=RED,label="High ≥50%"),
                       mpatches.Patch(color=YELLOW,label="Moderate 25–50%"),
                       mpatches.Patch(color=GREEN,label="Low <25%")],
              facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)
    save("reports/exploitation_by_domain.png")

# 6. Seniority — ALL jobs
def chart_seniority_by_domain(all_df):
    if all_df.empty or "seniority" not in all_df.columns: return
    pivot = all_df.groupby(["domain","seniority"]).size().unstack(fill_value=0)
    for col in ["Junior","Mid","Senior"]:
        if col not in pivot.columns: pivot[col] = 0
    pivot = pivot[["Junior","Mid","Senior"]]
    fig, ax = sf(12, max(4,len(pivot)*0.8))
    x = np.arange(len(pivot)); w = 0.25
    ax.bar(x-w, pivot["Junior"], w, label="Junior", color=GREEN,  edgecolor="none")
    ax.bar(x,   pivot["Mid"],    w, label="Mid",    color=YELLOW, edgecolor="none")
    ax.bar(x+w, pivot["Senior"], w, label="Senior", color=RED,    edgecolor="none")
    ax.set_xticks(x)
    ax.set_xticklabels([d.replace(" ","\n").replace("/","/\n") for d in pivot.index], color=TEXT, fontsize=9)
    ax_style(ax, f"Seniority Distribution — All {len(all_df)} Jobs")
    ax.set_ylabel("Job Count"); ax.grid(axis="y", color=BORDER, lw=0.5, alpha=0.4)
    ax.legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    save("reports/seniority_by_domain.png")

# 7. Salary vs Score — ALL jobs
def chart_salary_bubble(agg_df):
    if agg_df.empty: return
    df = agg_df.dropna(subset=["avg_salary_usd"])
    if df.empty: return
    fig, ax = sf(10,6)
    for _, row in df.iterrows():
        color = DOMAIN_COLORS.get(row["domain"], MUTED)
        ax.scatter(row["skill_score"], row["avg_salary_usd"]/1000,
                   s=row["job_count"]*90, color=color, alpha=0.85, edgecolors="none", zorder=3)
        ax.annotate(f"{row['domain']}\n({int(row['job_count'])} jobs)",
                    (row["skill_score"], row["avg_salary_usd"]/1000),
                    textcoords="offset points", xytext=(8,4), color=TEXT, fontsize=8)
    ax.axvline(x=3.0, color=RED, lw=1, ls="--", alpha=0.4)
    ax_style(ax, "Avg Salary (USD) vs Inflation Score — All Jobs\n(bubble size = total job count)")
    ax.set_xlabel("Skill Inflation Score"); ax.set_ylabel("Avg Annual Salary (USD thousands)")
    ax.grid(color=BORDER, lw=0.5, alpha=0.4)
    save("reports/salary_vs_score.png")

# 8. Cert Demand — ALL jobs
def chart_cert_demand():
    text = all_raw_text()
    if not text: return
    certs = {
        "CISSP":text.count("cissp"), "CISA":text.count("cisa"),
        "CRISC":text.count("crisc"), "CEH":text.count("ceh"),
        "ISO 27001":text.count("iso 27001"), "Security+":text.count("security+"),
        "OSCP":text.count("oscp"), "CCSP":text.count("ccsp"),
        "CISM":text.count("cism"), "GCFA":text.count("gcfa"),
        "GCFE":text.count("gcfe"), "GICSP":text.count("gicsp"),
        "CIPP":text.count("cipp"), "PCNSE":text.count("pcnse"),
        "SC-200":text.count("sc-200"), "GIAC":text.count("giac"),
    }
    certs = dict(sorted({k:v for k,v in certs.items() if v>0}.items(), key=lambda x:x[1]))
    if not certs: return
    fig, ax = sf(8, max(4,len(certs)*0.6))
    max_v = max(certs.values())
    colors = [ACCENT if v==max_v else YELLOW if v>=3 else MUTED for v in certs.values()]
    bars = ax.barh(list(certs.keys()), list(certs.values()), color=colors, height=0.55, edgecolor="none")
    for bar,val in zip(bars, certs.values()):
        ax.text(bar.get_width()+0.05, bar.get_y()+bar.get_height()/2,
                str(val), va="center", color=TEXT, fontsize=9, fontweight="bold")
    ax_style(ax, "Certification Demand — All Jobs")
    ax.set_xlabel("Mentions"); ax.tick_params(axis="y", colors=TEXT)
    ax.grid(axis="x", color=BORDER, lw=0.5, alpha=0.5)
    save("reports/cert_demand.png")

# 9. Tool Demand — ALL jobs
def chart_tool_demand():
    text = all_raw_text()
    if not text: return
    tools_all = [
        ("Splunk",text.count("splunk")),("Burp Suite",text.count("burp suite")),
        ("CrowdStrike",text.count("crowdstrike")),("Sentinel",text.count("sentinel")),
        ("Wiz",text.count(" wiz ")),("Okta",text.count("okta")),
        ("CyberArk",text.count("cyberark")),("Metasploit",text.count("metasploit")),
        ("Snyk",text.count("snyk")),("Palo Alto",text.count("palo alto")),
        ("Dragos",text.count("dragos")),("Claroty",text.count("claroty")),
        ("Varonis",text.count("varonis")),("Volatility",text.count("volatility")),
        ("ServiceNow",text.count("servicenow")),("BloodHound",text.count("bloodhound")),
    ]
    tools = dict(sorted([(k,v) for k,v in tools_all if v>0], key=lambda x:-x[1]))
    if not tools: return
    fig, ax = sf(9, max(4,len(tools)*0.58))
    COLOR_MAP = {
        "Splunk":"#ff4560","CrowdStrike":"#ff4560","Sentinel":"#ff4560",
        "Burp Suite":"#fb923c","Metasploit":"#fb923c","BloodHound":"#fb923c",
        "Wiz":"#2dd4bf","Snyk":"#2dd4bf",
        "Okta":"#00e676","CyberArk":"#00e676",
        "Palo Alto":"#facc15","Dragos":"#34d399","Claroty":"#34d399",
        "Varonis":"#e879f9","Volatility":"#f87171","ServiceNow":"#00e5ff",
    }
    bar_colors = [COLOR_MAP.get(k, MUTED) for k in tools.keys()]
    bars = ax.barh(list(tools.keys()), list(tools.values()), color=bar_colors, height=0.55, edgecolor="none")
    for bar,val in zip(bars, tools.values()):
        ax.text(bar.get_width()+0.05, bar.get_y()+bar.get_height()/2,
                str(val), va="center", color=TEXT, fontsize=9, fontweight="bold")
    ax_style(ax, "Tool Demand — All Jobs"); ax.set_xlabel("Mentions")
    ax.tick_params(axis="y", colors=TEXT); ax.invert_yaxis()
    ax.grid(axis="x", color=BORDER, lw=0.5, alpha=0.5)
    save("reports/tool_demand.png")

# 10. Country Comparison — ALL months aggregated
def chart_country_comparison():
    path = "data/processed/country_index.csv"
    if not os.path.exists(path): return
    df = pd.read_csv(path)
    agg = df.groupby("country").apply(lambda g: pd.Series({
        "job_count":   g["job_count"].sum(),
        "avg_years":   (g["avg_years"]  *g["job_count"]).sum()/g["job_count"].sum(),
        "skill_score": (g["skill_score"]*g["job_count"]).sum()/g["job_count"].sum(),
        "avg_sal_usd": g["avg_sal_usd"].mean(),
    })).reset_index().sort_values("skill_score", ascending=True)

    fig, axes = plt.subplots(1,2, figsize=(14, max(4,len(agg)*0.65)), facecolor=BG)
    bar_colors = [RED if s>=3 else YELLOW if s>=2 else GREEN for s in agg["skill_score"]]
    axes[0].set_facecolor(SURFACE)
    bars = axes[0].barh(agg["country"], agg["skill_score"], color=bar_colors, height=0.5, edgecolor="none")
    for bar,val,jobs in zip(bars, agg["skill_score"], agg["job_count"]):
        axes[0].text(bar.get_width()+0.04, bar.get_y()+bar.get_height()/2,
                     f"{val:.2f}  ({int(jobs)} jobs)", va="center", color=TEXT, fontsize=9)
    axes[0].axvline(x=3.0, color=RED, lw=1, ls="--", alpha=0.4)
    ax_style(axes[0], "Inflation Score by Country — All Jobs")
    axes[0].set_xlabel("Score"); axes[0].tick_params(axis="y", colors=TEXT)
    axes[0].set_xlim(0, max(agg["skill_score"].max()*1.3, 4))

    axes[1].set_facecolor(SURFACE)
    sal_df = agg.dropna(subset=["avg_sal_usd"]).sort_values("avg_sal_usd")
    bars2 = axes[1].barh(sal_df["country"], sal_df["avg_sal_usd"]/1000,
                         color=ACCENT, height=0.5, alpha=0.75, edgecolor="none")
    for bar,val in zip(bars2, sal_df["avg_sal_usd"]/1000):
        axes[1].text(bar.get_width()+0.3, bar.get_y()+bar.get_height()/2,
                     f"${val:.0f}k", va="center", color=TEXT, fontsize=9)
    ax_style(axes[1], "Avg Salary (USD) by Country — All Jobs")
    axes[1].set_xlabel("USD thousands"); axes[1].tick_params(axis="y", colors=TEXT)
    axes[1].set_xlim(0, (sal_df["avg_sal_usd"].max()/1000*1.3) if not sal_df.empty else 150)
    plt.tight_layout(pad=2)
    plt.savefig("reports/country_comparison.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(); print("  ✓ reports/country_comparison.png")

# 11. Anomaly Flags — ALL jobs
def chart_anomalies(all_df):
    if all_df.empty or "anomaly_flags" not in all_df.columns: return
    all_flags = ["EXPERIENCE_INFLATION","CERT_OVERLOAD","TOOL_STACK_ABUSE",
                 "UNDERPAID_EXPERIENCED","SENIOR_EXPLOITATION"]
    counts = {f: all_df["anomaly_flags"].str.contains(f, na=False).sum() for f in all_flags}
    counts = {k.replace("_"," ").title():v for k,v in counts.items() if v>0}
    if not counts: return
    total = len(all_df)
    fig, ax = sf(8, max(4,len(counts)*0.7))
    bar_colors = [RED if v/total>=0.4 else YELLOW if v/total>=0.2 else ORANGE for v in counts.values()]
    bars = ax.barh(list(counts.keys()), list(counts.values()), color=bar_colors, height=0.5, edgecolor="none")
    for bar,val in zip(bars, counts.values()):
        ax.text(bar.get_width()+0.05, bar.get_y()+bar.get_height()/2,
                f"{val} jobs ({val/total*100:.0f}%)", va="center", color=TEXT, fontsize=9)
    ax_style(ax, f"Exploitation Signal Flags — All {total} Jobs")
    ax.set_xlabel("Jobs Flagged"); ax.tick_params(axis="y", colors=TEXT)
    ax.set_xlim(0, max(counts.values())*1.55); ax.grid(axis="x", color=BORDER, lw=0.5, alpha=0.5)
    save("reports/anomaly_flags.png")

# 12. Salary Scatter — ALL jobs
def chart_salary_scatter(all_df):
    if all_df.empty: return
    df = all_df.dropna(subset=["salary_usd"])
    if len(df) < 2: return
    fig, ax = sf(10,5)
    for domain, grp in df.groupby("domain"):
        ax.scatter(grp["years_required"], grp["salary_usd"]/1000,
                   color=DOMAIN_COLORS.get(domain,MUTED), s=70, alpha=0.85,
                   label=domain, zorder=3, edgecolors="none")
    if len(df) >= 3:
        z  = np.polyfit(df["years_required"], df["salary_usd"]/1000, 1)
        xl = np.linspace(df["years_required"].min(), df["years_required"].max(), 100)
        ax.plot(xl, np.poly1d(z)(xl), color=MUTED, lw=1.5, ls="--", alpha=0.5, label="Trend")
    ax_style(ax, f"Salary (USD) vs Experience — All {len(df)} Jobs with Salary Data")
    ax.set_xlabel("Years Required"); ax.set_ylabel("Annual Salary (USD thousands)")
    ax.legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=8, loc="upper left", ncol=3)
    ax.grid(color=BORDER, lw=0.5, alpha=0.4)
    save("reports/salary_vs_experience.png")

# README Updater
def update_readme(gdf, month, agg_df, all_df):
    readme = "README.md"
    if not os.path.exists(readme): return
    rows_for_month = gdf[gdf["month"]==month]
    if rows_for_month.empty: rows_for_month = gdf[gdf["month"]==gdf["month"].max()]
    latest = rows_for_month.iloc[-1]
    with open(readme,"r",encoding="utf-8") as f: content = f.read()

    def rb(c, label, value, color):
        pat = rf'!\[{re.escape(label)}\]\(https://img\.shields\.io/badge/[^)]*\)'
        v = str(value).replace("-","--").replace(" ","%20")
        l = label.replace("-","--").replace(" ","%20")
        return re.sub(pat, f"![{label}](https://img.shields.io/badge/{l}-{v}-{color}?style=flat)", c)

    total_jobs = len(all_df) if not all_df.empty else int(gdf["job_count"].sum())
    content = rb(content,"Skill Score",     f"{latest['skill_score']:.2f}","red")
    content = rb(content,"Avg Years",       f"{latest['avg_years']:.1f}","blue")
    content = rb(content,"Avg Certs",       f"{latest['avg_certs']:.1f}","green")
    content = rb(content,"Avg Tools",       f"{latest['avg_tools']:.1f}","yellow")
    content = rb(content,"Jobs Analyzed",   total_jobs,"brightgreen")
    content = rb(content,"Last Updated",    month,"blue")
    if pd.notna(latest.get("exploitation_rate")):
        content = rb(content,"Exploitation Rate",f"{latest['exploitation_rate']:.0f}%25","orange")

    score=float(latest["skill_score"]); exploit=float(latest.get("exploitation_rate",0))
    sal=latest.get("avg_salary_usd",0)
    sal_str=f"~${float(sal):,.0f}" if pd.notna(sal) and sal else "N/A"
    sig_emoji="🔴 **HIGH INFLATION**" if score>3.0 else "🟡 **MODERATE INFLATION**" if score>2.0 else "🟢 **HEALTHY**"
    n_domains = agg_df["domain"].nunique() if not agg_df.empty else 6

    signal_block = f"""## ⚠️ Industry Signal — {pd.to_datetime(month+'-01').strftime('%B %Y')}

> {sig_emoji} — Global score **{score:.2f}**, {'above' if score>3.0 else 'below'} the 3.0 threshold. **{exploit:.0f}% of all listings** flagged for requirement signals.

| Metric | Value | Signal |
|--------|-------|--------|
| 📈 Global Skill Inflation Score | **{score:.2f}** | {'🔴 High — above threshold' if score>3.0 else '🟡 Moderate'} |
| 📅 Avg Years Required | **{float(latest['avg_years']):.1f} yrs** | 🔴 Rising across all domains |
| 🧠 Avg Certifications Demanded | **{float(latest['avg_certs']):.1f}** | 🟡 Cert creep industry-wide |
| 🛠️ Avg Tools Required | **{float(latest['avg_tools']):.1f}** | 🔴 High tool complexity |
| ⚠️ Requirement Signal Rate | **{exploit:.0f}%** | {'🔴 Majority of listings flagged' if exploit>50 else '🟡 Nearly half flagged'} |
| 💰 Avg Salary (USD) | **{sal_str}** | 🟡 Varies significantly by market |
| 💼 Total Jobs Analyzed | **{total_jobs}** | ✅ {n_domains} domains · 6 countries |"""

    content = re.sub(r'## ⚠️ Industry Signal.*?(?=\n---\n)', signal_block, content, flags=re.DOTALL)

    if not agg_df.empty:
        def derive_insight(row):
            parts=[]
            years=float(row["avg_years"]); certs=float(row["avg_certs"]); tools=float(row["avg_tools"])
            exploit=float(row.get("exploitation_rate",0)); sal=float(row["avg_salary_usd"]) if pd.notna(row.get("avg_salary_usd")) else 0
            threshold=45000+(years*5000)
            if sal>0 and years>=4:
                if sal<threshold*0.55:   parts.append(f"${sal:,.0f} avg for {years:.0f}+ yrs — pay gap critical")
                elif sal<threshold*0.80: parts.append(f"${sal:,.0f} avg vs {years:.0f}+ yrs — below market")
            if exploit==100:        parts.append("every listing flagged")
            elif exploit>=75:       parts.append(f"{exploit:.0f}% of listings flagged")
            if certs>=5:            parts.append(f"{certs:.1f} certs avg — extreme stacking")
            elif certs>=4:          parts.append(f"{certs:.1f} avg certs — above market norm")
            if tools>=5:            parts.append(f"{tools:.1f} tools required simultaneously")
            elif tools>=4:          parts.append(f"{tools:.1f} avg tools per listing")
            if not parts:
                score=float(row["skill_score"])
                if score>=4.0: parts.append(f"score {score:.2f} — highest requirement pressure")
                elif score>=3.0: parts.append(f"{years:.0f} yrs + {certs:.1f} certs now baseline")
                else: parts.append(f"most balanced — {years:.0f} yrs avg, {certs:.1f} certs")
            return "; ".join(parts[:2])

        domain_rows="".join(
            f"| {r['domain']} | {r['avg_years']:.1f} | {r['avg_certs']:.1f} | "
            f"{'🔴' if r['skill_score']>=3 else '🟡' if r['skill_score']>=2 else '🟢'} **{r['skill_score']:.2f}** | "
            f"{derive_insight(r)} | {int(r['job_count'])} |\n"
            for _,r in agg_df.sort_values("skill_score",ascending=False).iterrows()
        )
        domain_table=("| Domain | Avg Years | Avg Certs | Score | Signal | Jobs |\n"
                      "|--------|-----------|-----------|-------|--------|------|\n"+domain_rows)
        content=re.sub(r'\| Domain \| Avg Years \| Avg Certs \| Score \| Signal \| Jobs \|.*?(?=\n---\n|\n\n---)',
                       domain_table.rstrip(), content, flags=re.DOTALL)

    hist_rows="".join(
        f"| {r['month']} | {r['avg_years']:.2f} | {r['avg_certs']:.2f} | "
        f"{r['avg_tools']:.2f} | **{r['skill_score']:.2f}** | {int(r.get('job_count',0))} |\n"
        for _,r in gdf.iterrows()
    )
    hist_block=("| Month | Avg Years | Avg Certs | Avg Tools | Skill Score | Jobs |\n"
                "|-------|-----------|-----------|-----------|-------------|------|\n"+hist_rows)
    content=re.sub(r'\| Month \| Avg Years.*?(?=\n##|\Z)', hist_block.rstrip(), content, flags=re.DOTALL)
    with open(readme,"w",encoding="utf-8") as f: f.write(content)
    print("  ✓ README.md updated")

# Monthly Report
def write_report(gdf, ddf, month, agg_df):
    rows_for_month=gdf[gdf["month"]==month]
    if rows_for_month.empty: rows_for_month=gdf[gdf["month"]==gdf["month"].max()]
    latest=rows_for_month.iloc[-1]; score=float(latest["skill_score"])
    sig=("🔴 **HIGH INFLATION**" if score>3.0 else "🟡 **MODERATE INFLATION**" if score>2.0 else "🟢 **HEALTHY**")
    dtable="".join(
        f"| {r['domain']} | {r['avg_years']:.1f} | {r['avg_certs']:.1f} | {r['skill_score']:.2f} | "
        f"{'🔴' if r['skill_score']>=3 else '🟡'} | {int(r['job_count'])} |\n"
        for _,r in agg_df.sort_values("skill_score",ascending=False).iterrows()
    ) if not agg_df.empty else ""
    report=f"""# CSII Monthly Report — {month}\n\n## Signal: {sig}\n\n## Global Metrics\n| Metric | Value |\n|--------|-------|\n| Avg Years Required | {latest['avg_years']:.2f} |\n| Avg Certifications | {latest['avg_certs']:.2f} |\n| Avg Tools Required | {latest['avg_tools']:.2f} |\n| Skill Score | {score:.4f} |\n| Jobs This Month | {int(latest['job_count'])} |\n| Signal Rate | {latest.get('exploitation_rate',0):.1f}% |\n\n## Domain Intelligence — All Jobs\n| Domain | Avg Years | Avg Certs | Score | Signal | Total Jobs |\n|--------|-----------|-----------|-------|--------|------------|\n{dtable}"""
    os.makedirs("reports", exist_ok=True)
    with open("reports/Monthly-CSII-Report.md","w",encoding="utf-8") as f: f.write(report)
    print("  ✓ reports/Monthly-CSII-Report.md")

# Main
def generate():
    gpath="data/processed/monthly_index.csv"; dpath="data/processed/domain_index.csv"
    if not os.path.exists(gpath):
        print("No monthly_index.csv. Run calculate_index.py first."); return
    gdf=pd.read_csv(gpath); ddf=pd.read_csv(dpath) if os.path.exists(dpath) else None
    current_month=pd.Timestamp.now().strftime("%Y-%m")
    month=current_month if current_month in gdf["month"].values else gdf["month"].max()
    if month!=current_month: print(f"  ℹ  No data for {current_month} — using {month}")
    os.makedirs("reports", exist_ok=True)
    all_df=load_all_jobs(); agg_df=aggregate_domains(all_df)
    n_months=all_df["month"].nunique() if not all_df.empty else 0
    print(f"Generating charts from {len(all_df)} total jobs across {n_months} months...")
    chart_global_trend(gdf)
    chart_domain_comparison(agg_df)
    chart_domain_trend()
    chart_domain_donut(all_df)
    chart_exploitation_by_domain(agg_df)
    chart_seniority_by_domain(all_df)
    chart_salary_bubble(agg_df)
    chart_cert_demand()
    chart_tool_demand()
    chart_country_comparison()
    chart_anomalies(all_df)
    chart_salary_scatter(all_df)
    update_readme(gdf, month, agg_df, all_df)
    write_report(gdf, ddf, month, agg_df)
    print("✓ All done.")

if __name__=="__main__":
    generate()
