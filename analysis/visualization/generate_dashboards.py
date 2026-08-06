"""
Construction Change Order and RFI Analytics - dashboard generation.

Regenerates every dashboard in share/assets/ directly from the analytical CSV
outputs in analysis/tables/. Deterministic: same inputs, same pixels.

Usage:
    python analysis/visualization/generate_dashboards.py [output_dir]

Data disclosure: all records are synthetic. See documentation/.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inproject_bi import (  # noqa: E402
    Dashboard, STATUS, BRICK, BRICK_2, NAVY_3, GREEN, AMBER, RED, INK, MUTED,
    MONEY, money, hbar, grouped_bar, donut, table_panel,
)

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "analysis" / "tables"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "share" / "assets"

STEEL = "#53616D"
SAGE = "#647267"


def read(n):
    return pd.read_csv(T / n, encoding="utf-8-sig")


kpi = read("executive_kpis.csv").set_index("KPI")["Value"].astype(float)
health = read("project_health_distribution.csv")
cat = read("change_category_summary.csv")
party = read("change_initiating_party_summary.csv")
top10 = read("top_10_priority_projects.csv")
year = read("yearly_trend_summary.csv")
disc = read("rfi_discipline_summary.csv")
rtype = read("rfi_type_summary.csv")
seg = read("lifecycle_segment_summary.csv")
bott = read("workflow_bottleneck_summary.csv")
assoc = read("association_results.csv")
risk = read("project_workflow_risk_summary.csv")

SUB = ("Decision speed, commercial exposure and workflow health across a "
       "90-project synthetic construction portfolio, 2022-2025.")
ORDER = ["Red", "Yellow", "Green"]


def clip(s, n=24):
    """Truncate on a word boundary so names never break mid-word."""
    s = str(s)
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0]
    return (cut or s[:n]) + "…"


# ==========================================================  1. Executive
def executive():
    d = Dashboard("Change Order and RFI Analytics", SUB,
                  eyebrow="Executive portfolio view")
    d.kpis([
        (f"{int(kpi['Projects'])}", "Projects", NAVY_3),
        (f"{int(kpi['RFIs']):,}", "RFIs", NAVY_3),
        (f"{kpi['Average RFI response']:.1f} d", "Avg RFI response", AMBER),
        (f"{kpi['RFI on-time rate']:.1f}%", "RFI on-time rate", RED),
        (money(kpi["Approved change value"]), "Approved change value", BRICK),
        (money(kpi["Pending change exposure"]), "Pending exposure", AMBER),
    ])

    hs = health.set_index("Workflow_Health")["Project_Count"]
    ax = d.panel((0.0, 0.52, 0.30, 0.48), "Workflow health",
                 "Projects by composite risk band")
    donut(ax, ORDER, [int(hs[k]) for k in ORDER], [STATUS[k] for k in ORDER],
          centre_value=int(hs.sum()), centre_label="projects")

    c = cat.sort_values("Approved_Value", ascending=False).head(6)
    ax = d.panel((0.32, 0.52, 0.68, 0.48), "Commercial exposure by change category",
                 "Approved value versus pending exposure")
    grouped_bar(ax, [t.replace(" or ", " / ").replace("Requirement", "Req.")
                     for t in c["Change_Category"]],
                [("Approved value", c["Approved_Value"].tolist(), BRICK),
                 ("Pending exposure", c["Pending_Exposure"].tolist(), STEEL)],
                fmt=MONEY)
    ax.tick_params(axis="x", labelrotation=12)

    ax = d.panel((0.0, 0.0, 0.46, 0.48), "Response and approval trend",
                 "Average RFI response and change approval cycle, by year")
    yr = year.sort_values("Year")
    ax.plot(yr["Year"], yr["Avg_RFI_Response_Days"], marker="o", color=BRICK,
            linewidth=2.4, label="RFI response days", zorder=3)
    ax.plot(yr["Year"], yr["Avg_Approval_Cycle_Days"], marker="s", color=NAVY_3,
            linewidth=2.4, label="Change approval days", zorder=3)
    for _, r in yr.iterrows():
        ax.annotate(f"{r['Avg_RFI_Response_Days']:.1f}",
                    (r["Year"], r["Avg_RFI_Response_Days"]),
                    textcoords="offset points", xytext=(0, -15), ha="center",
                    fontsize=8.4, color=BRICK)
        ax.annotate(f"{r['Avg_Approval_Cycle_Days']:.1f}",
                    (r["Year"], r["Avg_Approval_Cycle_Days"]),
                    textcoords="offset points", xytext=(0, 9), ha="center",
                    fontsize=8.4, color=NAVY_3)
    ax.set_xticks(yr["Year"].tolist())
    ax.set_ylabel("Days")
    ax.set_ylim(0, yr["Avg_Approval_Cycle_Days"].max() * 1.4)
    ax.legend(fontsize=9, ncol=2, loc="upper left")
    ax.grid(axis="x", visible=False)

    ax = d.panel((0.48, 0.0, 0.52, 0.48), "Projects requiring management attention",
                 "Ranked by composite workflow risk score")
    t = top10.head(7)
    table_panel(
        ax, ["Project", "Risk", "Health", "RFI days", "Approval", "Pending %"],
        [[f"{r.Project_ID}  {clip(r.Project_Name)}", f"{int(r.Workflow_Risk_Score)}",
          r.Workflow_Health, f"{r.Avg_Response_Days:.1f}",
          f"{r.Avg_Approval_Cycle_Days:.1f}", f"{r.Pending_Exposure_Pct_Budget:.2f}%"]
         for r in t.itertuples()],
        widths=[0.44, 0.08, 0.13, 0.12, 0.12, 0.11],
        aligns=["left", "right", "left", "right", "right", "right"],
        cell_colors={(i, 2): STATUS.get(r.Workflow_Health, INK)
                     for i, r in enumerate(t.itertuples())})
    d.save(OUT / "construction_change_order_rfi_executive_dashboard.png")


# ==========================================================  2. Operational
def operational():
    d = Dashboard("RFI Response Performance",
                  "Where response time is lost, and what it costs downstream.",
                  eyebrow="Operational insights")
    d.kpis([
        (f"{int(kpi['Open RFIs'])}", "Open RFIs", AMBER),
        (f"{int(kpi['Overdue open RFIs'])}", "Overdue open", RED),
        (f"{kpi['Median RFI response']:.0f} d", "Median response", NAVY_3),
        (f"{kpi['RFI-to-change conversion']:.1f}%", "RFI to change", BRICK),
        (money(kpi["RFI actual cost impact"]), "RFI cost impact", BRICK),
        (f"{int(kpi['RFI actual schedule impact']):,} d", "RFI schedule impact", AMBER),
    ])

    dd = disc.sort_values("Avg_Response_Days", ascending=False).head(8)
    ax = d.panel((0.0, 0.52, 0.50, 0.48), "Response time by discipline",
                 "Average days to respond; slowest first", left=0.24)
    hbar(ax, dd["Discipline"].tolist(), dd["Avg_Response_Days"].tolist(),
         color=BRICK, fmt=lambda v: f"{v:.1f} d")
    ax.set_xlabel("Average response days")

    ax = d.panel((0.52, 0.52, 0.48, 0.48), "On-time rate by discipline",
                 "Share of RFIs answered within the required window", left=0.26)
    dd2 = disc.sort_values("On_Time_Rate_Pct")
    cols = [RED if v < 40 else AMBER if v < 50 else GREEN
            for v in dd2["On_Time_Rate_Pct"]]
    hbar(ax, dd2["Discipline"].tolist(), dd2["On_Time_Rate_Pct"].tolist(),
         colors=cols, fmt=lambda v: f"{v:.1f}%")
    ax.set_xlabel("On-time rate (%)")

    rt = rtype.sort_values("Actual_Cost_Impact", ascending=False)
    ax = d.panel((0.0, 0.0, 0.50, 0.48), "Cost impact by RFI type",
                 "Actual recorded cost impact of resolved RFIs", left=0.26)
    hbar(ax, [clip(t, 21) for t in rt["RFI_Type"]],
         rt["Actual_Cost_Impact"].tolist(), color=BRICK_2,
         fmt=lambda v: money(v))
    ax.xaxis.set_major_formatter(MONEY)
    ax.set_xlabel("Actual cost impact")

    ax = d.panel((0.52, 0.0, 0.48, 0.48), "Delivery conditions and response speed",
                 "Owner decision profile and digital coordination level")
    labels, resp, ontime, cols = [], [], [], []
    for _, r in seg.iterrows():
        labels.append(f"{r['Segment']}\n{r['Segment_Type'].split()[0]}")
        resp.append(r["Avg_RFI_Response_Days"])
        ontime.append(r["On_Time_Rate_Pct"])
        cols.append(BRICK if r["Segment_Type"].startswith("Owner") else STEEL)
    grouped_bar(ax, labels,
                [("Avg response days", resp, BRICK),
                 ("On-time rate %", ontime, STEEL)])
    ax.tick_params(axis="x", labelsize=8.2)
    d.save(OUT / "construction_change_order_rfi_operational_dashboard.png")


# ==========================================================  3. Workflow
def workflow():
    d = Dashboard("Workflow Bottlenecks and Drivers",
                  "Where approval time accumulates, and which behaviours travel with it.",
                  eyebrow="Workflow analysis")
    d.kpis([
        (f"{int(kpi['Change orders']):,}", "Change orders", NAVY_3),
        (f"{int(kpi['Approved changes'])}", "Approved", GREEN),
        (f"{kpi['Average approval cycle']:.1f} d", "Avg approval cycle", AMBER),
        (f"{int(kpi['Old pending changes >35 days'])}", "Pending > 35 days", RED),
        (f"{kpi['Average forecast incorporation lag']:.1f} d", "Forecast lag", AMBER),
        (f"{int(kpi['Median RFI-to-change identification lag'])} d", "RFI to change lag", BRICK),
    ])

    b = bott.sort_values("Avg_Stage_Days", ascending=False).head(6)
    ax = d.panel((0.0, 0.52, 0.55, 0.48), "Slowest workflow stages",
                 "Average days in stage, by item type and accountable role",
                 left=0.34)
    hbar(ax, [f"{clip(r.To_Status, 24)}\n{clip(r.Assigned_To_Role, 22)}"
              for r in b.itertuples()],
         b["Avg_Stage_Days"].tolist(),
         colors=[BRICK if r.Item_Type == "Change Order" else STEEL for r in b.itertuples()],
         fmt=lambda v: f"{v:.1f} d")
    ax.tick_params(axis="y", labelsize=8.0)
    ax.set_xlabel("Average days in stage")
    ax.legend(handles=[
        plt.Line2D([], [], marker="s", linestyle="", color=BRICK, label="Change order"),
        plt.Line2D([], [], marker="s", linestyle="", color=STEEL, label="RFI"),
    ], fontsize=8.6, ncol=2, loc="lower right")

    rev = bott[bott["Revision_Loop_Count"] > 0].sort_values(
        "Revision_Loop_Count", ascending=False).head(6)
    ax = d.panel((0.57, 0.52, 0.43, 0.48), "Rework loops",
                 "Stages returned for revision or clarification", left=0.34)
    hbar(ax, [f"{clip(r.To_Status, 24)}\n{clip(r.Assigned_To_Role, 22)}"
              for r in rev.itertuples()],
         rev["Revision_Loop_Count"].tolist(), color=AMBER,
         fmt=lambda v: f"{int(v):,}")
    ax.tick_params(axis="y", labelsize=8.0)
    ax.set_xlabel("Revision loops")

    a = assoc.drop_duplicates(subset=["Relationship"]).copy()
    a["abs"] = a["Statistic"].abs()
    a = a.sort_values("abs", ascending=False).head(6)
    ax = d.panel((0.0, 0.0, 0.55, 0.48), "Tested relationships",
                 "Correlation strength; association only, not causation",
                 left=0.40)
    cols = [BRICK if v > 0 else STEEL for v in a["Statistic"]]
    hbar(ax, [clip(r.replace("Project average ", "Project avg ")
                    .replace(" vs ", "\nvs "), 46)
              for r in a["Relationship"]],
         a["abs"].tolist(), colors=cols, fmt=lambda v: f"{v:.3f}")
    ax.tick_params(axis="y", labelsize=7.6)
    ax.set_xlabel("|correlation coefficient|")

    p = party.sort_values("Approved_Value", ascending=False)
    ax = d.panel((0.57, 0.0, 0.43, 0.48), "Approved value by initiating party",
                 "Who originates the commercial exposure", left=0.28)
    hbar(ax, p["Initiating_Party"].tolist(), p["Approved_Value"].tolist(),
         color=BRICK, fmt=lambda v: money(v))
    ax.xaxis.set_major_formatter(MONEY)
    ax.set_xlabel("Approved change value")
    d.save(OUT / "construction_change_order_rfi_workflow_analysis.png")


# ==========================================================  4. Priority
def priority():
    d = Dashboard("Project Priority and Intervention",
                  "Which projects to review first, and the pattern that identifies them.",
                  eyebrow="Management priorities")
    hs = health.set_index("Workflow_Health")["Project_Count"]
    d.kpis([
        (f"{int(hs['Red'])}", "Red projects", RED),
        (f"{int(hs['Yellow'])}", "Yellow projects", AMBER),
        (f"{int(hs['Green'])}", "Green projects", GREEN),
        ("0.817", "Response vs approval r", BRICK),
        (money(kpi["Linked approved change value"]), "RFI-linked change value", BRICK_2),
        (f"{kpi['RFI on-time rate']:.1f}%", "Portfolio on-time rate", RED),
    ])

    ax = d.panel((0.0, 0.50, 0.52, 0.50), "The portfolio-level pattern",
                 "Projects with slower RFI response also approve changes more slowly (Pearson r = 0.817)")
    for band in ORDER:
        s = risk[risk["Workflow_Health"] == band]
        ax.scatter(s["Avg_Response_Days"], s["Avg_Approval_Cycle_Days"],
                   s=28, color=STATUS[band], label=band, alpha=0.85,
                   edgecolor="white", linewidth=0.6, zorder=3)
    ax.set_xlabel("Average RFI response days")
    ax.set_ylabel("Average change approval days")
    ax.legend(fontsize=9, ncol=3, loc="upper left", title=None)

    ax = d.panel((0.54, 0.50, 0.46, 0.50), "Workflow risk score distribution",
                 "Composite score across the 90-project portfolio")
    counts = risk["Workflow_Risk_Score"].value_counts().sort_index()
    cols = [GREEN if s <= 3 else AMBER if s <= 6 else RED for s in counts.index]
    ax.bar(counts.index, counts.values, color=cols, width=0.72, zorder=3)
    for x, v in zip(counts.index, counts.values):
        ax.text(x, v + 0.4, str(int(v)), ha="center", va="bottom",
                fontsize=8.6, color=INK, zorder=4)
    ax.set_xlabel("Workflow risk score")
    ax.set_ylabel("Projects")
    ax.set_xticks(list(counts.index))
    ax.grid(axis="x", visible=False)
    ax.set_ylim(0, counts.values.max() * 1.18)

    ax = d.panel((0.0, 0.0, 1.0, 0.46), "Top 10 priority projects",
                 "Highest composite workflow risk; review these first")
    t = top10.head(10)
    table_panel(
        ax,
        ["#", "Project", "Type", "Delivery", "Health", "Risk", "RFI days",
         "On-time", "Approval", "Pending exposure"],
        [[str(i + 1), f"{r.Project_ID}  {clip(r.Project_Name, 26)}",
          r.Project_Type, r.Delivery_Method, r.Workflow_Health,
          f"{int(r.Workflow_Risk_Score)}", f"{r.Avg_Response_Days:.1f}",
          f"{r.On_Time_Rate_Pct:.1f}%", f"{r.Avg_Approval_Cycle_Days:.1f}",
          money(r.Pending_Change_Exposure)]
         for i, r in enumerate(t.itertuples())],
        widths=[0.035, 0.26, 0.105, 0.105, 0.075, 0.055, 0.075, 0.075, 0.08, 0.115],
        aligns=["right", "left", "left", "left", "left", "right", "right",
                "right", "right", "right"],
        cell_colors={(i, 4): STATUS.get(r.Workflow_Health, INK)
                     for i, r in enumerate(t.itertuples())})
    d.save(OUT / "construction_change_order_rfi_project_priority.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"Writing dashboards to {OUT}")
    executive()
    operational()
    workflow()
    priority()
    print("done")
