"""enb_style.py — Energy & Buildings figure style (journal-arena v4-pro).

Usage:
    from enb_style import apply_style, save_enb, OKABE_ITO
    apply_style()
    ... build figure ...
    save_enb(fig, "fig1_parity", width="single")     # -> fig1_parity.pdf + .png

Deterministic ENB compliance:
  * 300 dpi always; PNG saved WITHOUT bbox-tight so pixel widths are EXACT:
    single column 3.543 in = 1063 px | 1.5 column 5.38 in = 1615 px |
    full page 7.48 in = 2244 px  (ENB-FIG-2, checklists/01)
  * all text >= 7 pt at final size (rcParams floor)
  * Okabe-Ito palette — colourblind-safe by construction (passes figureqc)
  * vector PDF alongside raster PNG (Elsevier accepts both; PDF keeps fonts)
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cycler

OKABE_ITO = ["#0072B2", "#D55E00", "#009E73", "#CC79A7",
             "#E69F00", "#56B4E9", "#000000"]
WIDTHS = {"single": 3.543, "onehalf": 5.38, "full": 7.48}   # inches @ 300 dpi


def apply_style():
    plt.rcParams.update({
        "figure.dpi": 300, "savefig.dpi": 300,
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 7.5, "axes.labelsize": 8.0, "axes.titlesize": 8.5,
        "xtick.labelsize": 7.0, "ytick.labelsize": 7.0, "legend.fontsize": 7.0,
        "axes.linewidth": 0.6, "lines.linewidth": 1.0, "patch.linewidth": 0.5,
        "axes.prop_cycle": cycler(color=OKABE_ITO),
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.linewidth": 0.4, "grid.alpha": 0.3,
        "figure.constrained_layout.use": True,
        "savefig.facecolor": "white",
    })


def save_enb(fig, name, width="single", outdir="rendered", height=None):
    """Save PDF+PNG at the EXACT ENB width class. Returns the png path."""
    w = WIDTHS[width]
    h = height if height else fig.get_size_inches()[1]
    fig.set_size_inches(w, h)
    os.makedirs(outdir, exist_ok=True)
    fig.savefig(os.path.join(outdir, f"{name}.pdf"), dpi=300)
    png = os.path.join(outdir, f"{name}.png")
    fig.savefig(png, dpi=300)          # no bbox_inches -> exact 1063/1615/2244 px
    px = int(round(w * 300))
    print(f"saved {png} ({px} px wide, 300 dpi) + PDF twin")
    return png
