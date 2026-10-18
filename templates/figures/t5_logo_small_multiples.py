"""t5_logo_small_multiples.py — FIG-MPL template: LOGO holdout small multiples.

Advanced craft (generalisation evidence, LBNL good-practice: report performance
on unseen groups): shared-y small multiples, one facet per held-out climate
regime, model families as grouped bars with paired-seed 95% CIs, full-refit
reference line per facet, honest 'transfer adds nothing' annotation slot.
Synthetic demo data — replace with values from input/results (law 10).
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from enb_style import apply_style, save_enb, OKABE_ITO


def main(outdir="rendered"):
    apply_style()
    rng = np.random.default_rng(5)
    regimes = ["hot-humid", "hot-dry", "mixed", "cold", "very cold", "marine"]
    models = ["linear", "GBM", "stack-OOF", "+transfer"]
    base = {"linear": 0.52, "GBM": 0.68, "stack-OOF": 0.776, "+transfer": 0.778}

    fig, axes = plt.subplots(2, 3, figsize=(7.48, 3.6), sharey=True)
    for ax, reg in zip(axes.ravel(), regimes):
        shift = rng.normal(0, 0.045)
        vals, cis = [], []
        for m in models:
            v = base[m] + shift + rng.normal(0, 0.012)
            vals.append(v); cis.append(abs(rng.normal(0.012, 0.005)))
        x = np.arange(len(models))
        for i, (v, c, m) in enumerate(zip(vals, cis, models)):
            ax.bar(i, v, width=0.68, color=OKABE_ITO[i % 6], alpha=0.9 if i < 3 else 0.45,
                   edgecolor="none")
            ax.errorbar(i, v, yerr=c, fmt="none", ecolor="#222222", elinewidth=0.7,
                        capsize=1.6)
        ax.axhline(base["stack-OOF"] + 0.002, lw=0.6, ls="--", color="#000000")
        ax.set_title(f"{reg} (held out)", fontsize=7.5, loc="left")
        ax.set_xticks(x, models, fontsize=5.8, rotation=20, ha="right")
        ax.set_ylim(0.35, 0.90)
        ax.grid(axis="x", visible=False)
    axes[0, 0].set_ylabel("test R² (full refit)")
    axes[1, 0].set_ylabel("test R² (full refit)")
    fig.suptitle("leave-one-regime-out: every model refit without the facet's regime",
                 fontsize=8.5, x=0.02, ha="left")
    save_enb(fig, "t5_logo_small_multiples", width="full", outdir=outdir, height=3.6)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "rendered")
