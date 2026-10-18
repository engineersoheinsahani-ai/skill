"""t2_conformal_calibration.py — FIG-MPL template: conformal coverage calibration.

Advanced craft: empirical vs nominal coverage with binomial 95% bands (honest
uncertainty ON the QC plot itself), marginal-interval-width on a twin axis,
per-regime markers (LOGO holdouts), inset zoom on the operating point (90%).
Synthetic demo data — replace `empirical`/`widths` arrays with values read
from input/results artifacts (law 10: never invent numbers).
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from enb_style import apply_style, save_enb, OKABE_ITO


def main(outdir="rendered"):
    apply_style()
    rng = np.random.default_rng(7)
    nominal = np.linspace(0.50, 0.99, 12)
    n_cal = 1800                                   # calibration split size
    # synthetic: slightly conservative coverage + binomial noise
    empirical = np.clip(nominal + rng.normal(0.004, 0.006, nominal.size), 0.45, 0.999)
    widths = 0.9 + 5.2 * nominal**2.4 + rng.normal(0, 0.05, nominal.size)
    se = np.sqrt(nominal * (1 - nominal) / n_cal)  # binomial SE

    fig, ax = plt.subplots(figsize=(3.543, 3.0))
    ax.axline((0.5, 0.5), (0.99, 0.99), lw=0.8, ls="--", color="#000000",
              label="ideal (nominal = empirical)")
    ax.fill_between(nominal, nominal - 1.96 * se, nominal + 1.96 * se,
                    color=OKABE_ITO[0], alpha=0.15, lw=0,
                    label="95% binomial band (n_cal=1800)")
    ax.errorbar(nominal, empirical, yerr=1.96 * se, fmt="o", ms=3.2, lw=0.8,
                capsize=1.6, color=OKABE_ITO[0], label="all households")
    ax.plot(nominal, np.clip(empirical - 0.012 + rng.normal(0, 0.003, 12), .4, 1),
            "s", ms=2.8, color=OKABE_ITO[1], label="hot-climate LOGO holdout")
    ax.plot(nominal, np.clip(empirical + 0.010 + rng.normal(0, 0.003, 12), .4, 1),
            "^", ms=2.8, color=OKABE_ITO[2], label="cold-climate LOGO holdout")

    ax2 = ax.twinx()
    ax2.plot(nominal, widths, lw=1.0, ls=":", color=OKABE_ITO[4])
    ax2.set_ylabel("mean interval width (kWh)", color=OKABE_ITO[4])
    ax2.tick_params(axis="y", colors=OKABE_ITO[4])
    ax2.grid(False)

    axin = ax.inset_axes([0.06, 0.62, 0.34, 0.34])
    m = (nominal > 0.86) & (nominal < 0.94)
    axin.plot(nominal[m], empirical[m], "o-", ms=2.5, lw=0.8, color=OKABE_ITO[0])
    axin.axline((0.9, 0.9), slope=1, lw=0.6, ls="--", color="k")
    axin.annotate("operating point\n90% → 90.2%", (0.90, 0.902), fontsize=5.6,
                  xytext=(0.865, 0.93), arrowprops=dict(arrowstyle="->", lw=0.5))
    axin.set_xlim(0.86, 0.94); axin.set_ylim(0.86, 0.94)
    axin.tick_params(labelsize=5.5)

    ax.set_xlabel("nominal coverage level"); ax.set_ylabel("empirical coverage")
    ax.set_xlim(0.5, 1.0); ax.set_ylim(0.5, 1.0)
    ax.legend(loc="lower right", frameon=False, fontsize=6)
    save_enb(fig, "t2_conformal_calibration", width="single", outdir=outdir, height=3.0)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "rendered")
