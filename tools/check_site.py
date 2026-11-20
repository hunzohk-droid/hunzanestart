"""Check generated pages, local targets, metadata, schema and sitemap."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
pages = [ROOT / 'index.html', *sorted((ROOT / 'products').glob('*/index.html'))]
canonicals = set()
titles = set()
for file in pages:
    text = file.read_text(encoding='utf-8')
    title = re.search(r'<title>(.*?)</title>', text).group(1)
    assert title not in titles, f'Duplicate title: {file}'
    titles.add(title)
    assert len(re.findall(r'<h1\b', text)) == 1, file
    canonical = re.findall(r'<link rel="canonical" href="([^"]+)"', text)
    assert len(canonical) == 1 and canonical[0] not in canonicals, file
    canonicals.add(canonical[0])
    assert '<meta name="description"' in text, file
    for target in re.findall(r'(?:href|src)="([^"]+)"', text):
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        path = (file.parent / unquote(parsed.path)).resolve()
        assert path.is_relative_to(ROOT), (file, target)
        assert path.exists(), (file, target)
        if path.is_dir():
            assert (path / 'index.html').exists(), (file, target)
    for data in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S):
        json.loads(data)
sitemap = ET.parse(ROOT / 'sitemap.xml')
urls = {node.text for node in sitemap.findall('.//{*}loc')}
assert urls == canonicals, 'Sitemap and canonical URLs differ'
assert len(pages) == 34, f'Expected homepage + 33 products, found {len(pages)}'
print(f'PASS: {len(pages)} pages; unique titles, H1s, canonical URLs, local links, JSON-LD and sitemap checked.')
