"use client";

import { useState } from "react";
import { AREA_NAMES, ID_NAME } from "@/lib/labels";

const KIND_NAMES = {
  direct: "Direct", anchor: "Victim or safety", area: "Impact area", area_strong: "Impact area (strong)",
  population: "Who it reaches",
};

export default function TermTable({ terms }) {
  const [q, setQ] = useState("");
  const needle = q.toLowerCase();
  const rows = terms.filter((t) => !needle ||
    `${t.term} ${t.kind} ${KIND_NAMES[t.kind]} ${t.area} ${ID_NAME[t.area] || ""} ${AREA_NAMES[t.area] || ""} ${t.note}`
      .toLowerCase().includes(needle));
  return (
    <section className="terms" aria-labelledby="terms-h">
      <h2 id="terms-h">Term list</h2>
      <p style={{ color: "var(--muted)" }}>
        The words and code citations the tool matches. A term ending in * matches any ending. &quot;Code section
        citation&quot; rows are patterns that match citations such as Family Code §6211.
      </p>
      <div className="terms-head">
        <input type="search" aria-label="Search terms" placeholder="Search terms, kinds or areas" autoComplete="off"
          value={q} onChange={(e) => setQ(e.target.value)} />
        <span className="count">{rows.length} of {terms.length} terms</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Term</th><th>Kind</th><th>Area or group</th><th>Note</th></tr></thead>
          <tbody>
            {rows.map((t, i) => (
              <tr key={i}>
                <td>{t.term.startsWith("re:") ? "code section citation" : t.term}</td>
                <td><span className="kind">{KIND_NAMES[t.kind] || t.kind}</span></td>
                <td>{ID_NAME[t.area] || AREA_NAMES[t.area] || t.area}</td>
                <td>{t.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
