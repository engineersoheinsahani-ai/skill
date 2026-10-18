"""t4_feature_stability.py — FIG-MPL template: feature importance WITH stability.

Advanced craft (addresses the interpretability-review critique: SHAP/LIME ignore
seed & fold variance): lollipop mean-importance across 10 paired seeds, 95% CI
error bars, colour-coded feature families (physics / weather / survey / geometry),
instability flag marker (CI spanning the neighbour rank => 'unstable rank').
Synthetic demo data — replace with values from input/results (law 10).
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from enb_style import apply_style, save_enb, OKABE_ITO

FAMILIES = {"PH_": OKABE_ITO[2], "HDD/CDD": OKABE_ITO[0], "survey": OKABE_ITO[3],
            "geometry": OKABE_ITO[4]}


def main(outdir="rendered"):
    apply_style()
    rng = np.random.default_rng(3)
    names = ["PH_wall_R", "HDD65", "CDD65", "PH_window_area", "geometry_sqft",
             "survey_income", "PH_roof_R", "survey_occupants", "geometry_floors",
             "PH_infiltration", "survey_vintage", "PH_duct_eff"]
    fams = ["PH_", "HDD/CDD", "HDD/CDD", "PH_", "geometry", "survey",
            "PH_", "survey", "geometry", "PH_", "survey", "PH_"]
    mean = np.linspace(0.21, 0.045, len(names)) * rng.uniform(0.85, 1.15, len(names))
    ci = mean * rng.uniform(0.06, 0.42, len(names))          # seed spread
    order = np.argsort(mean)
    names = [names[i] for i in order]; mean = mean[order]; ci = ci[order]
    fams = [fams[i] for i in order]

    fig, ax = plt.subplots(figsize=(3.543, 3.4))
    y = np.arange(len(names))
    ax.hlines(y, 0, mean, lw=1.1, color="#BBBBBB", zorder=1)
    for i, (m, c, f) in enumerate(zip(mean, ci, fams)):
        unstable = c > 0.28 * m
        ax.errorbar(m, i, xerr=c, fmt="o", ms=3.4, lw=0.9, capsize=2.0,
                    color=FAMILIES[f], markeredgecolor="#D55E00" if unstable else FAMILIES[f],
                    markeredgewidth=1.1 if unstable else 0.6, zorder=2)
    ax.set_yticks(y, names, fontsize=6.5)
    ax.set_xlabel("mean |SHAP| (10 paired seeds) ± 95% CI")
    ax.set_title("feature importance with seed-stability", loc="left")
    handles = [plt.Line2D([], [], marker="o", ls="", ms=3.4, color=c, label=f)
               for f, c in FAMILIES.items()]
    handles.append(plt.Line2D([], [], marker="o", ls="", ms=3.6, mfc="w",
                              mec=OKABE_ITO[1], mew=1.1, label="unstable rank"))
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=6)
    ax.grid(axis="y", visible=False)
    save_enb(fig, "t4_feature_stability", width="single", outdir=outdir, height=3.4)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "rendered")
