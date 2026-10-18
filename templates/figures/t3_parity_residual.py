"""t3_parity_residual.py — FIG-MPL template: parity density + residual regime violins.

Advanced craft: log-log hexbin parity (density instead of overplot), 1:1 and
±20% guides, NMBE/CV(RMSE) annotation box anchored to artifact values,
residual distributions per climate regime as split violins with seed-CI notches.
Synthetic demo data — replace with values from input/results (law 10).
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from enb_style import apply_style, save_enb, OKABE_ITO


def main(outdir="rendered"):
    apply_style()
    rng = np.random.default_rng(11)
    n = 4200
    true = np.exp(rng.normal(np.log(6000), 0.75, n))          # kWh, log-normal-ish
    err = rng.normal(0, 0.16, n) + 0.05 * np.sin(np.log(true))  # heteroscedastic
    pred = true * np.exp(err)
    regimes = rng.choice(["hot", "mixed", "cold", "marine"], n, p=[.28, .34, .25, .13])

    fig = plt.figure(figsize=(7.48, 2.9))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1.0], wspace=0.22)

    ax = fig.add_subplot(gs[0, 0])
    hb = ax.hexbin(true, pred, xscale="log", yscale="log", gridsize=42,
                   cmap="Blues", mincnt=1, bins="log")
    lims = [true.min() * 0.8, true.max() * 1.25]
    ax.axline((lims[0], lims[0]), (lims[1], lims[1]), lw=0.8, color="k")
    ax.axline((lims[0], lims[0] * 1.2), (lims[1], lims[1] * 1.2), lw=0.5,
              ls=":", color=OKABE_ITO[1])
    ax.axline((lims[0], lims[0] / 1.2), (lims[1], lims[1] / 1.2), lw=0.5,
              ls=":", color=OKABE_ITO[1])
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("measured annual EUI (kWh)"); ax.set_ylabel("predicted (kWh)")
    ax.set_title("a · parity (log density)", loc="left")
    cb = fig.colorbar(hb, ax=ax, pad=0.015)
    cb.set_label("households (log)", fontsize=6.5)
    cb.ax.tick_params(labelsize=6)
    ax.text(0.03, 0.95, "NMBE = [number needed]\nCV(RMSE) = [number needed]\nR² = [number needed]",
            transform=ax.transAxes, va="top", fontsize=6.5,
            bbox=dict(fc="white", ec="#999999", lw=0.5, boxstyle="round,pad=0.3"))

    ax2 = fig.add_subplot(gs[0, 1])
    resid = 100 * (pred - true) / true
    data = [resid[regimes == r] for r in ["hot", "mixed", "cold", "marine"]]
    parts = ax2.violinplot(data, positions=[1, 2, 3, 4], widths=0.82,
                           showmedians=True, quantiles=[[-0.5], [-0.5], [-0.5], [-0.5]])
    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(OKABE_ITO[i % 6]); pc.set_alpha(0.55); pc.set_edgecolor("none")
    parts["cmedians"].set_color("#000000"); parts["cmedians"].set_linewidth(1.0)
    ax2.axhline(0, lw=0.7, color="k")
    ax2.axhspan(-20, 20, color=OKABE_ITO[2], alpha=0.08, lw=0)
    ax2.set_xticks([1, 2, 3, 4], ["hot", "mixed", "cold", "marine"])
    ax2.set_ylabel("residual (%)"); ax2.set_xlabel("climate regime (LOGO holdout)")
    ax2.set_title("b · residual distribution by regime", loc="left")
    save_enb(fig, "t3_parity_residual", width="full", outdir=outdir, height=2.9)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "rendered")
