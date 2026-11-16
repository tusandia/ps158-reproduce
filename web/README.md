# California DV Law Index: self-updating website

A Next.js site that rebuilds itself every morning from the California
Legislature's public data and from news feeds.

```
8:00 a.m. Pacific, every day (GitHub Actions: .github/workflows/daily-update.yml)
  │
  ├─ dv_index/update.py   reads this week's change files from downloads.leginfo.legislature.ca.gov,
  │                       re-flags any bill with a new version, logs NEW / UPDATED / REMOVED
  │                       (Sundays: rebuilds from the whole session file)
  ├─ dv_index/news.py     reads the feeds in web/data/news_sources.json, keeps DV-related headlines
  ├─ git commit web/data  only if something changed
  └─ next build → GitHub Pages
```

## Pages

| Page | Shows |
|---|---|
| `/` California bills | counts, latest changes, identity buttons (combinable), impact areas, searchable bill list, session gaps |
| `/federal/` | the WomensLaw federal statute list, marked DV / partly / context |
| `/news/` | headlines from the feeds, linked to bills in the index when a story names one |
| `/codebook/` | `dv_index/CODEBOOK.md` and the searchable term list |

All data is in `web/data/*.json`, written by the Python scripts. The site has
no server or database: `next build` bakes the JSON into static pages in `web/out/`.

## One-time setup on GitHub

1. **Put this on the default branch.** Scheduled workflows only run on the
   repository's default branch. Merge this branch into it, or make this branch
   the default in Settings → General → Default branch.
2. **Turn on GitHub Pages.** Settings → Pages → Build and deployment → Source:
   **GitHub Actions**. (Pages on a private repository needs GitHub Pro, which is
   free for students through GitHub Education. Otherwise make the repository
   public, or use Vercel below.)
3. **Allow the workflow to push.** Settings → Actions → General → Workflow
   permissions: **Read and write permissions**.
4. **Run it once by hand.** Actions → "Daily update and deploy" → Run workflow.
   The site appears at `https://<your-username>.github.io/<repo-name>/`.

### Using Vercel instead of GitHub Pages

Import the repository at vercel.com, set the root directory to `web`, and leave
the build settings as they are. Vercel rebuilds on every push, including the
bot's daily data commit. Then delete the `deploy` job from the workflow so the
site isn't deployed twice.

## Working on it locally

```bash
cd web
npm install
npm run dev
```

Open http://localhost:3000. To refresh the data first:

```bash
cd dv_index
python update.py          # this week's changes
python update.py --full   # whole session (downloads about 1.2 GB)
python news.py
```

## Changing what it tracks

- **Words and citations:** edit `dv_index/lexicon.csv`, then run
  `python update.py --full` so every bill is re-scored.
- **News feeds:** edit `web/data/news_sources.json`. Any RSS or Atom feed
  works. Only headlines, links, sources and dates are stored.
- **Coding rules:** edit `dv_index/CODEBOOK.md`; the Codebook page updates on
  the next build.

## Notes

- The schedule has two UTC times because California switches between PDT and
  PST. The workflow keeps whichever matches 8 a.m. that day. GitHub sometimes
  starts scheduled runs late when it's busy.
- The data files change every day (at least the "updated" date), so expect one
  small bot commit per morning.
- The site only uses sources that allow automated access: the Legislature's
  bulk downloads and public RSS feeds. Sites behind bot checks (WomensLaw, the
  ABA) are added by hand, as with `dv_index/reference/`.
