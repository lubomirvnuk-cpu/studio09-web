#!/usr/bin/env python3
"""Vyrobí podstránky áut (auta/<slug>/index.html) z údajov v titulke (zoznam CARS v index.html)
a zo šablóny auta/_sablona.html. Fotky auta sú v auta/<slug>/foto/01.jpg, 02.jpg… (+ zmenšené v foto/m/).

Spustenie:  python3 auta/vyrob.py
Nová fotka/poradie: python3 auta/vyrob.py --fotky <slug> <zložka s originálmi> <IMG_1,IMG_2,...>
"""
import json, os, re, subprocess, sys, html
from urllib.parse import quote

KOREN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTA = os.path.join(KOREN, 'auta')
TEL = '421908714517'


def nacitaj_auta():
    s = open(os.path.join(KOREN, 'index.html'), encoding='utf-8').read()
    i = s.index('const CARS=[') + len('const CARS=')
    j = s.index('];', i) + 1
    js = 'const CARS=' + s[i:j] + ';process.stdout.write(JSON.stringify(CARS))'
    return json.loads(subprocess.run(['node', '-e', js], capture_output=True, text=True, check=True).stdout)


def eur(n):
    return f'{n:,}'.replace(',', ' ') + ' €'


def splatka(cena, ako=20, mes=84, urok=6.9):
    istina = cena * (1 - ako / 100); r = urok / 100 / 12
    return round(istina * r / (1 - (1 + r) ** -mes))


def qr_svg(text):
    import qrcode
    q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_L)
    q.add_data(text); q.make()
    m = q.get_matrix(); n = len(m)
    d = ''.join(f'M{x},{y}h1v1h-1z' for y, row in enumerate(m) for x, v in enumerate(row) if v)
    return f'<svg class="qr" viewBox="0 0 {n} {n}" shape-rendering="crispEdges" aria-hidden="true"><path d="{d}" fill="#0D1220"/></svg>'


AVAIL = {'skladom': 'Skladom', 'objednavka': 'Na objednávku', 'rezervovane': 'Rezervované',
         'pripravujeme': 'Pripravujeme', 'predane': 'Predané'}


def pocet_fotiek(slug):
    d = os.path.join(AUTA, slug, 'foto')
    return len([f for f in os.listdir(d) if re.fullmatch(r'\d\d\.jpg', f)]) if os.path.isdir(d) else 0


