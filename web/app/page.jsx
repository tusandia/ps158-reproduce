import CaliforniaExplorer from "@/components/CaliforniaExplorer";
import { getBills, getGaps, getMeta, getRelated, getUpdates } from "@/lib/data";
import { fmtDate } from "@/lib/labels";

export default function CaliforniaPage() {
  const meta = getMeta();
  const bills = getBills();
  const updates = getUpdates().slice(0, 15);
  const gaps = getGaps();
  return (
    <div className="panel">
      <section style={{ display: "grid", gap: 14 }}>
        <div className="tally">
          {[
            [(meta.total || 0).toLocaleString("en-US"), "bills read"],
            [bills.length, "flagged as relevant"],
            [meta.direct ?? bills.filter((b) => b.l === "direct").length, "direct"],
            [bills.length - (meta.direct ?? 0), "indirect"],
            [meta.became_law ?? 0, "became law"],
          ].map(([n, t]) => <div key={t}><b>{n}</b><span>{t}</span></div>)}
        </div>
        <p className="define">
          <b>Flagged</b> means the tool picked a bill out as likely to matter to DV survivors. <b>Direct</b> bills name
          domestic, dating or family violence, or change a DV law. <b>Indirect</b> bills don&apos;t say &quot;domestic
          violence&quot; but change something survivors rely on, such as housing, immigration status, custody, guns or
          benefits, and use victim or safety language.
        </p>
        <p className="notice">
          These labels are predictions from a keyword-and-theme tool, not yet checked against hand coding. Read the bill
          before relying on a label.
        </p>
      </section>

      <section style={{ display: "grid", gap: 12 }} aria-labelledby="upd-h">
        <h2 id="upd-h">Latest changes</h2>
        {updates.length ? (
          <div className="updates">
            {updates.map((u, i) => (
              <div key={i} className="upd">
                <span className="upd-date">{fmtDate(u.date)}</span>
                <span className={`chg ${u.change}`}>{u.change.toLowerCase()}</span>
                <span className="measure"><a href={u.u} target="_blank" rel="noopener">{u.m}</a></span>
                <span>{u.s}{u.v ? ` (${u.v})` : ""}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="empty-box">
            No changes yet. Each morning the site checks the Legislature&apos;s change files and lists bills that were
            newly flagged, amended or passed here.
          </p>
        )}
      </section>

      <CaliforniaExplorer bills={bills} related={getRelated()} />

      <section className="gaps" aria-labelledby="gaps-h">
        <h2 id="gaps-h">What the session didn&apos;t address</h2>
        <p>
          Research on immigrant and South Asian survivors documents these problems. The number is how many of the
          session&apos;s bills mention each one, flagged or not.
        </p>
        <div className="gap-list">
          {gaps.map((g) => (
            <div key={g.issue} className="gap">
              <span className={`gap-n ${g.n === 0 ? "zero" : ""}`}>{g.n}</span>
              <span>{g.issue}</span>
              <span className="gap-src">{g.src}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="method" aria-labelledby="method-h">
        <h2 id="method-h">How bills are flagged</h2>
        <div className="method-grid">
          <div><h3>Source</h3><p>The Legislature&apos;s official bulk data (downloads.leginfo.legislature.ca.gov). For each AB and SB bill, the tool reads the latest version&apos;s title, subject and Legislative Counsel&apos;s Digest.</p></div>
          <div><h3>Direct</h3><p>The bill names domestic, intimate partner, dating or family violence, or cites a section of the Domestic Violence Prevention Act (Family Code §§6200–6409).</p></div>
          <div><h3>Indirect</h3><p>The bill touches an impact area (housing, immigration, custody, firearms and so on) and uses victim or safety language. Some citations count on their own, such as Civil Code §1946.7, which lets victims end a lease.</p></div>
          <div><h3>Updates</h3><p>Every morning the site reads the day&apos;s change files and re-flags any bill with a new version. Once a week it rebuilds from the full session file.</p></div>
        </div>
      </section>
    </div>
  );
}
