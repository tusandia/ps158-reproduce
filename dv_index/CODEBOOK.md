# Coding scheme: California laws and DV survivors

Unit of analysis: one bill (latest version), or one code section. Code every
item from its title, Legislative Counsel's Digest and, if still unclear, the
bill text. Code **what the law does**, not what its author says it is for.

## 1. `relevance` (pick one)

| Code | Rule | Examples |
|---|---|---|
| `direct` | The law names domestic violence, intimate partner / dating violence or family violence, or amends a provision whose only or main subject is DV (e.g. the Domestic Violence Prevention Act, Fam. Code §6200 et seq.; Pen. Code §273.5; DV restraining orders; batterer intervention programs). | DVRO procedure; DV shelter funding; coercive control as abuse. |
| `indirect` | The law does not need to mention DV, but it **materially changes what a survivor can get or what risks they face** in at least one impact area below, *and* survivors are a group it clearly reaches more than incidentally. | Expanding eligibility for U-visa certifications; lease termination rights for crime victims; firearm relinquishment procedures; court interpreter access in family court; address confidentiality; services offered regardless of immigration status; rules on service of process or ex parte divorce; jurisdiction in custody cases that cross state or national borders; funding for culturally specific organizations. |
| `none` | Neither. A passing mention of "victims" in a broad bill does not make it `indirect` unless the change would matter to a survivor's safety, housing, status, income, children or access to courts. | |

Tie-breakers:
- Bills covering several crimes (e.g. "victims of domestic violence, sexual assault, stalking or human trafficking") that name DV are `direct`.
- Elder / dependent adult abuse and child abuse alone are `indirect` only if they apply within a family or household relationship that would meet Fam. Code §6211; otherwise `none`.
- Spot bills or bills whose text is only intent language: code what the digest says the bill would do; add `spot bill` in `notes`.
- Abuse by in-laws or other family members counts as DV when the relationship meets Fam. Code §6211, which covers more than spouses. Transnational marriage abandonment is usually carried out by the husband *and* his family (Bhandari 2025).
- A law can hurt survivors. Code it `direct` or `indirect` all the same, and say in `notes` that the effect is harmful. Examples: a law that makes interpreters harder to get, or a law that lets an abuser use a protective order or a false abuse claim against the survivor.

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

## 2b. `abuse_forms` (any the law responds to, separated by `;`)

The kinds of abuse the law addresses. A law about restraining orders in general
gets `general`. The list follows the Learning Network's typology (Tabibi et al.
2018) plus two forms documented among South Asian women in the U.S.
(Bhandari 2025).

| Code | Covers |
|---|---|
| `general` | Abuse in general, with no form singled out. |
| `physical` | Hitting, choking or strangulation, withholding hormones or medication. |
| `sexual` | Sexual assault, reproductive coercion, forced abortion, refusal to use protection. |
| `psychological` | Isolation, threats, coercive control, threats to "out" a partner, harm to pets or service animals. |
| `economic` | Control of money or accounts, coerced debt, dowry demands, keeping a partner from working. |
| `technology` | Monitoring, tracking, stalkerware, intimate images, abuse through devices and social media. |
| `neglect` | Withholding food, care, medication or mobility aids. |
| `forced_marriage` | Forcing someone into marriage, or keeping them in one. |
| `immigration_related` | Threats about status or deportation, withholding or destroying passports and visas, refusing to file or withdrawing a sponsorship, keeping a partner from learning English. |
| `transnational_abandonment` | Leaving a spouse stranded abroad, cancelling her visa or tickets, locking her out after migration, serving divorce ex parte in another country (Bhandari 2025). |
| `child_related` | Using children to control: abduction, alienation, false abuse claims, fights over custody jurisdiction. |
| `faith_misuse` | Using religion or a faith leader to justify abuse or keep a survivor from leaving (Tabibi et al. 2018). |

## 3. `populations` (any that apply)

Survivors the law specifically reaches. Tag a realm only when the law itself
reaches that group; don't infer from who tends to use a program.

| Code | Covers |
|---|---|
| `immigrant_vawa` | Immigration status, VAWA self-petitions, U/T visas, asylum, refugees, noncitizens, public charge. |
| `women_gender` | Women, gender, gender-based violence, pregnancy, reproductive health, forced or coerced marriage. |
| `faith` | Religion, places of worship, clergy, faith-based organizations, but only where faith changes something for survivors. Examples: shelters or services that meet religious and spiritual needs, religious discrimination in victim services, immigration enforcement at places of worship, and the role of faith leaders, who can help a survivor or side with the abuser (Bhandari 2025). A passing mention in a list of protected traits doesn't count. |
| `language_access` | Interpreters, translation, limited English proficiency. In `notes`, name any language the law lists. |
| `youth`, `elder_dependent_adult`, `disability`, `tribal`, `lgbtq`, `rural` | As named. |

No 2025–26 bill names a religion, ethnicity or South Asian language. Muslim and
South Asian survivors are therefore not separate codes. Their concerns are
tracked through the realms above and through `abuse_forms`.

**Caution against "culturalizing" violence.** Code what the law does, not
assumptions about a community. Violence against women happens in every
culture. Treating it as a product of one community's culture, rather than of
structural inequality, is itself a harm (Tabibi et al. 2018). A forced-marriage
law is `women_gender` and `forced_marriage`. It isn't tagged to any religion or
ethnicity. This is how the coding handles the main risk
named in the proposal: indirect laws that matter mostly to a specific group.

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
- Problems that cross borders. In transnational abandonment, the husband files
  in one country while the wife is in another, so no single state's law reaches
  the whole case (Bhandari 2025). Remedies sit mostly in federal immigration law
  (VAWA self-petitions, work permits for dependent-visa holders such as H-4) and
  in other countries' laws.
- Gaps. An index of what passed can't show what was never introduced. The
  2025–26 session has no bill that mentions dowry, transnational or marriage
  abandonment, immigration-related abuse, international child abduction or the
  Hague Convention, culturally specific services, or faith leaders. Report
  these absences as findings.

## Sources

- Bhandari, S. (2025). Experiences of transnational abandonment in the lives of
  abused South Asian women in the United States. *Journal of Family Violence*,
  40, 1079–1089. https://doi.org/10.1007/s10896-024-00683-2
- Tabibi, J., Ahmad, S., Baker, L., & Lalonde, D. (2018). *Intimate partner
  violence against immigrant and refugee women*. Learning Network Issue 26.
  Centre for Research & Education on Violence Against Women & Children, Western
  University. (A Canadian source; its barriers and recommendations were used to
  pick impact areas, not to describe California law.)
