"use client";

import { useMemo, useState } from "react";
import { AREA_NAMES, ICONS, IDS, ID_NAME, fmtDate } from "@/lib/labels";

const STAGES = ["Introduced", "Amended", "Enrolled", "Chaptered"];
const stageOf = (v) => (v === "Chaptered" ? 4 : v === "Enrolled" ? 3 : v.startsWith("Amended") ? 2 : 1);
const hasIds = (b, ids) => [...ids].every((i) => b.p.includes(i));

function IdentityPicker({ bills, ids, toggle, related }) {
  const sel = IDS.filter((i) => ids.has(i.id));
  const n = bills.filter((b) => hasIds(b, ids)).length;
  const rel = sel.length === 1 ? related[sel[0].id] || [] : [];
  const url = (m) => bills.find((b) => b.m === m)?.u;
  return (
    <section className="ids" aria-labelledby="ids-h">
      <h2 id="ids-h">Who a law reaches</h2>
      <p>
        Pick one identity, or several to see laws that reach all of them at once. A bill counts only when its own
        text uses that group&apos;s language, so some groups are small. The number on each button is how many bills
        you would see if you added it.
      </p>
      <p>
        No bill this session names a religion, an ethnicity or a South Asian language, so bills can&apos;t be sorted
        by community. For Muslim and South Asian survivors, advocates most often raise immigration and VAWA, language
        access, faith, and forced marriage (under Woman). None of these is unique to those communities.
      </p>
      <div className="id-grid">
        {IDS.map((i) => {
          const on = ids.has(i.id);
          const next = new Set(ids).add(i.id);
          const count = bills.filter((b) => hasIds(b, next)).length;
          return (
            <button key={i.id} type="button" className="id-btn" aria-pressed={on} disabled={!on && count === 0}
              aria-label={`${i.long}: ${count} bills`} onClick={() => toggle(i.id)}>
              <svg viewBox="0 0 24 24" aria-hidden="true" dangerouslySetInnerHTML={{ __html: ICONS[i.id] }} />
              <span className="id-name">{i.name}</span>
              <span className="id-n">{count}</span>
            </button>
          );
        })}
      </div>
      {sel.length > 0 && (
        <div className="id-summary">
          <h3>{sel.map((i) => i.long).join(" + ")}: {n} bill{n === 1 ? "" : "s"}</h3>
          {sel.map((i) => (
            <p key={i.id}>
              <b>{i.name}</b> covers {i.def.charAt(0).toLowerCase() + i.def.slice(1)}{" "}
              {i.note && <span className="note">{i.note}</span>}
            </p>
          ))}
          {rel.length > 0 && (
            <>
              <p><b>Worth a look, not in the index:</b></p>
              {rel.map((r) => (
                <p key={r.m}>
                  <span className="measure">{url(r.m) ? <a href={url(r.m)} target="_blank" rel="noopener">{r.m}</a> : r.m}</span>{" "}
                  {r.note}
                </p>
              ))}
            </>
          )}
          <p><a href="#bills">See the bills ↓</a></p>
        </div>
      )}
    </section>
  );
}

