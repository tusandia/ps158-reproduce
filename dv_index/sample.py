"""Draw a stratified sample of flagged bills for hand-coding (the gold standard).

Recall can only be measured if the sample includes bills the tool did NOT flag,
so the sample is stratified on the predicted label (direct / indirect / none),
and each row carries a weight (stratum size / sample size) that evaluate.py
uses to estimate population-level precision and recall.

Two files are written:
    coding/coding_sheet.csv   what you code: shuffled, with NO predictions, so
                              coding is blind to the tool. Fill in `relevance`,
                              `areas`, `populations`, `notes`.
    coding/sample_key.csv     predictions, strata and weights (don't look at
                              this while coding).

Usage:
    python sample.py data/flags_2025.csv --n-direct 60 --n-indirect 80 --n-none 160
"""

import argparse
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
SHEET_COLS = ["row", "bill_id", "measure", "title", "subject", "digest", "url"]
CODE_COLS = ["relevance", "areas", "populations", "notes"]


def stratified_sample(flags, sizes, seed=158):
    parts = []
    for label, n in sizes.items():
        stratum = flags[flags["pred_label"] == label]
        take = min(n, len(stratum))
        s = stratum.sample(n=take, random_state=seed).copy()
        s["stratum"] = label
        s["stratum_size"] = len(stratum)
        s["weight"] = len(stratum) / take if take else 0.0
        parts.append(s)
    sample = pd.concat(parts).sample(frac=1, random_state=seed).reset_index(drop=True)
    sample.insert(0, "row", range(1, len(sample) + 1))
    return sample


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("flags")
    p.add_argument("--n-direct", type=int, default=60)
    p.add_argument("--n-indirect", type=int, default=80)
    p.add_argument("--n-none", type=int, default=160)
    p.add_argument("--seed", type=int, default=158)
    p.add_argument("--outdir", default=HERE / "coding")
    args = p.parse_args()

    flags = pd.read_csv(args.flags, dtype=str)
    sample = stratified_sample(flags, {"direct": args.n_direct, "indirect": args.n_indirect,
                                       "none": args.n_none}, args.seed)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    sheet = sample.reindex(columns=SHEET_COLS)
    for c in CODE_COLS:
        sheet[c] = ""
    sheet_path, key_path = outdir / "coding_sheet.csv", outdir / "sample_key.csv"
    for path in (sheet_path, key_path):
        if path.exists():
            raise SystemExit(f"{path} exists; move it first so finished coding isn't overwritten")
    sheet.to_csv(sheet_path, index=False)
    sample[["row", "bill_id", "stratum", "stratum_size", "weight", "pred_label",
            "pred_areas", "score", "matched_terms"]].to_csv(key_path, index=False)
    print(f"{len(sample)} bills to code -> {sheet_path}")
    print(sample.groupby("stratum")[["stratum_size"]].first().assign(
        sampled=sample["stratum"].value_counts()))


if __name__ == "__main__":
    main()
