#!/usr/bin/env python3
"""Build the new CMA site from its editable template and original media registry.

No network or third-party Python dependencies. Artwork bytes are never re-encoded.
Usage: python3 cma/redesign/build.py --assets-source cma/dist/index.html --output-dir cma/release
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

VERSION = 'studio-rebuild-20260922'
HERE = Path(__file__).resolve().parent

class Registry(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.inside = False
        self.images: dict[str, str] = {}
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == 'template' and a.get('id') == 'asset-library':
            self.inside = True
        if self.inside and tag == 'img':
            key, src = a.get('data-key'), a.get('src')
            if not key or not src or not re.fullmatch(r'[a-z0-9-]+', key):
                raise ValueError('Invalid original asset record')
            if key in self.images:
                raise ValueError(f'Duplicate asset key: {key}')
            self.images[key] = src
    def handle_endtag(self, tag: str) -> None:
        if tag == 'template':
            self.inside = False

def build(source: Path, destination: Path, template_path: Path) -> dict:
    original = source.read_text(encoding='utf-8')
    registry = Registry()
    registry.feed(original)
    if not registry.images:
        raise ValueError('Original CMA artwork registry is missing; refusing a placeholder build')
    source_parts = {name:(HERE/name).read_text(encoding='utf-8') for name in ('site.css','site.js')}
    template = template_path.read_text(encoding='utf-8')
    template = template.replace('{{SITE_CSS}}',source_parts['site.css']).replace('{{SITE_JS}}',source_parts['site.js'])
    template_bytes = template.encode('utf-8')
    required = set(re.findall(r'\{\{asset:([a-z0-9-]+)\}\}', template))
    # Dialog images are referenced in the application data rather than HTML tokens.
    required.update({'logo','hunters','hunters-event','hunters-social','nightsky-poster',
                     'nightsky-cherry','nightsky-lime','nightsky-ale','gold-standard',
                     'gold-black','gold-nine','gold-poster','gold-event','whitestone',
                     'whitestone-one','whitestone-two','land-of-gold','elegance',
                     'elegance-aloe','elegance-cocoa','elegance-pink','dr-klin'})
    missing = sorted(required - registry.images.keys())
    if missing:
        raise ValueError(f'Missing authentic artwork: {missing}')
    destination.mkdir(parents=True, exist_ok=True)
    media = destination / 'media'
    media.mkdir(exist_ok=True)
    extensions = {'image/webp':'webp','image/png':'png','image/jpeg':'jpg','image/gif':'gif'}
    records = []
    paths = {}
    for key, uri in registry.images.items():
        match = re.fullmatch(r'data:([^;,]+);base64,([A-Za-z0-9+/=\s]+)', uri)
        if not match or match[1] not in extensions:
            raise ValueError(f'{key}: expected an embedded original raster image')
        data = base64.b64decode(re.sub(r'\s','',match[2]), validate=True)
        if len(data) < 20:
            raise ValueError(f'{key}: empty image data')
        digest = hashlib.sha256(data).hexdigest()
        filename = f'{key}-{digest[:12]}.{extensions[match[1]]}'
        output = media / filename
        output.write_bytes(data)
        if hashlib.sha256(output.read_bytes()).hexdigest() != digest:
            raise AssertionError('Artwork preservation verification failed')
        paths[key] = f'/media/{filename}'
        records.append({'key':key,'file':paths[key],'bytes':len(data),'sha256':digest})
    for key in required:
        template = template.replace('{{asset:'+key+'}}', paths[key])
    template = template.replace('{{ASSET_MAP}}', json.dumps(paths, ensure_ascii=True).replace('<','\\u003c'))
    if re.search(r'\{\{(?:asset:|ASSET_MAP|SITE_CSS|SITE_JS)', template):
        raise AssertionError('Unresolved build tokens')
    if f'content="{VERSION}"' not in template:
        raise AssertionError('Missing release identifier')
    (destination / 'index.html').write_text(template,encoding='utf-8')
    manifest = {'version':VERSION,'template_sha256':hashlib.sha256(template_bytes).hexdigest(),
                'html_sha256':hashlib.sha256(template.encode()).hexdigest(),
                'asset_count':len(records),'artwork_bytes_preserved':True,'assets':records}
    (destination / 'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'version':VERSION,'html_bytes':len(template.encode()),'artwork_count':len(records),
                      'artwork_bytes':sum(r['bytes'] for r in records),'artwork_bytes_preserved':True}))
    return manifest

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets-source',type=Path,default=HERE.parent/'dist'/'index.html')
    parser.add_argument('--output-dir',type=Path,default=HERE.parent/'release')
    parser.add_argument('--template',type=Path,default=HERE/'site.html')
    args = parser.parse_args()
    build(args.assets_source,args.output_dir,args.template)

if __name__ == '__main__':
    main()