function AreaBars({ bills, area, setArea }) {
  const rows = useMemo(() => {
    const c = {};
    bills.forEach((b) => b.a.forEach((a) => {
      c[a] = c[a] || { d: 0, n: 0 };
      c[a][b.l === "direct" ? "d" : "n"]++;
    }));
    return Object.entries(c).sort((x, y) => y[1].d + y[1].n - (x[1].d + x[1].n));
  }, [bills]);
  const max = Math.max(1, ...rows.map(([, c]) => c.d + c.n));
  return (
    <section className="areas" aria-labelledby="areas-h">
      <div className="areas-head">
        <h2 id="areas-h">Impact areas</h2>
        <div className="legend">
          <span><i style={{ background: "var(--accent)" }} />Direct</span>
          <span><i style={{ background: "var(--indirect)" }} />Indirect</span>
          <span>Select an area to filter</span>
        </div>
      </div>
      <div className="bars">
        {rows.map(([a, c]) => {
          const t = c.d + c.n;
          return (
            <button key={a} type="button" className="bar" aria-pressed={area === a} title={`${c.d} direct, ${c.n} indirect`}
              onClick={() => setArea(area === a ? null : a)}>
              <span className="bar-name">{AREA_NAMES[a] || a}</span>
              <span className="bar-track" style={{ width: `${((t / max) * 100).toFixed(1)}%` }}>
                <i className="d" style={{ width: `${(c.d / t) * 100}%` }} />
                <i className="n" style={{ width: `${(c.n / t) * 100}%` }} />
              </span>
              <span className="bar-num">{t}</span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

function Bill({ b }) {
  const st = stageOf(b.v);
  const law = b.v === "Chaptered";
  return (
    <article className="bill">
      <div className="bill-top">
        <span className="measure"><a href={b.u} target="_blank" rel="noopener">{b.m}</a></span>
        <span className={`pill ${b.l}`}>{b.l}</span>
        <span className="subject">{b.s || b.t}</span>
      </div>
      <div className="bill-meta">
        <span className={`stage ${law ? "law" : ""}`} title={STAGES.slice(0, st).join(" → ")}>
          <span className="stage-track">{STAGES.map((_, i) => <i key={i} className={i < st ? "on" : ""} />)}</span>
          <span className="stage-label">{law ? "Became law" : `Last version: ${b.v}`}</span>
        </span>
        <span>{fmtDate(b.d)}</span>
        {b.session && <span>{b.session}</span>}
      </div>
      <div className="tags">
        {b.a.map((a) => <span key={a} className="tag">{AREA_NAMES[a] || a}</span>)}
        {b.p.map((p) => <span key={p} className="tag pop">{ID_NAME[p] || p}</span>)}
      </div>
      <details>
        <summary>Summary and why it was flagged</summary>
        <p className="digest">{b.x}</p>
        <p className="title-line">{b.t}</p>
        <p className="why">Matched: {b.k.map((k) => <code key={k}>{k}</code>)}</p>
        {Object.keys(b.rs || {}).length > 0 && (
          <div className="where">
            {Object.entries(b.rs).map(([r, t]) => <p key={r}><b>{ID_NAME[r] || r}:</b> <span>{t}</span></p>)}
          </div>
        )}
      </details>
    </article>
  );
}

export default function CaliforniaExplorer({ bills, related }) {
  const [q, setQ] = useState("");
  const [label, setLabel] = useState("all");
  const [status, setStatus] = useState("all");
  const [sort, setSort] = useState("score");
  const [area, setArea] = useState(null);
  const [ids, setIds] = useState(() => new Set());

  const toggle = (id) => setIds((s) => {
    const n = new Set(s);
    n.has(id) ? n.delete(id) : n.add(id);
    return n;
  });
  const clear = () => { setQ(""); setLabel("all"); setStatus("all"); setArea(null); setIds(new Set()); };

  const rows = useMemo(() => {
    const words = q.toLowerCase().split(/\s+/).filter(Boolean);
    const out = bills.filter((b) => {
      if (label !== "all" && b.l !== label) return false;
      if (status === "law" && b.v !== "Chaptered") return false;
      if (status === "not" && b.v === "Chaptered") return false;
      if (!hasIds(b, ids)) return false;
      if (area && !b.a.includes(area)) return false;
      if (words.length) {
        const hay = `${b.m} ${b.m.replace(" ", "")} ${b.s} ${b.t} ${b.x}`.toLowerCase();
        if (!words.every((w) => hay.includes(w))) return false;
      }
      return true;
    });
    const num = (m) => { const [k, n] = m.split(" "); return [k, +n]; };
    return out.sort(sort === "date" ? (a, b) => b.d.localeCompare(a.d)
      : sort === "measure" ? (a, b) => { const [ka, na] = num(a.m), [kb, nb] = num(b.m); return ka.localeCompare(kb) || na - nb; }
      : (a, b) => (a.l === b.l ? 0 : a.l === "direct" ? -1 : 1) || b.sc - a.sc);
  }, [bills, q, label, status, sort, area, ids]);

  const filtered = q || label !== "all" || status !== "all" || ids.size || area;
  return (
    <>
      <IdentityPicker bills={bills} ids={ids} toggle={toggle} related={related} />
      <AreaBars bills={bills} area={area} setArea={setArea} />
      <section aria-label="Bills" id="bills">
        <div className="filters">
          <input type="search" aria-label="Search bills" placeholder="Search bill number, subject or summary"
            autoComplete="off" value={q} onChange={(e) => setQ(e.target.value)} />
          <div className="seg" role="group" aria-label="Relevance">
            {["all", "direct", "indirect"].map((v) => (
              <button key={v} type="button" aria-pressed={label === v} onClick={() => setLabel(v)}>
                {v[0].toUpperCase() + v.slice(1)}
              </button>
            ))}
          </div>
          <select aria-label="Status" value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="all">Any status</option>
            <option value="law">Became law</option>
            <option value="not">Did not become law</option>
          </select>
          <select aria-label="Sort" value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="score">Sort: strongest match</option>
            <option value="date">Sort: latest action</option>
            <option value="measure">Sort: bill number</option>
          </select>
          <span className="count">
            {rows.length} of {bills.length} bills
            {ids.size > 0 && ` reaching ${[...ids].map((i) => ID_NAME[i]).join(" + ")}`}
            {filtered ? <> · <button type="button" className="clear" onClick={clear}>Clear filters</button></> : null}
          </span>
        </div>
        <div className="list">
          {rows.length ? rows.map((b) => <Bill key={b.id || b.m} b={b} />)
            : <p className="empty">No flagged bills match these filters. Try fewer identities or clear the filters.</p>}
        </div>
      </section>
    </>
  );
}