def stranka(c, vsetky, sablona):
    e = html.escape
    det = c.get('det', {})
    meno = f"{c['make']} {c['model']}"
    N = pocet_fotiek(c['slug'])
    specs = []
    for s in c['specs']:
        k, v = s[0], s[1]
        if k == 'Rok' and det.get('rok'): v = det['rok']
        hint = f' <small>{e(s[2])}</small>' if len(s) > 2 and s[2] else ''
        specs.append((k, e(v) + hint))
    specs += [(k, e(v)) for k, v in det.get('viac', [])]
    specs_html = ''.join(f'<div><dt>{e(k)}</dt><dd>{v}</dd></div>' for k, v in specs)
    tags = ''.join(f'<span>{e(t)}</span>' for t in c.get('tags', []))
    tags_html = f'<div class="au-tags">{tags}</div>' if tags else ''
    was = c.get('was')
    k = 'Cena s DPH' + (f' <s>{eur(was)}</s><b>−{eur(was - c["price"])}</b>' if was and was > c['price'] else '')
    bez = f'<span>{eur(round(c["price"] / 1.23))} bez DPH</span>' if 'Odpočet DPH' in c.get('tags', []) else ''
    price = (f'\n    <div class="k">{k}</div>\n    <strong>{eur(c["price"])}</strong>\n'
             f'    <p>alebo <b>{splatka(c["price"])} €</b> / mesiac{bez}</p>\n   ')
    wa = f'https://wa.me/{TEL}?text=' + quote(f'Dobrý deň, mám záujem o {meno} ({eur(c["price"]).replace(chr(160), " ")}).')
    vyb = det.get('vybava', '')
    vyb_html = f'<div><h2>Výbava</h2><p>{e(vyb)}</p></div>' if vyb else ''
    dalsie = [x for x in vsetky if x.get('slug') and x['id'] != c['id'] and x['avail'] == 'skladom'
              and pocet_fotiek(x['slug'])][:3]
    dal_html = ''
    if dalsie:
        dal_html = ('<section class="au3">\n <h2>Ďalšie autá skladom</h2>\n <div class="au-dal">\n' + ''.join(
            f'  <a href="../{x["slug"]}/"><img src="../{x["slug"]}/foto/m/01.jpg" alt="" loading="lazy"><b>{e(x["make"])}</b>'
            f'<i>{e(x["model"])}</i><span>{eur(x["price"])}</span></a>\n' for x in dalsie) + ' </div>\n</section>')
    th = ''.join(f'<button data-i="{i}"{" class=\"on\"" if i == 0 else ""}><img src="foto/m/{i + 1:02d}.jpg" alt="" loading="lazy">'
                 + (f'<span class="more">+{N - 7}</span>' if i == 7 and N > 8 else '') + '</button>' for i in range(min(N, 8)))
    grid = ''.join(f'<button data-i="{i}"><img src="foto/{"m/" if i else ""}{i + 1:02d}.jpg" alt="" loading="lazy"></button>' for i in range(N))
    km = next((s[1] for s in c['specs'] if s[0] == 'Najazdené'), '')
    rok = det.get('rok') or str(c.get('year', ''))
    title = f'{meno}, {rok}, {km} — {eur(c["price"])}'.replace(' ', ' ')
    desc = (f'{meno}, {rok}, {km}, {c["driveLabel"].lower()}, '
            + ', '.join(f'{k.lower()} {v}' for k, v in det.get('viac', [])[:2])
            + (', ' + ', '.join(t.lower() if t != 'Odpočet DPH' else 'možný odpočet DPH' for t in c.get('tags', [])) if c.get('tags') else '')
            + f'. {AVAIL[c["avail"]]} v Bratislave, cena {eur(c["price"])}.').replace(' ', ' ')
    r = {'TITLE': e(title), 'DESC': e(desc), 'SLUG': c['slug'], 'NAME': e(meno), 'CENA': eur(c['price']),
         'MAKE': e(c['make']), 'MODEL': e(c['model']), 'TAGS': tags_html, 'SPECS': specs_html, 'PRICE': price,
         'WAURL': wa, 'QR': qr_svg(wa), 'AVAIL': AVAIL[c['avail']], 'DRIVE': e(c['driveLabel']),
         'VYBAVA': vyb_html, 'DALSIE': dal_html, 'MAIN': f'<img src="foto/01.jpg" alt="{e(meno)}">',
         'TH': th, 'GRID': grid, 'N': str(N)}
    out = sablona
    for k_, v in r.items():
        out = out.replace('{{' + k_ + '}}', v)
    assert '{{' not in out, re.findall(r'\{\{\w+\}\}', out)
    return out


def fotky(slug, zdroj, poradie):
    from PIL import Image, ImageOps
    d = os.path.join(AUTA, slug, 'foto'); os.makedirs(os.path.join(d, 'm'), exist_ok=True)
    for f in os.listdir(d):
        if re.fullmatch(r'\d\d\.jpg', f): os.remove(os.path.join(d, f))
    for f in os.listdir(os.path.join(d, 'm')): os.remove(os.path.join(d, 'm', f))
    subory = {os.path.splitext(f)[0]: f for f in os.listdir(zdroj)}
    for i, meno in enumerate(poradie, 1):
        im = Image.open(os.path.join(zdroj, subory[meno])); im.draft('RGB', (1600, 1600))
        im = ImageOps.exif_transpose(im).convert('RGB'); im.thumbnail((1600, 1600))
        w, h = im.size
        if h > w * 3 / 4: t = round(w * 3 / 4); im = im.crop((0, (h - t) // 2, w, (h - t) // 2 + t))
        elif w > h * 4 / 3: t = round(h * 4 / 3); im = im.crop(((w - t) // 2, 0, (w - t) // 2 + t, h))
        im.thumbnail((1440, 1080))
        im.save(os.path.join(d, f'{i:02d}.jpg'), quality=76, optimize=True, progressive=True)
        m = im.copy(); m.thumbnail((560, 420))
        m.save(os.path.join(d, 'm', f'{i:02d}.jpg'), quality=72, optimize=True, progressive=True)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--fotky':
        fotky(sys.argv[2], sys.argv[3], sys.argv[4].split(','))
    auta = nacitaj_auta()
    sablona = open(os.path.join(AUTA, '_sablona.html'), encoding='utf-8').read()
    hotove = []
    for c in auta:
        if not c.get('slug') or not pocet_fotiek(c['slug']):
            continue
        p = os.path.join(AUTA, c['slug'], 'index.html')
        open(p, 'w', encoding='utf-8').write(stranka(c, auta, sablona))
        hotove.append(c['slug'])
    print('Hotové:', ', '.join(hotove))


if __name__ == '__main__':
    main()
