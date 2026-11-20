"""Prepare only public website assets for Cloudflare Workers static hosting."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'dist'
DEST.mkdir(exist_ok=True)
for name in ('index.html', 'sitemap.xml', 'robots.txt', 'img', 'products'):
    source = ROOT / name
    target = DEST / name
    if source.is_dir():
        shutil.copytree(source, target, dirs_exist_ok=True)
    else:
        shutil.copy2(source, target)
(DEST / '404.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page not found | HunzaNestart</title><main><h1>Page not found</h1><p><a href="/">Browse HunzaNestart templates</a></p></main></html>', encoding='utf-8')
print('Public files packaged in dist/')
