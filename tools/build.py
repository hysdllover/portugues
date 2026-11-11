"""Build the home-screen web app (index.html) from src/app.html.

src/app.html is the page body used for the claude.ai artifact (no <head>).
This wraps it in a full document with the PWA head tags and the
service worker registration. Run: python3 tools/build.py
"""
import hashlib, json, re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
src = (root / 'src' / 'app.html').read_text(encoding='utf-8')
VERSION = hashlib.sha1(src.encode('utf-8')).hexdigest()[:10]

# head part = everything before the first <style> (title, meta, font link)
cut = src.index('<style>')
head_bits = [l for l in src[:cut].splitlines() if l.strip() and 'apple-mobile-web-app' not in l and 'claude:' not in l]
body = src[cut:]

head = '\n'.join([
    '<!doctype html>',
    '<html lang="ko">',
    '<head>',
    '<meta charset="utf-8">',
    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">',
    '<meta name="apple-mobile-web-app-capable" content="yes">',
    '<meta name="mobile-web-app-capable" content="yes">',
    '<meta name="apple-mobile-web-app-status-bar-style" content="default">',
    '<meta name="apple-mobile-web-app-title" content="Passo">',
    '<meta name="theme-color" content="#EDF0F2">',
    '<link rel="manifest" href="manifest.webmanifest">',
    '<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">',
    '<link rel="icon" type="image/png" href="icons/icon-192.png">',
    *head_bits,
    '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
    'body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>',
    '</head>',
    '<body>',
    f"<script>window.APP_VERSION = '{VERSION}';</script>",
])
tail = ("\n<script>if ('serviceWorker' in navigator) addEventListener('load', () => "
        "navigator.serviceWorker.register('sw.js', {updateViaCache: 'none'}).catch(() => {}));</script>\n</body>\n</html>\n")
(root / 'index.html').write_text(head + '\n' + body.rstrip('\n') + tail, encoding='utf-8')
(root / 'version.json').write_text(json.dumps({'v': VERSION}) + '\n', encoding='utf-8')
sw = root / 'sw.js'
sw.write_text(re.sub(r"const CORE = 'passo-core-[^']*'", f"const CORE = 'passo-core-{VERSION}'", sw.read_text(encoding='utf-8')), encoding='utf-8')
print('built index.html, version', VERSION)
