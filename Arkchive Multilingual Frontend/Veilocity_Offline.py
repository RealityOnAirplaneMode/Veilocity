#!/usr/bin/env python3
"""Build offline-friendly JavaScript indexes for the Veilocity Portable Ark.

Place in the archive root alongside language folders and 'court-of-illusions-trafficking'.
Run: python3 build_manifests.py
Existing index.html is preserved. Use --write-index to replace it.
The Court link and optional Bitcoin support/contact section are embedded in the landing-page template.
No external Python packages or local HTTP server required.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

VERSION_RE = re.compile(r"\s+(v\d+)$", re.IGNORECASE)
COURT_FOLDER = "court-of-illusions-trafficking"
COURT_HTML = "ENGLISH - Court.html"
ARCHIVE_FOLDER_RE = re.compile(r"^(?:ark\s+)?[^/]+\s+v\d+$", re.IGNORECASE)
FLAG_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
HTML_EXTENSIONS = {".html", ".htm"}


def natural_key(value: str):
    return [int(x) if x.isdigit() else x.casefold() for x in re.split(r"(\d+)", value)]


def js_literal(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def get_version(folder_name: str) -> str:
    match = VERSION_RE.search(folder_name)
    return match.group(1) if match else ""


def get_country(folder_name: str) -> str:
    country = re.sub(r"^ark\s+", "", folder_name, flags=re.IGNORECASE)
    country = VERSION_RE.sub("", country)
    return re.sub(r"\s+", " ", country.replace("_", " ")).strip()


def find_flag(files: list[str]) -> str:
    images = [name for name in files if Path(name).suffix.lower() in FLAG_EXTENSIONS]
    candidates = [name for name in images if "flag" in Path(name).stem.casefold()]
    return sorted(candidates, key=natural_key)[0] if candidates else ""


def choose_primary(files: list[str], country: str) -> str:
    html = [name for name in files if Path(name).suffix.lower() in HTML_EXTENSIONS]
    # Never use a court-related page as the landing page.
    html = [name for name in html if "court" not in Path(name).name.casefold()]
    if not html:
        return ""
    # Prefer an HTML page whose name matches the language/country, then stable sort.
    tokens = [t for t in re.split(r"[^\w]+", country.casefold()) if len(t) > 2]
    def priority(name: str):
        stem = Path(name).stem.casefold()
        return (0 if any(token in stem for token in tokens) else 1,
                len(Path(name).parts), natural_key(name))
    return sorted(html, key=priority)[0]


INDEX_HTML = '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n<title>Veilocity — Multilingual Archive</title>\n<style>\n:root{color-scheme:light;--peach:#eac3a1;--cream:#f8ead8;--paper:#fdf3e5;--ink:#51473c;--muted:#786958;--teal:#307b78;--line:#e9cfb4;--orange:#df683b}\n*{box-sizing:border-box}body{margin:0;min-height:100vh;background:linear-gradient(115deg,#e5b894 0%,#f3d2af 55%,#eac29e 100%);color:var(--ink);font:16px/1.55 system-ui,-apple-system,\'Segoe UI\',sans-serif}\n.shell{max-width:1300px;margin:26px auto;padding:26px;display:grid;grid-template-columns:250px minmax(0,1fr);gap:36px;background:rgba(252,240,224,.93);border:1px solid #f8e5d1;border-radius:22px;box-shadow:0 16px 42px #69492e25}\n.sidebar{display:flex;flex-direction:column;gap:15px}.brand-image{width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:14px;box-shadow:0 6px 20px #55412e26}.brand-fallback{width:100%;aspect-ratio:1/1;display:grid;place-items:center;border-radius:14px;background:linear-gradient(145deg,#b7a59a,#e6c39c);font:700 1.9rem Georgia,serif;color:#285e5b;text-align:center}.side-note{background:#fff4e6;border:1px solid #efd5b9;border-radius:14px;padding:15px;color:#67594c;font-size:.92rem}.side-note strong{color:var(--orange)}\n.content{min-width:0}header{border-bottom:1px solid #ead9c7;padding:6px 0 20px;margin-bottom:22px}.eyebrow{text-transform:uppercase;letter-spacing:.18em;color:#b2a18e;font-size:.73rem}h1{color:var(--teal);font-size:clamp(2rem,4.5vw,3.1rem);font-weight:750;letter-spacing:.015em;margin:4px 0 8px}header p{margin:0;color:var(--muted)}\n.tools{display:flex;align-items:center;gap:15px;margin:0 0 23px;flex-wrap:wrap}input{background:#fffaf4;color:var(--ink);font:inherit;border:1px solid #e5d0b8;border-radius:12px;padding:14px 16px;min-width:220px;flex:1;outline-color:var(--teal)}#count{color:var(--muted);font-size:.9rem}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:17px}.card{background:#fff6eb;border:1px solid var(--line);border-radius:15px;padding:19px 13px 20px;text-align:center;box-shadow:0 4px 13px #73563a12;transition:transform .16s,box-shadow .16s}.card:hover{transform:translateY(-3px);box-shadow:0 9px 18px #73563a20}.flag-link{height:108px;display:flex;align-items:center;justify-content:center;border-radius:10px;text-decoration:none}.flag-link:focus-visible{outline:3px solid var(--teal)}.flag{max-width:155px;max-height:94px;object-fit:contain;filter:drop-shadow(0 4px 5px #0003)}.placeholder{font-size:3rem;color:var(--teal)}.country{color:var(--teal);font-weight:700;font-size:1.17rem;margin:10px 0 7px;overflow-wrap:anywhere}.version{display:inline-block;padding:3px 12px;background:#e6eeea;border-radius:30px;color:#426d66;font-size:.78rem;font-weight:700}.fallback{display:inline-block;margin-top:9px;color:var(--teal)}.empty{padding:30px;color:var(--muted);text-align:center}footer{font-size:.83rem;color:var(--muted);margin-top:40px;text-align:center}\n@media(max-width:760px){.shell{grid-template-columns:1fr;margin:12px;padding:18px;gap:20px}.sidebar{flex-direction:row;align-items:center}.brand-image,.brand-fallback{width:125px;min-width:125px;aspect-ratio:1}.side-note{flex:1}header{padding-top:0}.grid{grid-template-columns:repeat(auto-fill,minmax(145px,1fr))}}@media(max-width:430px){.sidebar{flex-direction:column}.brand-image,.brand-fallback{width:180px}h1{font-size:2rem}}\n.court-link-wrap{margin:0 0 24px}.court-link{display:inline-block;background:var(--teal);color:#fff;text-decoration:none;border-radius:12px;padding:13px 22px;font-weight:700;box-shadow:0 4px 12px #307b7822}.court-link:hover,.court-link:focus-visible{background:#24635f;color:#fff;text-decoration:none}.archive-subtitle{font-size:1rem;color:var(--muted);margin:0 0 18px;font-weight:600}.archive-description{max-width:68ch;margin:0 0 14px;line-height:1.65}.archive-remembrance{font-weight:750;color:var(--teal);margin:0 0 18px}.archive-testimony{background:#fff4e6;border-left:4px solid var(--teal);border-radius:0 12px 12px 0;padding:12px 17px;margin:0 0 20px;max-width:68ch}.archive-testimony p{margin:0;font-weight:650}.archive-testimony p+p{margin-top:3px}.archive-prompt{color:var(--muted);margin:0}\n\n.support-panel{margin:0 0 24px;padding:20px;border:1px solid #edc9a7;border-radius:16px;background:linear-gradient(145deg,#fff7ec,#f7e6d0);box-shadow:0 4px 15px #73563a12}.support-panel h2{color:var(--teal);margin:0 0 9px;font-size:1.35rem}.support-panel p{margin:0 0 14px}.support-layout{display:grid;grid-template-columns:minmax(0,180px) minmax(0,1fr);gap:20px;align-items:start}.support-art{width:100%;border-radius:13px;box-shadow:0 4px 12px #73563a22}.support-label{color:var(--orange);font-weight:750;margin:14px 0 7px}.support-address{display:block;overflow-wrap:anywhere;padding:12px;border:1px solid #edc9a7;border-radius:10px;background:#f9e2c9;font:0.91rem/1.55 ui-monospace,SFMono-Regular,Consolas,monospace}.support-actions,.support-contacts{display:flex;gap:9px;flex-wrap:wrap;margin-top:12px}.support-action,.support-contacts a{display:inline-block;border:1px solid #e6d5c1;border-radius:22px;padding:8px 13px;background:#fff4e6;color:var(--teal);font:600 .91rem system-ui,sans-serif;text-decoration:none;cursor:pointer}.support-action:hover,.support-contacts a:hover{background:#e7f0ec}.support-status{font-size:.84rem;color:var(--muted);min-height:1.4em;margin-top:7px}.support-note{font-size:.88rem;color:var(--muted)}@media(max-width:570px){.support-layout{grid-template-columns:1fr}.support-art{max-width:210px}}\n</style><script src="archives.js"></script></head>\n<body><main class="shell"><aside class="sidebar"><div id="brand"><div class="brand-fallback">VEILOCITY</div></div><div class="side-note"><strong>VEILOCITY · ARKHIVE</strong><p>Multilingual portable archives for offline browsing. Select a flag to open its archive.</p></div></aside>\n<section class="content"><header><div class="eyebrow">VEILOCITY</div><h1>Veilocity — Multilingual Archive</h1><p class="archive-subtitle">Online Mirror + Patreon Frontend + Offline Archive</p><p class="archive-description">This repository is a multilingual archive of my social media writings, designed for preservation, accessibility, and redistribution.</p><p class="archive-remembrance">This is not entertainment — it’s remembrance.</p><div class="archive-testimony"><p>Inner order &gt; outer control.</p><p>I don’t perform — I testify.</p></div><p class="archive-prompt">Choose a language or country to explore the archive.</p></header><div class="court-link-wrap"><a class="court-link" href="court-of-illusions-trafficking/ENGLISH%20-%20Court.html">Court of Illusions — Trafficking</a></div><section class="support-panel" aria-labelledby="support-heading"><h2 id="support-heading">Support Veilocity — Keep the Record Accessible</h2><p>Bringing this record into public view has taken considerable time, care, and energy. Veilocity is preserved and shared for anyone who wishes to examine the material independently. If you find value in this work, your voluntary support helps sustain its preservation and accessibility. There is no obligation to contribute.</p><div class="support-layout"><div id="support-art-holder"></div><div><p>The QR code in the Veilocity artwork contains my Bitcoin address. If you feel called to support this work, you may contribute using it.</p><div class="support-label">BTC address:</div><code class="support-address" id="support-btc">bc1qr5n4feh27pktff0cmu3m4n2zd70s466tsrxzk3</code><div class="support-actions"><button class="support-action" type="button" id="copy-btc">Copy BTC Address</button><a class="support-action" href="bitcoin:bc1qr5n4feh27pktff0cmu3m4n2zd70s466tsrxzk3">Open Bitcoin wallet</a></div><div class="support-status" id="support-status" role="status" aria-live="polite"></div><div class="support-label">Contact details:</div><div class="support-contacts"><a href="https://patreon.com/StephenChristopherCooke?utm_medium=unknown&amp;utm_source=join_link&amp;utm_campaign=creatorshare_creator&amp;utm_content=copyLink" target="_blank" rel="noopener noreferrer">Patreon</a><a href="https://www.tiktok.com/@veilocity_rising?is_from_webapp=1&amp;sender_device=pc" target="_blank" rel="noopener noreferrer">@veilocity_rising (TikTok)</a><a href="https://www.tiktok.com/@veilocity_?is_from_webapp=1&amp;sender_device=pc" target="_blank" rel="noopener noreferrer">@veilocity (TikTok)</a><a href="https://github.com/veilocity717-blip/VeilocityAndroid" target="_blank" rel="noopener noreferrer">GitHub</a><a href="mailto:stephencooke.c@gmail.com">Contact</a></div></div></div></section><div class="tools"><input id="search" type="search" placeholder="Search country, language, folder or version…" aria-label="Search archives"><span id="count" aria-live="polite"></span></div><div id="grid" class="grid"></div><p id="empty" class="empty" hidden></p><footer>Landing page build: court-text-link-v4 · Portable archive · Local files · No server required on compatible desktop browsers</footer></section></main>\n<script>\n(()=>{\'use strict\';const config=window.VEILOCITY_ARCHIVES||{};const folders=config.archives||[];const grid=document.getElementById(\'grid\'),search=document.getElementById(\'search\'),count=document.getElementById(\'count\'),empty=document.getElementById(\'empty\'),items=[];\nconst path=(folder,file)=>[folder,...String(file||\'\').split(\'/\')].map(encodeURIComponent).join(\'/\');const version=f=>(f.match(/\\s+(v\\d+)$/i)||[])[1]||\'\';const country=f=>f.replace(/^ark\\s+/i,\'\').replace(/\\s+v\\d+$/i,\'\');\nif(config.logo){const img=document.createElement(\'img\');img.className=\'brand-image\';img.alt=\'Veilocity artwork\';img.src=path(config.logo.folder,config.logo.file);img.onerror=()=>img.remove();document.getElementById(\'brand\').replaceChildren(img);img.addEventListener(\'error\',()=>{document.getElementById(\'brand\').innerHTML=\'<div class="brand-fallback">VEILOCITY</div>\';});}\nif(config.logo){const artwork=document.createElement(\'img\');artwork.className=\'support-art\';artwork.src=path(config.logo.folder,config.logo.file);artwork.alt=\'Veilocity artwork with embedded Bitcoin QR code\';artwork.onerror=()=>artwork.remove();document.getElementById(\'support-art-holder\').append(artwork);}\nconst copyBtn=document.getElementById(\'copy-btc\');if(copyBtn)copyBtn.addEventListener(\'click\',async()=>{const value=document.getElementById(\'support-btc\').textContent;const status=document.getElementById(\'support-status\');try{if(!navigator.clipboard||!navigator.clipboard.writeText)throw Error(\'Clipboard API unavailable\');await navigator.clipboard.writeText(value);status.textContent=\'Bitcoin address copied.\';}catch(e){const t=document.createElement(\'textarea\');t.value=value;t.style.position=\'fixed\';t.style.opacity=\'0\';document.body.append(t);t.select();let ok=false;try{ok=document.execCommand(\'copy\')}catch(e){}t.remove();status.textContent=ok?\'Bitcoin address copied.\':\'Select and copy the address shown above.\';}});\nfunction render(){const q=search.value.trim().toLocaleLowerCase();const filtered=items.filter(i=>i.search.includes(q)).sort((a,b)=>a.name.localeCompare(b.name));grid.replaceChildren();for(const i of filtered){const card=document.createElement(\'article\');card.className=\'card\';const a=document.createElement(\'a\');a.className=\'flag-link\';a.href=path(i.folder,i.primary);a.title=\'Open \'+i.name+\' archive\';if(i.flag){const img=document.createElement(\'img\');img.className=\'flag\';img.src=path(i.folder,i.flag);img.alt=i.name+\' flag\';img.onerror=()=>{img.replaceWith(Object.assign(document.createElement(\'span\'),{className:\'placeholder\',textContent:\'◈\'}));};a.append(img)}else{const span=document.createElement(\'span\');span.className=\'placeholder\';span.textContent=\'◈\';a.append(span)}const title=document.createElement(\'div\');title.className=\'country\';title.textContent=i.name;const pill=document.createElement(\'span\');pill.className=\'version\';pill.textContent=i.ver||\'Archive\';card.append(a,title,pill);if(!i.flag){const wrap=document.createElement(\'div\');const link=document.createElement(\'a\');link.className=\'fallback\';link.href=a.href;link.textContent=\'Open archive\';wrap.append(link);card.append(wrap)}grid.append(card)}count.textContent=filtered.length+\' of \'+items.length+\' archive\'+(items.length===1?\'\':\'s\');empty.hidden=filtered.length!==0;empty.textContent=folders.length===0?\'No archives found. Run build_manifests.py.\':items.length===0?\'No archive manifests loaded.\':\'No matching archives.\'}\nsearch.addEventListener(\'input\',render);render();for(const folder of folders){const s=document.createElement(\'script\');s.src=path(folder,\'manifest.js\');s.onload=()=>{const m=window.VEILOCITY_MANIFESTS?.[folder];if(m){const primary=m.primary_html||(m.files||[]).find(f=>/\\.html?$/i.test(f)&&!/court/i.test(f));if(primary){const name=m.country||country(folder),ver=m.version||version(folder);items.push({folder,name,ver,flag:m.flag||\'\',primary,search:[folder,name,ver,m.language,m.description,primary].join(\' \').toLocaleLowerCase()});}}render()};s.onerror=render;document.head.append(s)}})();\n</script></body></html>\n'

def find_logo(root: Path, directories: list[Path]):
    # Prefer logo.png beside this script (the archive root).
    logo = root / "logo.png"
    if logo.is_file():
        return {"folder": ".", "file": "logo.png"}
    # An explicit image named veilocity-logo.* in the root takes precedence.
    extensions = FLAG_EXTENSIONS - {".svg"}
    for stem in ("veilocity-logo", "veilocity_logo", "veilocity"):
        for p in root.iterdir():
            if p.is_file() and p.stem.casefold() == stem and p.suffix.lower() in extensions:
                return {"folder": ".", "file": p.name}
    # Search the English archive for a graphic with a descriptive filename.
    for folder in sorted(directories, key=lambda d: ("english" not in d.name.casefold(), d.name.casefold())):
        candidates = []
        for p in folder.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in extensions:
                continue
            name = p.stem.casefold()
            if "flag" in name:
                continue
            if any(word in name for word in ("veilocity", "logo", "qr")):
                priority = (0 if "veilocity" in name else 1 if "logo" in name else 2, len(p.parts))
                candidates.append((priority, p))
        if candidates:
            p = sorted(candidates, key=lambda x: x[0])[0][1]
            return {"folder": folder.name, "file": p.relative_to(folder).as_posix()}
    return None


# Shared with the Android app: archive downloads and top-level navigation.
DOWNLOADS_HTML = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Download Archives — Veilocity</title><style>\n*{box-sizing:border-box}body{margin:0;background:linear-gradient(115deg,#e5b894,#f3d2af 55%,#eac29e);color:#51473c;font:16px/1.55 system-ui,sans-serif}main{max-width:1100px;margin:24px auto;padding:clamp(18px,4vw,36px);background:#fcf0e0;border-radius:20px}h1,h2{color:#307b78}.back{color:#307b78;text-decoration:none;font-weight:650}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:16px;margin-top:24px}.card{display:flex;flex-direction:column;align-items:flex-start;background:#fff6eb;border:1px solid #e9cfb4;border-radius:15px;padding:20px}.card h2{font-size:1.12rem;margin:0 0 8px}.card p{flex:1;margin:0 0 16px}.card a{display:inline-block;background:#307b78;color:white;text-decoration:none;padding:9px 16px;border-radius:22px;font-weight:650}.card a:hover{background:#24635f}\n</style></head><body><main><a class="back" href="index.html">← Back to Arkhive</a><h1>Download Archives</h1><p>The English Bundle is a simple starting point with English and Court content included. Additional countries can be downloaded separately and added to the same <strong>Arkhive</strong> folder (for example, <code>/sdcard/Arkhive/</code>). Preserve the folder structure and rerun this script after adding content to refresh the offline archive index.</p><div class="grid"><article class="card"><h2>VeilocityAndroid with English Bundle</h2><p>English and Court content included</p><a target="_blank" rel="noopener noreferrer" href="https://mega.nz/folder/PHglWQgS#3tiuOKGQWo_W3ViS2na04Q">Open on MEGA ↗</a></article><article class="card"><h2>VeilocityAndroid &amp; PC Offline Frontend</h2><p>Android and PC offline frontend</p><a target="_blank" rel="noopener noreferrer" href="https://mega.nz/folder/IVo13S6D#noNLsVue5xmSCg9wbaaZAA">Open on MEGA ↗</a></article><article class="card"><h2>Court of Illusions — 11/11/2026</h2><p>Standalone Court archive</p><a target="_blank" rel="noopener noreferrer" href="https://mega.nz/folder/cUllmLKB#LZAmfGupLr4RnC6HARe6Iw">Open on MEGA ↗</a></article><article class="card"><h2>Volume 1</h2><p>Arabic, Bosnia, Bulgaria</p><a target="_blank" rel="noopener noreferrer" href="https://mega.nz/folder/DvZk3LDD#jlR6em7WKG1MuIvETs9-Dg">Open on MEGA ↗</a></article><article class="card"><h2>Volume 2</h2><p>French, German, Taiwan-Mandarin</p><a target="_blank" rel="noopener noreferrer" href="https://mega.nz/folder/e6hGRJrT#aowV_WD5DXNNabhuLRNKgA">Open on MEGA ↗</a></article><article class="card"><h2>Volume 3</h2><p>Ethiopia, Korean, Türkiye, Ukrainian</p><a target="_blank" rel="noopener noreferrer" href="https://mega.nz/folder/2vpRiL7Y#GH2nJQz6dCg_cNeXGaP_6w">Open on MEGA ↗</a></article><article class="card"><h2>Volume 4</h2><p>Iran, Japan, Polish</p><a target="_blank" rel="noopener noreferrer" href="https://mega.nz/folder/Gu4HUZra#JIl85Uuev52Enbu6_M9iaA">Open on MEGA ↗</a></article><article class="card"><h2>Volume 5</h2><p>English, Hebrew, Slovenia</p><a target="_blank" rel="noopener noreferrer" href="https://mega.nz/folder/8zhCUbAb#CNPaxsmqwrBGiL6VTZm1Pg">Open on MEGA ↗</a></article><article class="card"><h2>Volume 6</h2><p>Afrikaans, Greece, Hindi, Iceland</p><a target="_blank" rel="noopener noreferrer" href="https://mega.nz/folder/EqhjRZQD#REsKXwwW-UtJmTqSrX2EXg">Open on MEGA ↗</a></article><article class="card"><h2>Volume 7</h2><p>Cantonese, Danish, Thailand</p><a target="_blank" rel="noopener noreferrer" href="https://mega.nz/folder/IYMEVYgR#TXgEEP5kBlgGURh5hmRJgw">Open on MEGA ↗</a></article><article class="card"><h2>Volume 8</h2><p>Dutch, Italy, Vietnam</p><a target="_blank" rel="noopener noreferrer" href="https://mega.nz/folder/uvZB1ZwR#lCamVpOHDmKRObZ0MWeYnQ">Open on MEGA ↗</a></article><article class="card"><h2>Volume 9</h2><p>Nepal, Sweden, Taiwan, Zulu</p><a target="_blank" rel="noopener noreferrer" href="https://mega.nz/folder/hAUlFC6Q#E4SHZy0hFOXgFFfUPHy_Xg">Open on MEGA ↗</a></article><article class="card"><h2>Volume 10</h2><p>Japan, Norwegian, Russia</p><a target="_blank" rel="noopener noreferrer" href="https://mega.nz/folder/G5gjGSjI#SYwDWOSt3Dx27Np0iy3Diw">Open on MEGA ↗</a></article><article class="card"><h2>Volume 11</h2><p>Court of Illusions, Czech Republic, Georgia, Mongolia, Portuguese (Brazil), Romania</p><a target="_blank" rel="noopener noreferrer" href="https://mega.nz/folder/IYEVjCyD#AHtyxit0-0K7odi1tRZR8Q">Open on MEGA ↗</a></article><article class="card"><h2>Volume 12</h2><p>Albania, Spanish, Ukrainian</p><a target="_blank" rel="noopener noreferrer" href="https://mega.nz/folder/KoRSFLbK#BKiOgAo7XFqp2eIC8V1W1w">Open on MEGA ↗</a></article><article class="card"><h2>Volume 13</h2><p>Mongolia, Philippines, Romania, Sweden</p><a target="_blank" rel="noopener noreferrer" href="https://mega.nz/folder/wJY2VJSY#KUqFBlrvW_TwZgim0XaeyQ">Open on MEGA ↗</a></article><article class="card"><h2>All Volumes on google (may be less current than Mega)</h2><p>Google Drive archive collection. The MEGA downloads above may contain newer material.</p><a target="_blank" rel="noopener noreferrer" href="https://drive.google.com/drive/folders/1-ITJtqt2EpUfz6eDd1i8JW6zalth44Ed?usp=sharing">Open on Google Drive ↗</a></article></div><p>MEGA links require internet access. Downloaded archive content can be browsed offline.</p></main></body></html>'


def direct_download_links() -> str:
    """Legacy helper retained for compatibility; not inserted into the landing page."""
    from html import escape, unescape
    cards = re.findall(r'<article class="card"><h2>(.*?)</h2><p>.*?</p><a[^>]*href="([^"]+)"', DOWNLOADS_HTML, re.S)
    links = ''.join('<a href="' + escape(unescape(url), quote=True) + '" target="_blank" rel="noopener noreferrer">' + unescape(title) + '</a>' for title, url in cards)
    return '<details id="veilocity-direct-downloads" class="veilocity-direct-downloads"><summary>Show all archive download links</summary><div class="veilocity-download-links">' + links + '</div></details>'

DIRECT_DOWNLOAD_CSS = '''/* Direct archive links on the main landing page */
.veilocity-direct-downloads{margin:-12px 0 24px;padding:12px 16px;border:1px solid #e9cfb4;border-radius:12px;background:#fff6eb}
.veilocity-direct-downloads summary{cursor:pointer;color:#307b78;font-weight:700}
.veilocity-download-links{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:9px;margin-top:14px}
.veilocity-download-links a{display:block;padding:9px 12px;border-radius:9px;background:#e6eeea;color:#24635f;text-decoration:none;font-weight:600;overflow-wrap:anywhere}
.veilocity-download-links a:hover{background:#cfe3dc}
'''

NAV_BUTTONS = ""  # Download Archives is placed alongside Contact in the sidebar.
NAV_CSS = r'''/* Veilocity shared app action buttons */
.veilocity-app-actions{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 24px}
.veilocity-app-actions a{display:inline-block;padding:12px 18px;border-radius:12px;background:#307b78;color:#fff;text-decoration:none;font-weight:700;box-shadow:0 4px 12px #307b7822}
.veilocity-app-actions a:hover,.veilocity-app-actions a:focus-visible{background:#24635f;color:#fff}
'''


SUPPORT_SIDEBAR = r'''<section class="support-sidebar" id="veilocity-support" aria-labelledby="support-heading"><h2 id="support-heading">Support Veilocity</h2><p>Bringing this record into public view has taken time, care and energy. If you value its preservation and accessibility, voluntary support is welcome. No obligation.</p><p class="support-hint">QR code contains my Bitcoin address. If you feel called to support this work, you may donate using it.</p><strong>BTC address:</strong><code id="support-btc">bc1qr5n4feh27pktff0cmu3m4n2zd70s466tsrxzk3</code><button type="button" id="copy-btc">Copy BTC Address</button><strong>PayPal address:</strong><p class="support-hint">Copy the address to use it in PayPal.</p><code id="support-paypal">stevecooke.c@gmail.com</code><button type="button" id="copy-paypal">Copy PayPal Address</button><div id="support-status" role="status" aria-live="polite"></div><strong>Contact details:</strong><div class="support-contacts"><a href="https://patreon.com/StephenChristopherCooke?utm_medium=unknown&amp;utm_source=join_link&amp;utm_campaign=creatorshare_creator&amp;utm_content=copyLink" target="_blank" rel="noopener noreferrer">Patreon</a><a href="https://www.tiktok.com/@veilocity_rising?is_from_webapp=1&amp;sender_device=pc" target="_blank" rel="noopener noreferrer">@veilocity_rising</a><a href="https://www.tiktok.com/@veilocity_?is_from_webapp=1&amp;sender_device=pc" target="_blank" rel="noopener noreferrer">@veilocity</a><a href="https://github.com/veilocity717-blip/VeilocityAndroid" target="_blank" rel="noopener noreferrer">GitHub</a><a href="mailto:stephencooke.c@gmail.com">Contact</a><a href="veilocity-downloads.html" class="archive-download-button">Download Archives</a></div></section>'''

SUPPORT_CSS = r'''.support-contacts .archive-download-button{white-space:normal;line-height:1.35;text-align:center}
.support-sidebar{background:#fff4e6;border:1px solid #efd5b9;border-radius:14px;padding:15px;color:#67594c;font-size:.94rem;overflow-wrap:anywhere}.support-sidebar h2{color:#307b78;font-size:1.12rem;margin:0 0 8px}.support-sidebar p{margin:0 0 12px}.support-sidebar strong{display:block;color:#df683b;margin:13px 0 5px}.support-sidebar code{display:block;overflow-wrap:anywhere;background:#f9e2c9;border:1px solid #edc9a7;border-radius:9px;padding:9px;font:0.76rem/1.5 monospace}.support-sidebar button,.support-sidebar .support-pill,.support-contacts a{display:inline-block;margin:7px 0 0;border:1px solid #e6d5c1;border-radius:20px;padding:7px 10px;background:#fffaf3;color:#307b78;font:600 .82rem system-ui,sans-serif;text-decoration:none;cursor:pointer}.support-sidebar button:hover,.support-sidebar a:hover{background:#e7f0ec}.support-contacts{display:flex;flex-wrap:wrap;gap:5px}.support-sidebar #support-status{font-size:.78rem;min-height:1em;margin-top:7px}.support-sidebar .support-hint{font-size:.84rem}'''

SUPPORT_JS = r'''<script id="veilocity-support-script">(()=>{async function copy(id){const v=document.getElementById(id).textContent;try{if(!navigator.clipboard?.writeText)throw Error();await navigator.clipboard.writeText(v);return true}catch(e){const t=document.createElement('textarea');t.value=v;t.style.position='fixed';t.style.opacity='0';document.body.append(t);t.select();let ok=false;try{ok=document.execCommand('copy')}catch(e){}t.remove();return ok}}const status=document.getElementById('support-status');document.getElementById('copy-btc')?.addEventListener('click',async()=>{status.textContent=await copy('support-btc')?'Bitcoin address copied.':'Select and copy the address above.'});document.getElementById('copy-paypal')?.addEventListener('click',async()=>{const ok=await copy('support-paypal');status.textContent=ok?'PayPal address copied.':'Select and copy the PayPal address above.';})})();</script>'''


LOGO2_CSS = r'''/* Veilocity secondary badge: top-right of main content */
.content{position:relative}
.veilocity-logo2{position:absolute;top:4px;right:4px;width:clamp(68px,9.75vw,128px);height:auto;object-fit:contain;clip-path:circle(49% at 50% 50%);z-index:1;filter:drop-shadow(0 5px 8px #55412e25)}
.content>header{padding-right:clamp(85px,12vw,145px);min-height:100px}
@media(max-width:760px){.veilocity-logo2{width:80px;top:0;right:0}.content>header{padding-right:95px;min-height:90px}}
@media(max-width:430px){.veilocity-logo2{width:62px}.content>header{padding-right:75px;min-height:70px}}
'''


def update_logo2(index_path: Path) -> None:
    """Add/update optional logo2 without disturbing the existing page."""
    html = index_path.read_text(encoding='utf-8')
    html = re.sub(r'<img\b[^>]*\bid=["\']veilocity-logo2["\'][^>]*>', '', html, flags=re.I)
    html = re.sub(r'/\* Veilocity secondary badge: top-right of main content \*/.*?(?=</style>)', '', html, flags=re.S)
    html = html.replace('</style>', '\n'+LOGO2_CSS+'\n</style>', 1)
    # Relative asset works with file:// and local offline servers.
    if (index_path.parent / 'logo2.png').is_file():
        badge = '<img id="veilocity-logo2" class="veilocity-logo2" src="logo2.png" alt="Veilocity circular badge">'
        html, n = re.subn(r'(<section\s+class="content"[^>]*>)', lambda m: m.group(1)+badge, html, count=1)
        if not n:
            print('WARNING: Main content section not found; logo2 not inserted.')
        else:
            print('LOGO2: top-right badge enabled.')
    else:
        print('LOGO2: optional logo2.png not present in archive root; badge omitted.')
    index_path.write_text(html, encoding='utf-8')


def update_existing_index(index_path: Path) -> bool:
    """Move support into the existing left sidebar, reusing the existing logo."""
    import re
    html = index_path.read_text(encoding='utf-8')
    # Refresh legacy GitHub links and Gmail button labels throughout an existing page.
    html = html.replace('https://github.com/veilocity717-blip/VeilocityAndroidAndroid',
                        'https://github.com/veilocity717-blip/VeilocityAndroid')
    html = re.sub(r"https://github[.]com/veilocity717-blip/Veilocity(?=[/\"\'?#]|$)",
                  'https://github.com/veilocity717-blip/VeilocityAndroid', html, flags=re.I)
    html = re.sub(r"(<a\\b[^>]*href=[\"\']mailto:stephencooke[.]c@gmail[.]com[\"\'][^>]*>)\\s*Gmail\\s*(</a>)",
                  r'\\1Contact\\2', html, flags=re.I)
    # Remove any earlier main-column panel, including its duplicate QR artwork.
    html = re.sub(r'<section class="support-panel".*?</section>', '', html, flags=re.S)
    # Remove previous sidebar version, if updating this script repeatedly.
    html = re.sub(r'<section class="support-sidebar".*?</section>', '', html, flags=re.S)
    html = re.sub(r'<script id="veilocity-support-script">.*?</script>', '', html, flags=re.S)
    # Retire the old main-panel artwork and BTC event handlers; they refer to removed elements.
    html = re.sub(r"if\(config\.logo\)\{const artwork=.*?\.append\(artwork\);\}", '', html, flags=re.S)
    html = re.sub(r"const copyBtn=document\.getElementById\('copy-btc'\);.*?\}\);", '', html, flags=re.S)
    # Remove previously generated direct links before reinserting on reruns.
    html = re.sub(r'<details\s+id="veilocity-direct-downloads".*?</details>', '', html, flags=re.S | re.I)
    html = re.sub(r'/\* Direct archive links on the main landing page \*/.*?(?=</style>)', '', html, flags=re.S)
    # Refresh the shared Android-style navigation without duplicating it on reruns.
    html = re.sub(r'<nav\s+class="veilocity-app-actions".*?</nav>', '', html, flags=re.S | re.I)
    html = re.sub(r'/\* Veilocity shared app action buttons \*/.*?(?=</style>)', '', html, flags=re.S)
    # Do not show the expandable download links beneath the Court button.
    # Archive downloads remain accessible via the sidebar button.
    html = html.replace('</style>', '\n'+NAV_CSS+'\n</style>', 1)
    # Existing sidebar contains the logo and side-note. Append beneath both.
    match = re.search(r'</aside>', html, re.I)
    if not match:
        print('WARNING: No sidebar found; index.html unchanged.')
        return False
    html = html[:match.start()] + SUPPORT_SIDEBAR + html[match.start():]
    html = re.sub(r'/\* veilocity sidebar support \*/.*?(?=</style>)', '', html, flags=re.S)
    html = html.replace('</style>', '\n/* veilocity sidebar support */\n'+SUPPORT_CSS+'\n</style>', 1)
    html = html.replace('</body>', SUPPORT_JS+'</body>', 1)
    index_path.write_text(html, encoding='utf-8')
    print('UPDATED LANDING PAGE: sidebar support, copy-only PayPal and Bitcoin controls.')
    return True


def build(root: Path, write_index: bool = False) -> None:
    directories = sorted(
        (p for p in root.iterdir() if p.is_dir() and ARCHIVE_FOLDER_RE.match(p.name)),
        key=lambda p: natural_key(p.name),
    )
    # Court is a standalone text link, not a language-grid card.
    included = []
    for directory in directories:
        # Recursive file listing supports asset subfolders, but the primary HTML
        # and flag may also be inside subfolders.
        files = sorted(
            (p.relative_to(directory).as_posix() for p in directory.rglob("*")
             if p.is_file() and p.name != "manifest.js"),
            key=natural_key,
        )
        is_court = directory.name == COURT_FOLDER
        country = "Court of Illusions — Trafficking" if is_court else get_country(directory.name)
        if is_court:
            # The original Court HTML references a sibling *_Files asset directory.
            # Do not rename or move those assets when preparing the offline archive.
            primary = COURT_HTML if COURT_HTML in files else ""
        else:
            primary = choose_primary(files, country)
        if not primary:
            expected = COURT_HTML if is_court else "a non-court HTML file"
            print(f"SKIP {directory.name}: missing {expected}")
            continue
        manifest = {
            "country": country,
            "language": country,
            "version": "Featured" if is_court else get_version(directory.name),
            "flag": "" if is_court else find_flag(files),
            "primary_html": primary,
            "description": "Court of Illusions — Trafficking: English court archive" if is_court else f"{country} portable archive",
            "item_count": len(files),
            "files": files,
        }
        js = (
            "window.VEILOCITY_MANIFESTS = window.VEILOCITY_MANIFESTS || {};\n"
            f"window.VEILOCITY_MANIFESTS[{json.dumps(directory.name, ensure_ascii=False)}] = "
            f"{js_literal(manifest)};\n"
        )
        (directory / "manifest.js").write_text(js, encoding="utf-8")
        included.append(directory.name)
        print(f"OK   {directory.name}: {primary} | flag: {manifest['flag'] or 'none'}")

    archives_js = "window.VEILOCITY_ARCHIVES = " + js_literal({"archives": included, "logo": find_logo(root, directories)}) + ";\n"
    (root / "archives.js").write_text(archives_js, encoding="utf-8")
    index_path = root / "index.html"
    if write_index or not index_path.exists():
        court_file = root / COURT_FOLDER / COURT_HTML
        if not court_file.is_file():
            print(f"WARNING: Court HTML not found at {court_file}; the landing-page link will still be displayed.")
        index_path.write_text(INDEX_HTML, encoding="utf-8")
        update_existing_index(index_path)
        print(f"UPDATED LANDING PAGE: {index_path}")
        print("COURT BUTTON: embedded before Support Veilocity and search")
        print("Wrote index.html (default offline landing page).")
    else:
        update_existing_index(index_path)
    # The downloads page is regenerated from the Android v2.8.18 links each run.
    (root / "veilocity-downloads.html").write_text(DOWNLOADS_HTML, encoding="utf-8")
    print("DOWNLOADS PAGE: veilocity-downloads.html (MEGA volumes + Google Drive)")
    update_logo2(index_path)
    print(f"LANDING PAGE PATH: {index_path}")
    print(f"COURT HTML EXISTS: {(root / COURT_FOLDER / COURT_HTML).is_file()}")
    print(f"COURT BUTTON IN INDEX: {'court-link-wrap' in index_path.read_text(encoding='utf-8')}")
    print(f"\nWrote archives.js with {len(included)} archive(s).")
    if not included:
        print("No eligible archive folders found. Expected language vNNN folders or court-of-illusions-trafficking/ENGLISH - Court.html.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent,
                        help="Directory containing archive folders (default: script directory)")
    parser.add_argument("--write-index", action="store_true",
                        help="Overwrite index.html with the English-inspired peach and cream design")
    args = parser.parse_args()
    build(args.root.expanduser().resolve(), write_index=args.write_index)
