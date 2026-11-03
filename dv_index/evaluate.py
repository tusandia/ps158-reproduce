"""Score the flagging tool against the hand-coded gold standard.

Reads the finished coding sheet and the sample key from sample.py, and writes a
markdown report with:
    - precision / recall / F1 for "relevant" (direct or indirect) and for "direct",
      both in the raw sample and weighted back to the full set of bills, with
      95% bootstrap intervals (resampling within strata)
    - the 3x3 confusion table (gold vs predicted label)
    - per-impact-area precision / recall among bills coded relevant
    - every false negative and false positive, to guide lexicon revisions
Optionally, --recode SHEET compares two codings of the same bills (e.g. your
re-code of a subset two weeks later) and reports Cohen's kappa.

Usage:
    python evaluate.py coding/coding_sheet.csv coding/sample_key.csv
    python evaluate.py coding/coding_sheet.csv coding/sample_key.csv --recode coding/recode.csv
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
LABELS = ["direct", "indirect", "none"]


def split_tags(s):
    return {t.strip().lower() for t in str(s or "").replace(",", ";").split(";") if t.strip()}


def load(sheet_path, key_path):
    sheet = pd.read_csv(sheet_path, dtype=str).fillna("")
    key = pd.read_csv(key_path, dtype=str).fillna("")
    sheet["relevance"] = sheet["relevance"].str.strip().str.lower()
    coded = sheet[sheet["relevance"] != ""]
    bad = coded[~coded["relevance"].isin(LABELS)]
    if len(bad):
        raise SystemExit(f"relevance must be one of {LABELS}; bad rows: {bad['row'].tolist()}")
    df = coded.merge(key, on=["row", "bill_id"], how="inner", validate="one_to_one")
    df["weight"] = df["weight"].astype(float)
    return df, len(sheet)


def prf(gold, pred, w):
    tp = (w * (gold & pred)).sum()
    fp = (w * (~gold & pred)).sum()
    fn = (w * (gold & ~pred)).sum()
    p = tp / (tp + fp) if tp + fp else np.nan
    r = tp / (tp + fn) if tp + fn else np.nan
    f = 2 * p * r / (p + r) if p and r and not np.isnan(p + r) else np.nan
    return p, r, f


def bootstrap(df, gold_fn, pred_fn, reps=2000, seed=158):
    rng = np.random.default_rng(seed)
    groups = [g for _, g in df.groupby("stratum")]
    stats = []
    for _ in range(reps):
        b = pd.concat([g.iloc[rng.integers(0, len(g), len(g))] for g in groups])
        stats.append(prf(gold_fn(b), pred_fn(b), b["weight"].to_numpy()))
    stats = np.array(stats, dtype=float)
    return np.nanpercentile(stats, [2.5, 97.5], axis=0)


def fmt(x):
    return "n/a" if x is None or np.isnan(x) else f"{x:.2f}"


def metric_table(df, reps):
    rows = []
    defs = {
        "Relevant (direct or indirect)": (lambda d: d["relevance"].isin(["direct", "indirect"]).to_numpy(),
                                          lambda d: d["pred_label"].isin(["direct", "indirect"]).to_numpy()),
        "Direct only": (lambda d: (d["relevance"] == "direct").to_numpy(),
                        lambda d: (d["pred_label"] == "direct").to_numpy()),
    }
    for name, (g, pr) in defs.items():
        raw = prf(g(df), pr(df), np.ones(len(df)))
        wtd = prf(g(df), pr(df), df["weight"].to_numpy())
        lo, hi = bootstrap(df, g, pr, reps)
        rows.append(f"| {name} | {fmt(raw[0])} | {fmt(raw[1])} | {fmt(raw[2])} | "
                    f"{fmt(wtd[0])} ({fmt(lo[0])}–{fmt(hi[0])}) | "
                    f"{fmt(wtd[1])} ({fmt(lo[1])}–{fmt(hi[1])}) | {fmt(wtd[2])} |")
    head = ("| Target | Precision (sample) | Recall (sample) | F1 (sample) | "
            "Precision (weighted, 95% CI) | Recall (weighted, 95% CI) | F1 (weighted) |\n"
            "|---|---|---|---|---|---|---|")
    return head + "\n" + "\n".join(rows)


def area_table(df):
    rel = df[df["relevance"].isin(["direct", "indirect"])]
    gold = rel["areas"].map(split_tags)
    pred = rel["pred_areas"].map(split_tags)
    areas = sorted(set().union(*gold, *pred)) if len(rel) else []
    lines = ["| Area | Coded | Predicted | Both | Precision | Recall |", "|---|---|---|---|---|---|"]
    for a in areas:
        g = gold.map(lambda s: a in s)
        p = pred.map(lambda s: a in s)
        both = (g & p).sum()
        lines.append(f"| {a} | {g.sum()} | {p.sum()} | {both} | "
                     f"{fmt(both / p.sum() if p.sum() else np.nan)} | "
                     f"{fmt(both / g.sum() if g.sum() else np.nan)} |")
    return "\n".join(lines)


def error_list(df, kind):
    gold_rel = df["relevance"].isin(["direct", "indirect"])
    pred_rel = df["pred_label"].isin(["direct", "indirect"])
    sel = df[gold_rel & ~pred_rel] if kind == "fn" else df[~gold_rel & pred_rel]
    if sel.empty:
        return "_None._"
    lines = ["| Bill | Coded | Predicted | Coded areas | Matched terms | Notes |", "|---|---|---|---|---|---|"]
    for r in sel.itertuples():
        lines.append(f"| [{r.measure or r.bill_id}]({r.url}) | {r.relevance} | {r.pred_label} | "
                     f"{r.areas} | {r.matched_terms[:150]} | {r.notes[:150]} |")
    return "\n".join(lines)


def confusion_md(conf):
    lines = ["| coded \\ predicted | " + " | ".join(LABELS) + " |", "|---" * (len(LABELS) + 1) + "|"]
    for label in LABELS:
        lines.append(f"| {label} | " + " | ".join(str(conf.loc[label, c]) for c in LABELS) + " |")
    return "\n".join(lines)


def kappa(a, b):
    a, b = pd.Series(a).reset_index(drop=True), pd.Series(b).reset_index(drop=True)
    po = (a == b).mean()
    pe = sum((a == l).mean() * (b == l).mean() for l in LABELS)
    return (po - pe) / (1 - pe) if pe < 1 else np.nan


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("sheet")
    p.add_argument("key")
    p.add_argument("--recode", help="a second coding of some of the same rows")
    p.add_argument("--reps", type=int, default=2000, help="bootstrap replications")
    p.add_argument("-o", "--output", default=HERE / "results" / "evaluation.md")
    args = p.parse_args()

    df, n_sheet = load(args.sheet, args.key)
    conf = pd.crosstab(df["relevance"], df["pred_label"]).reindex(index=LABELS, columns=LABELS, fill_value=0)

    parts = [
        "# Flagging tool vs. hand-coded gold standard", "",
        f"{len(df)} of {n_sheet} sampled bills coded. Weighted figures scale each stratum "
        "back to its full size, so they estimate performance on all bills, not just the sample.", "",
        "## Precision and recall", "", metric_table(df, args.reps), "",
        "## Confusion table (counts in sample)", "", confusion_md(conf), "",
        "## Impact areas (among bills coded relevant)", "", area_table(df), "",
        "## Missed: coded relevant, predicted none", "", error_list(df, "fn"), "",
        "## False alarms: coded none, predicted relevant", "", error_list(df, "fp"), "",
    ]
    if args.recode:
        rc = pd.read_csv(args.recode, dtype=str).fillna("")
        rc["relevance"] = rc["relevance"].str.strip().str.lower()
        both = df.merge(rc[rc["relevance"] != ""], on="bill_id", suffixes=("", "_2"))
        parts += ["## Intra-coder reliability", "",
                  f"{len(both)} bills coded twice; agreement "
                  f"{(both['relevance'] == both['relevance_2']).mean():.2f}, "
                  f"Cohen's kappa {fmt(kappa(both['relevance'], both['relevance_2']))}.", ""]

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"report -> {out}")
    print(metric_table(df, args.reps))


if __name__ == "__main__":
    main()
