import "./globals.css";
import Nav from "@/components/Nav";
import { getMeta } from "@/lib/data";
import { fmtDate } from "@/lib/labels";

export const metadata = {
  title: "California DV Law Index",
  description:
    "California bills that are about domestic violence, or that change what survivors can get, updated every morning from the Legislature's data.",
};

export default function RootLayout({ children }) {
  const meta = getMeta();
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,500;6..72,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap"
        />
      </head>
      <body>
        <div className="wrap">
          <header>
            <p className="eyebrow">
              California Legislature · {meta.current_session || ""} session · updated {fmtDate(meta.updated)}
            </p>
            <h1>California DV Law Index</h1>
            <p className="lede">
              Laws that are about domestic violence, and laws that never say so but still change what survivors can
              get: housing, immigration status, custody, firearms, benefits, courts and privacy.
            </p>
          </header>
          <Nav />
          {children}
          <footer>
            Rebuilt every morning from the California Legislature&apos;s public bulk data and news feeds. Last full
            refresh {fmtDate(meta.last_full_refresh)}. POLISCI 158 final project.
          </footer>
        </div>
      </body>
    </html>
  );
}
