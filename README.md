# Jessie J. — Physiotherapist portfolio

A fast, dependency-free static website. No framework, no build step needed to deploy.

## Deploy (pick one)

Everything to upload is in `dist/site/`:

```
dist/site/
  index.html              the whole page (HTML, CSS and JS inlined)
  Jessie-J-Resume.pdf     public résumé (home address and date of birth removed)
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

To test: serve `dist/site` on port 8765 and run `python3 scripts/check.py <screenshot-folder>`
(needs `pip install playwright && playwright install chromium`).

## Notes

- Fonts: Bricolage Grotesque (display), Plus Jakarta Sans (body) and IBM Plex Mono (labels) from Google Fonts.
- Markup lives in `src/markup.py`; the first design is kept in `archive/v1/` for reference.
- Respects reduced-motion settings; works with keyboard and screen readers.
- Home address, date of birth and gender from the résumé are intentionally not published.
