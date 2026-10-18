"""t6_tornado_bounds.py — FIG-MPL template: retrofit-bounds tornado + sign flip.

Advanced craft (the manuscript's 'naive estimate flips sign; matched-cell
correction restores it' story as ONE figure): diverging tornado of assumption
sensitivities, naive vs corrected estimator pair with bootstrap CI, composition-
bias arrow annotation, honest bounds shading ([number needed] slots included).
Synthetic demo data — replace with values from input/results (law 10).
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from enb_style import apply_style, save_enb, OKABE_ITO


def main(outdir="rendered"):
    apply_style()
    rng = np.random.default_rng(13)
    fig = plt.figure(figsize=(7.48, 2.8))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.25, 1.0], wspace=0.25)

    # --- a) tornado: savings sensitivity to each assumption -----------------
    ax = fig.add_subplot(gs[0, 0])
    factors = ["baseline model", "weather year", "match-cell correction",
               "occupancy behaviour", "vintage mix", "measure costs"]
    low = np.array([-1.9, -1.1, -0.2, -0.8, -0.6, -0.4])
    high = np.array([2.4, 1.3, 3.1, 0.9, 0.7, 0.5])
    order = np.argsort(-(high - low))
    factors = [factors[i] for i in order]; low = low[order]; high = high[order]
    y = np.arange(len(factors))[::-1]
    for yi, lo, hi in zip(y, low, high):
        col = OKABE_ITO[2] if hi > 0 > lo else OKABE_ITO[0]
        ax.barh(yi, hi - lo, left=lo, height=0.55, color=col, alpha=0.75,
                edgecolor="none")
        ax.text(hi + 0.12, yi, f"[{lo:+.1f}, {hi:+.1f}]", va="center", fontsize=6)
    ax.axvline(0, lw=0.8, color="k")
    ax.set_yticks(y, factors, fontsize=6.8)
    ax.set_xlabel("retrofit savings (TWh/yr, national stock)")
    ax.set_title("a · assumption sensitivity (simulation-validated bounds)", loc="left")
    ax.grid(axis="y", visible=False)

    # --- b) naive vs corrected estimator ------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    naive = rng.normal(-0.4, 0.5, 2000)             # sign-flipped naive estimate
    corr = rng.normal(1.6, 0.45, 2000)              # matched-cell corrected
    parts = ax2.violinplot([naive, corr], positions=[1, 2], widths=0.8,
                           showmedians=True)
    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(OKABE_ITO[1] if i == 0 else OKABE_ITO[2])
        pc.set_alpha(0.55); pc.set_edgecolor("none")
    parts["cmedians"].set_color("k")
    ax2.axhline(0, lw=0.8, color="k")
    ax2.annotate("composition bias\n(sign flip)", (1, -0.05), fontsize=6.2,
                 xytext=(0.45, 1.9), arrowprops=dict(arrowstyle="->", lw=0.7,
                 connectionstyle="arc3,rad=0.25"))
    ax2.set_xticks([1, 2], ["naive\n(direct diff)", "matched-cell\ncorrected"])
    ax2.set_ylabel("savings (TWh/yr)")
    ax2.set_title("b · why the correction matters", loc="left")
    save_enb(fig, "t6_tornado_bounds", width="full", outdir=outdir, height=2.8)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "rendered")
