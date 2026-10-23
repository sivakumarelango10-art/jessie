# Jessie J. — Physiotherapist portfolio

A fast, dependency-free static website. No framework, no build step needed to deploy.

## Deploy (pick one)

Everything to upload is in `dist/site/`:

```
dist/site/
  index.html              the whole page (HTML, CSS and JS inlined)
  Jessie_Physiotherapist_Resume.pdf  public résumé (home address and date of birth removed)
  assets/jessie.webp      portrait, background removed
  assets/og.jpg           preview image for WhatsApp / LinkedIn link shares
```

- **Netlify:** drag the `dist/site` folder onto https://app.netlify.com/drop
- **GitHub Pages:** push the contents of `dist/site` to a repo, then Settings → Pages
- **Vercel:** import this repo at https://vercel.com/new. `vercel.json` already tells Vercel to serve `dist/site`
  with no build step, so keep the defaults and click Deploy. Every push to `main` redeploys automatically.
- **Cloudflare Pages:** create a project and set the output folder to `dist/site`

Because the site is served from `dist/site`, run `python3 build.py` and commit the result after editing anything in `src/`.

Preview locally: `cd dist/site && python3 -m http.server 8000`, then open http://localhost:8000

## Editing content

All text lives in `src/content.py`, page structure and illustrations in `src/markup.py` (experience, research, education, contact details).
Styles are in `src/styles.css`, interactions in `src/main.js`. After editing, rebuild:

```
python3 build.py
```

To test: serve `dist/site` (e.g. `python3 -m http.server 8766` inside it) and run
`python3 scripts/audit.py <dir>` (layout, buttons, real résumé download) and `python3 scripts/loader_test.py <dir>` (loading screen).
Set `SITE_URL` if the site is served elsewhere. `scripts/check.py` takes full-page screenshots.
(needs `pip install playwright && playwright install chromium`).

## Notes

- Fonts: Bricolage Grotesque (display), Plus Jakarta Sans (body) and IBM Plex Mono (labels) from Google Fonts.
- Markup lives in `src/markup.py`; the first design is kept in `archive/v1/` for reference.
- Loading screen (`src/loader.js`, styles in `src/critical.css`): real 0–100% progress, weighted by actual tasks:
  each page section arriving (36), the font stylesheet (4), each of five typefaces (25), the portrait (21) and the
  interactive setup in main.js (14). No timer moves the number; failed or stalled tasks close via timeouts so the page
  always opens. The knee extends from 90° to straight as progress climbs. Critical CSS and the loader come first in
  the HTML so it paints within the first ~10 KB; fonts load without blocking. Skipped entirely without JavaScript.
- Respects reduced-motion settings; works with keyboard and screen readers.
- Home address, date of birth and gender from the résumé are intentionally not published.
