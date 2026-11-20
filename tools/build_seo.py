"""Build product landing pages from the actual homepage catalogue.

Run after build_shelves.py. Set --base-url to the approved production URL
when moving hosts; the current GitHub Pages address remains the default.
"""
import argparse
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urljoin
from xml.etree.ElementTree import Element, SubElement, ElementTree

ROOT = Path(__file__).resolve().parent.parent


def slug(title):
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')


class Catalogue(HTMLParser):
    def __init__(self):
        super().__init__()
        self.products = {}
        self.product = None
        self.field = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'article' and a.get('class') == 'card':
            self.product = {}
        if self.product is None:
            return
        if tag == 'img':
            self.product.update(image=a['src'], alt=a.get('alt', ''))
        if tag in ('h3', 'p'):
            self.field = 'title' if tag == 'h3' else 'description'
            self.product[self.field] = ''
        if tag == 'span' and a.get('class') == 'chip':
            self.field = 'format'
            self.product[self.field] = ''
        if tag == 'a' and 'hunzanestart.etsy.com/listing/' in a.get('href', ''):
            self.product['etsy'] = a['href']

    def handle_data(self, data):
        if self.product is not None and self.field:
            self.product[self.field] += data

    def handle_endtag(self, tag):
        if tag in ('h3', 'p', 'span'):
            self.field = None
        if tag == 'article' and self.product is not None:
            self.products[self.product['etsy']] = self.product
            self.product = None


def metadata(title, description, url, image):
    values = [('og:type', 'website'), ('og:site_name', 'HunzaNestart'),
              ('og:title', title), ('og:description', description),
              ('og:url', url), ('og:image', image)]
    return ('<link rel="canonical" href="' + html.escape(url, quote=True) + '">\n' +
            '\n'.join(f'<meta property="{k}" content="{html.escape(v, quote=True)}">' for k, v in values) +
            '\n<meta name="twitter:card" content="summary_large_image">')


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--base-url', default='https://hunzohk-droid.github.io/hunzanestart/')
    args = parser.parse_args()
    base = args.base_url.rstrip('/') + '/'
    if not base.startswith('https://'):
        parser.error('--base-url must be an HTTPS production address')
    page = (ROOT / 'index.html').read_text(encoding='utf-8')
    catalogue = Catalogue()
    catalogue.feed(page)
    products = list(catalogue.products.values())
    assert products and len({slug(p['title']) for p in products}) == len(products)
    css = re.search(r'<style>(.*?)</style>', page, re.S).group(1)
    # Replace generated metadata rather than accumulating it on repeated builds.
    page = re.sub(r'\n<!-- SEO:START -->.*?<!-- SEO:END -->', '', page, flags=re.S)
    title = 'Google Sheets Templates & Printable Planners | HunzaNestart'
    page = re.sub(r'<title>.*?</title>', f'<title>{html.escape(title)}</title>', page)
    home_description = re.search(r'<meta name="description" content="([^"]*)"', page).group(1)
    page = page.replace('</head>', '\n<!-- SEO:START -->\n' + metadata(title, home_description, base, urljoin(base, 'img/banner.webp')) + '\n<!-- SEO:END -->\n</head>')
    if '<h1' not in page:
        page = page.replace('<div class="lead">', '<h1>Templates and printables for work, home and life</h1>\n    <div class="lead">', 1)
    for p in products:
        name = html.escape(p['title'])
        link = f'products/{slug(p["title"])}/'
        page = page.replace(f'<h3>{name}</h3>', f'<h3><a href="{link}">{name}</a></h3>')
    (ROOT / 'index.html').write_text(page, encoding='utf-8')
    urls = [base]
    for p in products:
        path = f'products/{slug(p["title"])}/'
        url = urljoin(base, path)
        urls.append(url)
        esc = lambda key: html.escape(p[key], quote=True)
        image = p['image'] if p['image'].startswith('https://') else '../../' + p['image']
        related = [x for x in products if x['format'] == p['format'] and x != p][:3]
        related_links = ''.join(f'<li><a href="../{slug(x["title"])}/">{html.escape(x["title"])}</a></li>' for x in related)
        # Product facts are copied from source. No unverified offers or reviews.
        data = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': p['title'],
                'url': url, 'description': p['description'],
                'mainEntity': {'@type': 'Product', 'name': p['title'],
                    'description': p['description'], 'image': urljoin(base, p['image']),
                    'brand': {'@type': 'Brand', 'name': 'HunzaNestart'}, 'sameAs': p['etsy']}}
        output = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc('title')} — {esc('format')} | HunzaNestart</title>
<meta name="description" content="{esc('description')} Format: {esc('format')}. View details and buy on Etsy.">
<link rel="icon" href="../../img/logo.png">
{metadata(p['title'] + ' | HunzaNestart', p['description'], url, urljoin(base, p['image']))}
<style>{css}
.product{{display:grid;grid-template-columns:1fr 1fr;gap:32px;padding-block:36px}}
.product img{{width:100%;height:auto;border-radius:12px}}h1{{font-size:clamp(2rem,4vw,3rem)}}
.product p{{max-width:60ch}}.product .btn{{white-space:normal}}
@media(max-width:760px){{.product{{grid-template-columns:1fr}}}}
</style><script type="application/ld+json">{json.dumps(data).replace('<', chr(92) + 'u003c')}</script>
</head><body><header class="top"><div class="wrap"><a class="brand" href="../../">HunzaNestart</a><a href="../../">Browse all templates</a></div></header>
<main class="wrap"><nav aria-label="Breadcrumb"><p><a href="../../">Home</a> / {esc('title')}</p></nav>
<article class="product"><img src="{html.escape(image, quote=True)}" alt="{esc('alt')}" width="720" height="540">
<div><p class="eyebrow">Digital download · {esc('format')}</p><h1>{esc('title')}</h1>
<p>{esc('description')}</p><p><a class="btn" href="{esc('etsy')}">View details and buy on Etsy</a></p>
<p>Check the current price, complete contents and software requirements on Etsy before you buy.</p>
<h2>Get your digital download</h2><p>Purchase through Etsy. After payment is confirmed, open your download from your Etsy purchase. Follow the included guide to access your files or template.</p>
<h2>Before you buy</h2><p>This is a digital product. No physical item is shipped. This product uses {esc('format')}. Check the listing for the exact file formats and account requirements.</p>
<p>Questions about this template? <a href="{esc('etsy')}">Visit the Etsy listing</a> to contact HunzaNestart.</p></div></article>
{'<section><h2>More templates to explore</h2><ul>' + related_links + '</ul></section>' if related else ''}
</main><footer><div class="wrap">HunzaNestart · Digital downloads · <a href="https://hunzanestart.etsy.com/">Etsy shop</a></div></footer></body></html>'''
        folder = ROOT / path
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'index.html').write_text(output, encoding='utf-8')
    root = Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for url in urls:
        SubElement(SubElement(root, 'url'), 'loc').text = url
    ElementTree(root).write(ROOT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {base}sitemap.xml\n', encoding='utf-8')
    (ROOT / 'wrangler.jsonc').write_text(json.dumps({'name': 'hunzanestart', 'compatibility_date': '2026-11-20', 'assets': {'directory': './dist', 'not_found_handling': '404-page'}}, indent=2) + '\n', encoding='utf-8')
    print(f'Generated {len(products)} product pages and {len(urls)} sitemap URLs. Base: {base}')


if __name__ == '__main__':
    main()
