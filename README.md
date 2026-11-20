# HunzaNestart

Brand website for the HunzaNestart Etsy shop (https://hunzanestart.etsy.com). Static page served by GitHub Pages. Every product link goes to Etsy using the Share & Save link format.

## Website SEO draft — T-013

Prepared locally from commit bce2907 (33 products), 20 November 2026.
PR #1 was merged after Hassan's publishing approval on 20 November 2026.
Production target: https://hunzanestart.hunzo-hk.workers.dev/ . Canonical URLs
and sitemap entries use this primary address, including on GitHub Pages.

Rebuild after catalogue changes:

```sh
python tools/build_shelves.py
python tools/build_seo.py
python tools/check_site.py
python tools/package_site.py
```

For a confirmed Cloudflare production address, pass it to build_seo.py with
`--base-url https://THE-APPROVED-HOST/` before packaging. Workers static assets
configuration is in wrangler.jsonc; only dist/ is public. Do not deploy before
Hassan reviews and approves the exact destination and draft.

Verified: homepage plus 33 product pages, local link targets, unique titles,
one H1 per page, canonical URLs, JSON-LD parsing and sitemap consistency.
Browser preview checked on Biweekly Budget. Product claims and images are
reused from the source catalogue; actual product files were not re-audited.
Product structured data has no unverified prices or ratings and is not yet
eligible for Google product rich results without verified offer/review data.

Cloudflare is connected to this repository's main branch. Build command:
`python3 tools/build_seo.py --base-url https://hunzanestart.hunzo-hk.workers.dev/ && python3 tools/check_site.py && python3 tools/package_site.py`.
Deploy command: `npx wrangler deploy`. Preview builds are disabled.
Pending: first repository build and production checks, Search Console ownership
and sitemap submission. No credentials stored.
Current task record: shared tracker, Active Tasks, T-013.
