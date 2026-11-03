"""Flag California bills (or statutes) that are directly about domestic violence
or that materially affect DV survivors, using the editable lexicon in
lexicon.csv.

Rules (see CODEBOOK.md for the human coding rules these approximate):
    DIRECT    the summed weight of distinct `direct` terms is >= --direct-threshold (default 3)
    INDIRECT  not DIRECT, and either an `area_strong` term matches, or at least
              one `area` term matches AND the summed weight of anchors (`anchor`
              terms plus any `direct` terms) is >= --anchor-threshold (default 2)
    NONE      otherwise
Impact areas are every area whose terms matched. Population tags are reported
but do not change the label. Phrases of kind `exclude` are deleted from the
text before matching.

Input: any CSV with an id column (default bill_id) and one or more text
columns (default title, subject, digest), e.g. the output of fetch_bills.py.

Usage:
    python flag.py data/bills_2025.csv                 # writes data/flags_2025.csv
    python flag.py in.csv -o out.csv --text-cols title digest full_text
"""

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
DEFAULT_LEXICON = HERE / "lexicon.csv"
KINDS = {"direct", "anchor", "area", "area_strong", "population", "exclude"}


@dataclass
class Term:
    term: str
    kind: str
    area: str
    weight: float
    pattern: re.Pattern


def compile_term(term):
    """`re:...` is a raw regex; a trailing * is a word-ending wildcard; anything
    else is a literal phrase matched on word boundaries, case-insensitively,
    with any run of whitespace allowed between words."""
    if term.startswith("re:"):
        body = term[3:]
    else:
        wildcard = term.endswith("*")
        words = term.rstrip("*").split()
        body = r"\s+".join(re.escape(w) for w in words)
        body = r"\b" + body + (r"[\w'-]*" if wildcard else r"\b")
    return re.compile(body, re.IGNORECASE)


def load_lexicon(path=DEFAULT_LEXICON):
    terms = []
    with open(path, newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            term = (row.get("term") or "").strip()
            if not term or term.startswith("#"):
                continue
            kind = (row.get("kind") or "").strip()
            if kind not in KINDS:
                raise ValueError(f"{path}:{i}: unknown kind {kind!r} for term {term!r}")
            terms.append(Term(term, kind, (row.get("area") or "").strip(),
                              float(row.get("weight") or 1), compile_term(term)))
    return terms


def classify(text, lexicon, direct_threshold=3.0, anchor_threshold=2.0):
    """Return a dict with the predicted label, scores, areas and matched terms."""
    text = text or ""
    for t in lexicon:
        if t.kind == "exclude":
            text = t.pattern.sub(" ", text)

    hits = [t for t in lexicon if t.kind != "exclude" and t.pattern.search(text)]
    direct = [t for t in hits if t.kind == "direct"]
    anchors = [t for t in hits if t.kind in ("anchor", "direct")]
    areas_weak = [t for t in hits if t.kind == "area"]
    areas_strong = [t for t in hits if t.kind == "area_strong"]

    direct_score = sum(t.weight for t in direct)
    if direct_score >= direct_threshold:
        label = "direct"
    elif areas_strong or (areas_weak and sum(t.weight for t in anchors) >= anchor_threshold):
        label = "indirect"
    else:
        label = "none"

    areas = sorted({t.area for t in hits
                    if t.area and t.kind in ("direct", "area", "area_strong")})
    populations = sorted({t.area for t in hits if t.kind == "population"})
    score = sum(t.weight for t in hits if t.kind != "population")
    return {
        "pred_label": label,
        "score": score,
        "direct_score": direct_score,
        "pred_areas": ";".join(areas) if label != "none" else "",
        "populations": ";".join(populations),
        "matched_terms": "; ".join(f"{t.term} [{t.kind}]" for t in hits),
    }


def flag_frame(df, lexicon, text_cols, direct_threshold=3.0, anchor_threshold=2.0):
    present = [c for c in text_cols if c in df.columns]
    if not present:
        raise ValueError(f"none of the text columns {text_cols} are in the input")
    text = df[present].fillna("").astype(str).agg("\n".join, axis=1)
    results = pd.DataFrame([classify(t, lexicon, direct_threshold, anchor_threshold) for t in text],
                           index=df.index)
    return pd.concat([df, results], axis=1)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input")
    p.add_argument("-o", "--output", help="default: input name with bills_ -> flags_")
    p.add_argument("--lexicon", default=DEFAULT_LEXICON)
    p.add_argument("--text-cols", nargs="+", default=["title", "subject", "digest"])
    p.add_argument("--direct-threshold", type=float, default=3.0)
    p.add_argument("--anchor-threshold", type=float, default=2.0)
    args = p.parse_args()

    inp = Path(args.input)
    out = Path(args.output) if args.output else inp.with_name(
        inp.name.replace("bills_", "flags_") if "bills_" in inp.name else "flags_" + inp.name)
    try:
        df = pd.read_csv(inp, dtype=str)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame()
    if df.empty:
        out.write_text("bill_id,pred_label,score\n")
        print(f"no rows in {inp}; wrote empty {out}")
        return
    flagged = flag_frame(df, load_lexicon(args.lexicon), args.text_cols,
                         args.direct_threshold, args.anchor_threshold)
    flagged.sort_values("score", ascending=False).to_csv(out, index=False)
    counts = flagged["pred_label"].value_counts()
    print(f"{len(flagged)} rows -> {out}")
    for label in ("direct", "indirect", "none"):
        print(f"  {label:9s} {counts.get(label, 0)}")


if __name__ == "__main__":
    main()
