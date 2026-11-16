import { getBills, getNews } from "@/lib/data";
import { AREA_NAMES, fmtDate } from "@/lib/labels";

export const metadata = { title: "News · California DV Law Index" };

export default function NewsPage() {
  const news = getNews();
  const byMeasure = Object.fromEntries(getBills().map((b) => [b.m, b]));
  return (
    <div className="panel">
      <section style={{ display: "grid", gap: 12 }} aria-labelledby="news-h">
        <h2 id="news-h">In the news</h2>
        <p style={{ color: "var(--muted)", maxWidth: "70ch" }}>
          Headlines about California domestic violence law, collected each morning from news feeds and kept only when
          the same term list that flags bills finds them relevant. Each links to the original story. When a story names a
          bill in the index, the bill is linked too.
        </p>
        {news.length ? (
          <div className="news-list">
            {news.map((n) => (
              <article key={n.link} className="news">
                <a className="headline" href={n.link} target="_blank" rel="noopener">{n.title}</a>
                <div className="news-meta">
                  <span>{n.source}</span>
                  <span>{fmtDate(n.published)}</span>
                  <span className={`pill ${n.label}`}>{n.label}</span>
                  {n.bills.map((m) => byMeasure[m]
                    ? <a key={m} className="measure" href={byMeasure[m].u} target="_blank" rel="noopener">{m}</a>
                    : <span key={m} className="measure">{m}</span>)}
                  {n.areas.slice(0, 3).map((a) => <span key={a} className="tag">{AREA_NAMES[a] || a}</span>)}
                </div>
              </article>
            ))}
          </div>
        ) : (
          <p className="empty-box">
            No headlines yet. They appear after the first scheduled run, which reads the feeds listed in
            web/data/news_sources.json.
          </p>
        )}
      </section>
    </div>
  );
}
