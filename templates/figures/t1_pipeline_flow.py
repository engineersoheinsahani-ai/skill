"""t1_pipeline_flow.py — FIG-GV template: leakage-audited ML pipeline diagram.

Advanced graphviz craft: layered clusters (data -> features -> AUDIT GATES ->
models -> conformal -> artifacts), gates as red-outlined decision diamonds,
edge labels naming the deposited artifact (input/results/...), rank alignment.
Known pitfall avoided: splines="ortho" DROPS edge labels -> use polyline.

Renders with local graphviz if available:  dot -Tpng -Gdpi=300 pipeline.dot
Otherwise the .dot source is still written (owner renders anywhere).
"""
import os, subprocess, sys

DOT = """digraph pipeline {
  rankdir=TB; splines=polyline; nodesep=0.35; ranksep=0.5;
  bgcolor="white";
  node [shape=box, style="rounded,filled", fillcolor="#F5F7FA",
        color="#0072B2", fontname="Arial", fontsize=10, penwidth=0.8];
  edge [fontname="Arial", fontsize=8, color="#555555", penwidth=0.8];

  subgraph cluster_data {
    label="1 · DATA (provenance)"; style=dashed; color="#0072B2"; fontsize=11;
    recs   [label="RECS 2020 microdata\\n(18,496 households)"];
    tmy    [label="TMY3 weather\\n(station-matched)"];
    split  [label="splits: train / test /\\nCALIBRATION (untouched) / LOGO"];
    recs -> split; tmy -> split;
  }

  subgraph cluster_feat {
    label="2 · FEATURES (fit-on-train only)"; style=dashed; color="#009E73"; fontsize=11;
    ph     [label="PH_* physics features\\n(geometry/thermodynamics)"];
    enc    [label="encoders + scalers\\n(fit on TRAIN folds only)"];
    ph -> enc;
  }

  subgraph cluster_audit {
    label="3 · LEAKAGE AUDIT (9 tests)"; style=dashed; color="#D55E00"; fontsize=11;
    node [shape=diamond, fillcolor="#FFF3E8", color="#D55E00"];
    a1 [label="A-B: identifier &\\ntarget-derived scan"];
    a2 [label="C-E: transform\\nfit-scope checks"];
    a3 [label="F-I: temporal/group\\nholdout integrity"];
    a1 -> a2 -> a3;
  }

  subgraph cluster_model {
    label="4 · MODELS"; style=dashed; color="#CC79A7"; fontsize=11;
    node [shape=box, style="rounded,filled", fillcolor="#FDF2F8", color="#CC79A7"];
    base [label="baselines\\n(linear / GBM / RF)"];
    stack [label="OOF stacking\\n(honest out-of-fold)"];
    base -> stack [label="oof_meta.csv"];
  }

  subgraph cluster_conf {
    label="5 · CONFORMAL UQ"; style=dashed; color="#E69F00"; fontsize=11;
    node [shape=box, style="rounded,filled", fillcolor="#FEF9EC", color="#E69F00"];
    cal  [label="calibration split\\n(never trained on)"];
    int  [label="90% prediction\\nintervals"];
    cal -> int;
  }

  subgraph cluster_out {
    label="6 · ARTIFACTS (input/results/)"; style=dashed; color="#000000"; fontsize=11;
    man [label="run_manifest.json\\n(every published number)"];
    aud [label="leakage_audit.json\\n(passed: true)"];
    tbl [label="tables/ + figures/"];
  }

  split -> ph; enc -> a1; a3 -> base [label="audit passed"];
  stack -> cal; int -> man; a3 -> aud [label="9/9 tests"]; stack -> tbl;
}
"""


def main(outdir="rendered"):
    os.makedirs(outdir, exist_ok=True)
    dot_path = os.path.join(outdir, "t1_pipeline_flow.dot")
    open(dot_path, "w", encoding="utf-8").write(DOT)
    print("wrote", dot_path)
    for fmt in ("png", "pdf"):
        out = os.path.join(outdir, f"t1_pipeline_flow.{fmt}")
        try:
            subprocess.run(["dot", f"-T{fmt}", "-Gdpi=300", dot_path, "-o", out],
                           check=True, capture_output=True)
            print("rendered", out)
        except (OSError, subprocess.CalledProcessError) as e:
            print(f"graphviz 'dot' not available ({e}) — render the .dot anywhere: "
                  f"dot -T{fmt} -Gdpi=300 {dot_path} -o {out}")
            break


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "rendered")
