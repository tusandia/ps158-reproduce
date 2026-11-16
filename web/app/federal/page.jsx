import { getFederal } from "@/lib/data";

export const metadata = { title: "Federal law · California DV Law Index" };

export default function FederalPage() {
  const fed = getFederal();
  const topics = [...new Set(fed.map((r) => r.womenslaw_topic))];
  const yes = (t) => fed.filter((r) => r.womenslaw_topic === t && r.dv_specific === "yes").length;
  topics.sort((a, b) => yes(b) - yes(a));
  return (
    <div className="panel">
      <section className="federal" aria-labelledby="fed-h">
        <h2 id="fed-h">The federal layer</h2>
        <p>
          Federal law sets a floor that California builds on. These are the federal statutes and regulations WomensLaw
          selects for survivors. They aren&apos;t in the index of California bills, but many state bills only make
          sense next to them. Not all are about DV: each is marked <span className="dv yes">yes</span> if it is about
          DV, <span className="dv partly">partly</span> if it is a general law with a DV provision, or{" "}
          <span className="dv no">no</span> if it is listed for context.
        </p>
        <div className="fed-groups">
          {topics.map((t) => {
            const rows = fed.filter((r) => r.womenslaw_topic === t);
            const c = (k) => rows.filter((r) => r.dv_specific === k).length;
            return (
              <details key={t}>
                <summary>
                  <b>{t}</b>
                  <span className="fed-counts">{rows.length} · {c("yes")} DV · {c("partly")} partly · {c("no")} context</span>
                </summary>
                {rows.map((r) => (
                  <div key={r.citation} className="fed-row">
                    <span className={`dv ${r.dv_specific}`}>{r.dv_specific}</span>
                    <span><span className="fed-cit">{r.citation}</span><br />{r.title}</span>
                    <span className="fed-note">{r.note}</span>
                  </div>
                ))}
              </details>
            );
          })}
        </div>
        <p>
          Source: WomensLaw.org (National Network to End Domestic Violence), <i>Selected Federal Statutes</i>, updated
          December 17, 2025, and its federal pages on VAWA housing protections, federal gun laws and domestic violence in
          the military.
        </p>
      </section>
    </div>
  );
}
