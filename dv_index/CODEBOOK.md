# Coding scheme: California laws and DV survivors

Unit of analysis: one bill (latest version), or one code section. Code every
item from its title, Legislative Counsel's Digest and, if still unclear, the
bill text. Code **what the law does**, not what its author says it is for.

## 1. `relevance` (pick one)

| Code | Rule | Examples |
|---|---|---|
| `direct` | The law names domestic violence, intimate partner / dating violence or family violence, or amends a provision whose only or main subject is DV (e.g. the Domestic Violence Prevention Act, Fam. Code §6200 et seq.; Pen. Code §273.5; DV restraining orders; batterer intervention programs). | DVRO procedure; DV shelter funding; coercive control as abuse. |
| `indirect` | The law does not need to mention DV, but it **materially changes what a survivor can get or what risks they face** in at least one impact area below, *and* survivors are a group it clearly reaches more than incidentally. | Expanding eligibility for U-visa certifications; lease termination rights for crime victims; firearm relinquishment procedures; court interpreter access in family court; address confidentiality. |
| `none` | Neither. A passing mention of "victims" in a broad bill does not make it `indirect` unless the change would matter to a survivor's safety, housing, status, income, children or access to courts. | |

Tie-breakers:
- Bills covering several crimes (e.g. "victims of domestic violence, sexual assault, stalking or human trafficking") that name DV are `direct`.
- Elder / dependent adult abuse and child abuse alone are `indirect` only if they apply within a family or household relationship that would meet Fam. Code §6211; otherwise `none`.
- Spot bills or bills whose text is only intent language: code what the digest says the bill would do; add `spot bill` in `notes`.

## 2. `areas` (any that apply, separated by `;`)

Code every area the law *changes* for survivors. Use these exact codes so they
can be compared with the tool's predictions:

| Code | Covers |
|---|---|
| `immigration` | Immigration status, U/T visa certification, VAWA, cooperation with federal immigration enforcement, access to services regardless of status. |
| `housing` | Tenancy, eviction, lease termination, shelters, homelessness services, housing assistance. |
| `custody` | Custody, visitation, child support, dissolution, family court procedure. |
| `firearms` | Firearm and ammunition prohibitions, relinquishment, GVROs, APPS. |
| `benefits` | CalWORKs, CalFresh, Medi-Cal, unemployment, victim compensation, other cash or in-kind aid. |
| `language` | Interpreters, translation, language access. |
| `courts` | Protective orders, criminal procedure, evidence and privilege, legal aid, remote appearance, sentencing and diversion. |
| `privacy` | Address confidentiality (Safe at Home), personal data, tracking and stalkerware, records sealing. |
| `employment` | Leave, workplace protections, job-related accommodations. |
| `health` | Health care, mental health, reproductive health, forensic exams, mandated reporting by health workers. |
| `services` | Funding and rules for DV programs, hotlines, advocates (Cal OES etc.). |
| `child_welfare` | Child welfare, dependency, foster care, juvenile court. |
| `education` | Schools, campuses, Title IX. |
| `financial` | Coerced debt, economic abuse, credit, banking. |

Add a new code only if none fits; record it in `notes` and add matching terms
to `lexicon.csv` afterwards.

## 3. `populations` (any that apply)

Groups the law specifically reaches: `immigrant`, `rural`, `disability`,
`tribal`, `lgbtq`, `youth`, `elder_dependent_adult`, `language_minority`.
This is how the coding tracks the main risk named in the proposal: indirect
laws that matter mostly to a specific group.

## 4. `notes`

One line: why it is `indirect` (what changes for survivors), or why a close
call went to `none`. These notes are what you'll use to revise the lexicon.

## Procedure

1. Code blind: use `coding/coding_sheet.csv` only, never `sample_key.csv`.
2. After two weeks, re-code a random 15% of rows in a fresh copy of the sheet
   and run `evaluate.py --recode` for intra-coder agreement (Cohen's kappa).
3. Keep a log of rule changes; if a rule changes, re-check rows already coded.

## What the index can't capture

- Federal law and policy (e.g. expedited removal, enforcement priorities).
  These change what Californians can use but never show up as California bills.
- County and city ordinances, court rules (Judicial Council), and agency regulations.
- Laws whose effect on survivors depends on implementation or funding, not text.
- Bills where DV relevance is only clear from committee analyses or advocates'
  positions, not from the digest or text.
