"""
In Project BI - shared dashboard toolkit.

A small matplotlib layer that renders Power BI / Tableau style dashboards in the
In Project design system: dark header band, KPI tile row, panelled charts on a
light canvas, and a synthetic-data footer.

Design tokens mirror inproject-ai-agents/public/site.css so charts, web and
reports stay in step.

Every figure is deterministic: same inputs, same pixels.
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.ticker import FuncFormatter

# ---------------------------------------------------------------- palette
NAVY = "#02000B"        # --navy      headline / header band
NAVY_2 = "#0C0A16"      # --navy-2
NAVY_3 = "#15121F"      # --navy-3
INK = "#262320"         # --ink       body copy
MUTED = "#5B564E"       # --muted     secondary copy
BRICK = "#A04732"       # --terracotta  primary accent
BRICK_2 = "#BD5A43"     # --terracotta-2
BEIGE = "#EDEAE2"       # --beige     tiles
BEIGE_DIM = "#C8C3BA"   # --beige-dim
BG = "#F6F3EC"          # --bg        canvas
SURFACE = "#FFFFFF"     # --surface   panel fill
LINE = "#E2DCCF"        # --line      rules and gridlines
GREEN = "#3F9D6B"       # --green
AMBER = "#C8881F"       # --amber
RED = "#C0492F"         # --red

STATUS = {"Red": RED, "Yellow": AMBER, "Green": GREEN}

# Ordered categorical ramp: terracotta-led, navy-anchored, brand-safe.
SERIES = [BRICK, "#53616D", "#C8881F", "#647267", "#BD5A43", "#8A8078", "#3F9D6B", NAVY_3]

FONT_DISPLAY = "Roboto Slab"
FONT_BODY = "Source Sans 3"

DISCLOSURE = ("Synthetic portfolio data - created for portfolio demonstration. "
              "Not actual client performance and not an industry benchmark.")


# ---------------------------------------------------------------- fonts
def register_fonts() -> tuple[str, str]:
    """Register the brand faces from wherever they live on this machine.

    Falls back to matplotlib defaults if the files are unavailable, so the
    script still runs on a clean checkout.
    """
    candidates = [
        Path(r"C:\Users\narci\projects\inproject-ai-agents\public\fonts"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Windows" / "Fonts",
        Path(r"C:\Windows\Fonts"),
        Path(__file__).resolve().parent / "fonts",
    ]
    found = set()
    for d in candidates:
        if not d.is_dir():
            continue
        for f in d.glob("*.ttf"):
            if any(k in f.name.replace(" ", "") for k in ("RobotoSlab", "SourceSans3")):
                try:
                    font_manager.fontManager.addfont(str(f))
                    found.add(f.name)
                except Exception:
                    pass
    names = {f.name for f in font_manager.fontManager.ttflist}
    display = FONT_DISPLAY if FONT_DISPLAY in names else "DejaVu Serif"
    body = FONT_BODY if FONT_BODY in names else "DejaVu Sans"
    return display, body


DISPLAY_FACE, BODY_FACE = register_fonts()

plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "font.family": [BODY_FACE],
    "font.size": 10,
    "text.color": INK,
    "axes.labelcolor": MUTED,
    "axes.edgecolor": LINE,
    "axes.facecolor": SURFACE,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": LINE,
    "grid.linewidth": 0.8,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "legend.frameon": False,
})


# ---------------------------------------------------------------- formatters
def money(v, _=None):
    a = abs(v)
    if a >= 1e9:
        return f"${v/1e9:,.2f}B"
    if a >= 1e6:
        return f"${v/1e6:,.1f}M"
    if a >= 1e3:
        return f"${v/1e3:,.0f}K"
    return f"${v:,.0f}"


def pct0(v, _=None):
    return f"{v:.0f}%"


def pct_frac(v, _=None):
    return f"{v*100:.0f}%"


MONEY = FuncFormatter(money)
PCT0 = FuncFormatter(pct0)
PCT_FRAC = FuncFormatter(pct_frac)


# ---------------------------------------------------------------- dashboard
class Dashboard:
    """A dashboard canvas: header band, optional KPI row, then panels.

    Coordinates are figure-relative (0-1). ``content`` gives the rectangle left
    for panels after the header, KPI row and footer have taken their space.
    """

    def __init__(self, title, subtitle="", width=16.0, height=9.5, eyebrow=None):
        self.fig = plt.figure(figsize=(width, height), facecolor=BG)
        self.w, self.h = width, height

        header_h = 0.9 / height
        self.fig.patches.append(Rectangle(
            (0, 1 - header_h), 1, header_h, transform=self.fig.transFigure,
            facecolor=NAVY, edgecolor="none", zorder=0))

        y = 1 - header_h
        if eyebrow:
            self.fig.text(0.022, y + header_h * 0.70, eyebrow.upper(), color=BRICK_2,
                          fontsize=9.5, fontweight="bold", family=BODY_FACE,
                          va="center", linespacing=1.0)
            self.fig.text(0.022, y + header_h * 0.36, title, color="#FFFFFF",
                          fontsize=17, fontweight="bold", family=DISPLAY_FACE, va="center")
        else:
            self.fig.text(0.022, y + header_h * 0.62, title, color="#FFFFFF",
                          fontsize=18, fontweight="bold", family=DISPLAY_FACE, va="center")
        if subtitle:
            self.fig.text(0.022, y + header_h * (0.14 if eyebrow else 0.26), subtitle,
                          color=BEIGE_DIM, fontsize=9.5, family=BODY_FACE, va="center")

        self._top = 1 - header_h - 0.022
        self._bottom = 0.052

    # ---- KPI tiles ----
    def kpis(self, tiles, height=0.135, gap=0.010):
        """tiles: list of (value, label) or (value, label, accent_colour)."""
        n = len(tiles)
        left, right = 0.022, 0.978
        span = right - left
        w = (span - gap * (n - 1)) / n
        top = self._top
        for i, t in enumerate(tiles):
            value, label = t[0], t[1]
            accent = t[2] if len(t) > 2 else BRICK
            x = left + i * (w + gap)
            self.fig.patches.append(FancyBboxPatch(
                (x, top - height), w, height,
                boxstyle="round,pad=0,rounding_size=0.006",
                transform=self.fig.transFigure, facecolor=SURFACE,
                edgecolor=LINE, linewidth=1.0, zorder=1))
            self.fig.patches.append(Rectangle(
                (x, top - height), 0.0035, height, transform=self.fig.transFigure,
                facecolor=accent, edgecolor="none", zorder=2))
            self.fig.text(x + w / 2, top - height * 0.42, str(value), ha="center",
                          va="center", fontsize=21, fontweight="bold",
                          color=NAVY, family=DISPLAY_FACE, zorder=3)
            self.fig.text(x + w / 2, top - height * 0.80, label.upper(), ha="center",
                          va="center", fontsize=8.6, color=MUTED,
                          family=BODY_FACE, zorder=3)
        self._top = top - height - 0.022

    # ---- panels ----
    def panel(self, rect, title=None, note=None, left=0.055, right=0.028,
              bottom=0.115):
        """rect = (x, y, w, h) inside the remaining content area.

        ``left`` is the axes inset as a fraction of panel width. Raise it for
        horizontal bars whose category labels would otherwise overflow.
        """
        cx, cy, cw, ch = rect
        x0 = 0.022 + cx * 0.956
        y0 = self._bottom + cy * (self._top - self._bottom)
        w0 = cw * 0.956
        h0 = ch * (self._top - self._bottom)

        self.fig.patches.append(FancyBboxPatch(
            (x0, y0), w0, h0, boxstyle="round,pad=0,rounding_size=0.006",
            transform=self.fig.transFigure, facecolor=SURFACE,
            edgecolor=LINE, linewidth=1.0, zorder=1))

        head = 0.0
        if title:
            self.fig.text(x0 + 0.014, y0 + h0 - 0.030, title, fontsize=11.5,
                          fontweight="bold", color=NAVY, family=DISPLAY_FACE,
                          va="center", zorder=3)
            head = 0.058
        if note:
            self.fig.text(x0 + 0.014, y0 + h0 - 0.030 - 0.028, note, fontsize=8.6,
                          color=MUTED, family=BODY_FACE, va="center", zorder=3)
            head += 0.030

        ax = self.fig.add_axes([
            x0 + left * w0,
            y0 + bottom * h0,
            w0 - (left + right) * w0,
            h0 - head - bottom * h0,
        ], zorder=2)
        ax.set_facecolor(SURFACE)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(LINE)
        ax.spines["bottom"].set_color(LINE)
        ax.tick_params(labelsize=9, length=0)
        return ax

    def text_panel(self, rect, title, lines, note=None):
        """A findings / narrative panel: numbered rows of (bold lead, body)."""
        cx, cy, cw, ch = rect
        x0 = 0.022 + cx * 0.956
        y0 = self._bottom + cy * (self._top - self._bottom)
        w0 = cw * 0.956
        h0 = ch * (self._top - self._bottom)
        self.fig.patches.append(FancyBboxPatch(
            (x0, y0), w0, h0, boxstyle="round,pad=0,rounding_size=0.006",
            transform=self.fig.transFigure, facecolor=SURFACE,
            edgecolor=LINE, linewidth=1.0, zorder=1))
        self.fig.text(x0 + 0.014, y0 + h0 - 0.030, title, fontsize=11.5,
                      fontweight="bold", color=NAVY, family=DISPLAY_FACE,
                      va="center", zorder=3)
        top = y0 + h0 - 0.030 - 0.040
        step = (top - y0 - 0.018) / max(len(lines), 1)
        for i, (lead, body) in enumerate(lines):
            yy = top - i * step - step * 0.30
            self.fig.text(x0 + 0.014, yy, lead, fontsize=9.4, fontweight="bold",
                          color=BRICK, family=BODY_FACE, va="center", zorder=3)
            self.fig.text(x0 + 0.014, yy - step * 0.34, body, fontsize=9.0,
                          color=INK, family=BODY_FACE, va="center", zorder=3,
                          wrap=True)
        if note:
            self.fig.text(x0 + 0.014, y0 + 0.012, note, fontsize=8.2, color=MUTED,
                          style="italic", family=BODY_FACE, va="bottom", zorder=3)

    # ---- output ----
    def save(self, path, disclosure=DISCLOSURE):
        self.fig.text(0.022, 0.020, disclosure, fontsize=8.2, color=MUTED,
                      style="italic", family=BODY_FACE, va="center")
        self.fig.text(0.978, 0.020, "In Project LLC", fontsize=8.2, color=MUTED,
                      family=BODY_FACE, va="center", ha="right")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.fig.savefig(path, facecolor=BG)
        plt.close(self.fig)
        print(f"  wrote {path.name}  ({path.stat().st_size/1024:.0f} KB)")


# ---------------------------------------------------------------- chart helpers
def hbar(ax, labels, values, color=BRICK, fmt=lambda v: f"{v:,.0f}",
         colors=None, pad_frac=0.16):
    """Horizontal bars, highest at top, value labelled at the bar end."""
    y = range(len(labels))
    cols = colors if colors is not None else [color] * len(labels)
    ax.barh(list(y), values, color=cols, height=0.62, zorder=3)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=9, color=INK)
    ax.invert_yaxis()
    ax.grid(axis="x", color=LINE, linewidth=0.8)
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    top = max(values) if len(values) else 1
    ax.set_xlim(0, top * (1 + pad_frac))
    for yy, v in zip(y, values):
        ax.text(v + top * 0.015, yy, fmt(v), va="center", ha="left",
                fontsize=8.8, color=INK, zorder=4)
    return ax


def vbar(ax, labels, values, color=BRICK, fmt=lambda v: f"{v:,.0f}", colors=None):
    x = range(len(labels))
    cols = colors if colors is not None else [color] * len(labels)
    ax.bar(list(x), values, color=cols, width=0.60, zorder=3)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=9, color=INK)
    ax.grid(axis="y", color=LINE, linewidth=0.8)
    ax.grid(axis="x", visible=False)
    top = max(values) if len(values) else 1
    ax.set_ylim(0, top * 1.18)
    for xx, v in zip(x, values):
        ax.text(xx, v + top * 0.03, fmt(v), ha="center", va="bottom",
                fontsize=8.8, color=INK, zorder=4)
    return ax


def grouped_bar(ax, labels, series, fmt=None, width=0.38,
                legend_loc="upper right", headroom=1.30):
    """series: list of (name, values, colour).

    ``headroom`` lifts the y-limit so the legend never sits on top of a bar.
    """
    n = len(series)
    x = range(len(labels))
    for i, (name, values, col) in enumerate(series):
        off = (i - (n - 1) / 2) * width
        ax.bar([xx + off for xx in x], values, width=width, label=name,
               color=col, zorder=3)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=9, color=INK)
    ax.grid(axis="y", color=LINE, linewidth=0.8)
    ax.grid(axis="x", visible=False)
    ax.legend(fontsize=9, ncol=n, loc=legend_loc)
    top = max(max(v) for _, v, _ in series)
    ax.set_ylim(0, top * headroom)
    if fmt:
        ax.yaxis.set_major_formatter(fmt)
    return ax


def donut(ax, labels, values, colors, centre_value=None, centre_label=None,
          legend_below=False):
    """Ring chart. Set ``legend_below`` in narrow panels, where a side legend
    would otherwise run into the centre label."""
    wedges, _ = ax.pie(values, colors=colors, startangle=90,
                       wedgeprops=dict(width=0.34, edgecolor=SURFACE, linewidth=2))
    ax.set(aspect="equal")
    if centre_value is not None:
        ax.text(0, 0.10, str(centre_value), ha="center", va="center",
                fontsize=20, fontweight="bold", color=NAVY, family=DISPLAY_FACE)
    if centre_label:
        ax.text(0, -0.20, centre_label.upper(), ha="center", va="center",
                fontsize=8.4, color=MUTED)
    total = sum(values) or 1
    entries = [f"{l}  {v:,.0f}  ({v/total:.0%})" for l, v in zip(labels, values)]
    if legend_below:
        ax.legend(wedges, entries, loc="upper center",
                  bbox_to_anchor=(0.5, -0.02), fontsize=8.8, ncol=1)
    else:
        ax.legend(wedges, entries, loc="center left",
                  bbox_to_anchor=(1.0, 0.5), fontsize=9)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    return ax


def table_panel(ax, columns, rows, widths=None, aligns=None, cell_colors=None):
    """A clean BI-style table drawn inside an axes."""
    ax.axis("off")
    ax.grid(False)
    ncol = len(columns)
    widths = widths or [1.0 / ncol] * ncol
    aligns = aligns or ["left"] * ncol
    xs, acc = [], 0.0
    for w in widths:
        xs.append(acc)
        acc += w
    nrow = len(rows)
    rh = 1.0 / (nrow + 1)

    ax.add_patch(Rectangle((0, 1 - rh), 1, rh, facecolor=NAVY,
                           edgecolor="none", transform=ax.transAxes, zorder=2))
    for j, c in enumerate(columns):
        a = aligns[j]
        px = xs[j] + (0.008 if a == "left" else widths[j] - 0.008 if a == "right"
                      else widths[j] / 2)
        ax.text(px, 1 - rh / 2, c, ha=a, va="center", fontsize=8.8,
                fontweight="bold", color="#FFFFFF", transform=ax.transAxes, zorder=3)

    for i, row in enumerate(rows):
        yy = 1 - (i + 2) * rh
        if i % 2 == 0:
            ax.add_patch(Rectangle((0, yy), 1, rh, facecolor=BG, edgecolor="none",
                                   transform=ax.transAxes, zorder=1))
        for j, val in enumerate(row):
            a = aligns[j]
            px = xs[j] + (0.008 if a == "left" else widths[j] - 0.008 if a == "right"
                          else widths[j] / 2)
            col = INK
            if cell_colors and (i, j) in cell_colors:
                col = cell_colors[(i, j)]
            ax.text(px, yy + rh / 2, str(val), ha=a, va="center", fontsize=8.7,
                    color=col, transform=ax.transAxes, zorder=3)
    return ax
