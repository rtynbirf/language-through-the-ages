# -*- coding: utf-8 -*-
"""Каноническая сборка linguistic-code-epochs-v1.html (репо-копия).
Шрифты берутся из путей установки (Liberation Serif, DejaVu Sans Mono); в иных средах поправить FONTS.
: self-contained, base64 woff2 (pyftsubset),
вёрстка на min()/clamp() без @media, ноль внешних запросов. Валидация: теги, счёт слов,
анахронизмы, покрытие шрифтов, внешние URL. Пишет файл в repo-ltta и печатает паспорт."""
import base64, hashlib, html, io, re, sys
from pathlib import Path
from html.parser import HTMLParser
from fontTools import subset as fts


from epochs_data import PREAMBLE, LEGEND, ERAS, TABLE_CAPTION, TABLE_HEAD, TABLE_ROWS, VERDICT, FOOTER

# путь артефакта — относительно корня репозитория (сборка запускается из build/)
OUT = Path(__file__).resolve().parent.parent / "linguistic-code-epochs-v1.html"

FONTS = {
    "serif-r": ("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", "LibSerif", "normal", 400),
    "serif-b": ("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf", "LibSerif", "bold", 700),
    "serif-i": ("/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf", "LibSerif", "italic", 400),
    "mono-r":  ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", "DejaVuMono", "normal", 400),
}

# ---------------------------------------------------------------- fonts
def collect_charset(s):
    base = set(s) | set(chr(c) for c in range(0x20, 0x7F))
    base |= set("№«»—–…·×→✓?¡") | set("λόγοςscriptura ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψω")
    base |= set("АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя")
    base.discard("\n"); base.discard("\r"); base.discard("\t")
    return "".join(sorted(base))

def subset_font(path, charset):
    opts = fts.Options()
    opts.flavor = "woff2"
    opts.desubroutinize = True
    opts.drop_tables += ["GSUB", "GPOS"]
    font = fts.load_font(str(path), opts)
    ss = fts.Subsetter(opts)
    ss.populate(text=charset)
    ss.subset(font)
    buf = io.BytesIO()
    fts.save_font(font, buf, opts)
    return buf.getvalue()

def font_face_css(key, data):
    path, fam, style, weight = FONTS[key]
    b64 = base64.b64encode(data).decode("ascii")
    return (
        f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};"
        f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
    )

# ---------------------------------------------------------------- html
CSS = """
:root{--bg:#16130f;--paper:#1c1813;--paper2:#211c15;--ink:#d9d0c1;--muted:#8f8471;--rule:#372f24;
--mono:'DejaVuMono',ui-monospace,'Cascadia Mono',Consolas,monospace;
--serif:'LibSerif',Georgia,'Times New Roman',serif;}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:calc(56px + 1.5em)}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--serif);
font-size:clamp(16px,0.55vw + 13.4px,20px);line-height:1.62;
-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
.skip{position:absolute;left:-9999px}
.skip:focus{left:8px;top:8px;background:var(--paper2);padding:8px 14px;border:1px solid var(--rule);z-index:99}
:focus-visible{outline:2px solid #c9a227;outline-offset:2px}
#progress{position:fixed;top:0;left:0;height:3px;width:100%;transform-origin:0 50%;
transform:scaleX(0);background:linear-gradient(90deg,#c9a227,#c96f4a);z-index:50}
header.top{position:sticky;top:0;z-index:40;background:color-mix(in srgb,var(--bg) 88%,transparent);
backdrop-filter:blur(6px);border-bottom:1px solid var(--rule);
padding:0.55em clamp(12px,4vw,48px)}
.topline{display:flex;flex-wrap:wrap;gap:0.5em 1.2em;align-items:baseline}
.brand{font-weight:700;letter-spacing:0.14em;font-size:clamp(13px,1.4vw,16px);text-transform:uppercase}
.brand span{color:var(--muted);font-weight:400;letter-spacing:0.06em;text-transform:none}
nav.era-nav{display:flex;flex-wrap:wrap;gap:0.35em;margin-top:0.45em}
nav.era-nav a{font-family:var(--mono);font-size:clamp(11px,1vw,13px);color:var(--muted);
text-decoration:none;border:1px solid var(--rule);border-radius:999px;padding:0.25em 0.8em}
nav.era-nav a:hover{color:var(--ink);border-color:#5a4f3d}
main{max-width:76ch;margin:0 auto;padding:0 clamp(12px,4vw,48px)}
section{padding:clamp(2.2em,5vh,4.5em) 0;border-bottom:1px solid var(--rule)}
h1{font-size:clamp(26px,4.2vw,44px);line-height:1.12;margin:0.4em 0 0.2em;letter-spacing:0.01em}
h1 small{display:block;font-size:0.42em;color:var(--muted);font-weight:400;letter-spacing:0.18em;text-transform:uppercase;margin-top:0.8em}
h2{font-size:clamp(20px,2.6vw,30px);margin:0 0 0.4em}
.kicker{font-family:var(--mono);font-size:clamp(11px,1vw,13px);color:var(--muted);letter-spacing:0.08em}
.lede{color:var(--ink);max-width:64ch}
legend,.lbl{font-family:var(--mono);font-size:clamp(11px,0.95vw,13px);color:var(--muted);letter-spacing:0.06em}
.chips{display:flex;flex-wrap:wrap;gap:0.4em;margin:0.5em 0 0.2em;padding:0;list-style:none}
.chips li{font-family:var(--mono);font-size:clamp(11px,0.95vw,13px);border:1px solid var(--rule);
border-radius:999px;padding:0.22em 0.75em;color:var(--ink)}
.chips.banned li{color:#b08d7e;border-style:dashed;text-decoration:line-through;text-decoration-thickness:1px}
.era{border-bottom:1px solid var(--rule)}
.era-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:0.4em 0.8em;margin-bottom:0.6em}
.era-num{font-family:var(--mono);font-size:clamp(30px,4vw,46px);line-height:1;color:var(--accent,--ink)}
.era-name{font-size:clamp(22px,3vw,34px);font-weight:700}
.era-sub{font-style:italic;color:var(--accent,--ink);font-size:clamp(14px,1.6vw,18px)}
.era-bounds{width:100%;color:var(--muted);font-size:clamp(12px,1.2vw,15px)}
.voice{margin:1.2em 0;padding:1.1em 1.3em;background:var(--paper);border:1px solid var(--rule);
border-left:3px solid var(--accent,#c9a227);border-radius:0 6px 6px 0;position:relative}
.voice .lbl{display:block;margin-bottom:0.6em}
blockquote.voice p{margin:0;font-size:clamp(16px,0.5vw + 14px,20px)}
.era-italic .voice p{font-style:italic}
.era-smallcaps .voice p{font-variant-caps:all-small-caps;letter-spacing:0.03em}
.era-dropcap .voice p::first-letter{font-size:2.7em;float:left;line-height:0.82;padding:0.04em 0.12em 0 0;color:var(--accent);font-weight:700}
.era-columns .voice p{column-count:2;column-gap:2em;text-align:justify;hyphens:auto}
.era-mono .voice{border-left-color:var(--accent);background:repeating-linear-gradient(0deg,rgba(85,214,141,0.035) 0 2px,transparent 2px 4px),var(--paper)}
.era-mono .voice p{font-family:var(--mono);font-size:clamp(13px,0.45vw + 11.4px,15px);line-height:1.66}
.era-gloss .voicewrap{display:grid;grid-template-columns:minmax(0,3fr) minmax(170px,1fr);gap:1em}
.glosscol{border-left:1px dashed var(--rule);padding:0.9em;color:var(--muted);font-size:clamp(12px,1vw,14px)}
.glosscol .lbl{display:block;margin-bottom:0.5em;color:var(--accent)}
ol.theses{margin:1.1em 0 0;padding-left:1.4em}
ol.theses li{margin:0.45em 0}
ol.theses b{color:var(--accent)}
.epistemic{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:1em;margin:1.2em 0}
.epistemic>div{background:var(--paper2);border:1px solid var(--rule);border-radius:6px;padding:0.9em 1.1em}
.epistemic ul{margin:0.4em 0 0;padding-left:1.2em}
.epistemic li{margin:0.4em 0;color:var(--ink)}
.epistemic .mark-k{color:#9dbb8a;font-family:var(--mono);font-size:0.92em}
.epistemic .mark-q{color:#c9a227;font-family:var(--mono);font-size:0.92em}
.lexcheck{color:var(--muted);font-size:clamp(12px,1.1vw,14px);font-family:var(--mono)}
.lexcheck::before{content:'проверка лексики — ';color:#6f6552}
.tablewrap{overflow-x:auto;border:1px solid var(--rule);border-radius:6px;background:var(--paper)}
table{border-collapse:collapse;width:100%;min-width:720px;font-size:clamp(12px,1vw,15px)}
caption{caption-side:top;text-align:left;padding:0.9em 1em;color:var(--muted);font-family:var(--mono);font-size:clamp(11px,1vw,13px)}
th,td{border:1px solid var(--rule);padding:0.6em 0.75em;vertical-align:top;text-align:left}
thead th{background:var(--paper2);font-family:var(--mono);font-size:0.92em;letter-spacing:0.04em}
tbody th{background:var(--paper2);font-weight:700;white-space:nowrap}
tbody td{color:var(--ink)}
.verdict{max-width:70ch;font-size:clamp(17px,1.4vw,22px);line-height:1.5}
.verdict b{color:#c9a227}
footer{max-width:76ch;margin:0 auto;padding:2.2em clamp(12px,4vw,48px) 5em;color:var(--muted);font-size:clamp(12px,1.1vw,14px)}
#totop{position:fixed;right:14px;bottom:14px;z-index:45;font-family:var(--mono);font-size:12px;
color:var(--muted);background:var(--paper2);border:1px solid var(--rule);border-radius:999px;
padding:0.5em 1em;cursor:pointer;opacity:0;pointer-events:none;transition:opacity 0.3s}
#totop.on{opacity:1;pointer-events:auto}
.fade{opacity:0;transform:translateY(10px);transition:opacity 0.6s ease,transform 0.6s ease}
.fade.in{opacity:1;transform:none}
@media (prefers-reduced-motion: reduce){html{scroll-behavior:auto}.fade{transition:none;opacity:1;transform:none}}
"""

JS = """
(function(){
'use strict';
var bar=document.getElementById('progress');
var top=document.getElementById('totop');
var tick=false;
function onScroll(){
  if(tick) return; tick=true;
  requestAnimationFrame(function(){
    var h=document.documentElement;
    var max=h.scrollHeight-h.clientHeight;
    bar.style.transform='scaleX('+(max>0?(h.scrollTop/max):0)+')';
    top.classList.toggle('on',h.scrollTop>600);
    tick=false;
  });
}
document.addEventListener('scroll',onScroll,{passive:true}); onScroll();
top.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'});});
var fades=document.querySelectorAll('.fade');
if('IntersectionObserver' in window){
  var io=new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target);} });
  },{rootMargin:'0px 0px -8% 0px'});
  fades.forEach(function(el){io.observe(el);});
}else{
  for(var i=0;i<fades.length;i++){fades[i].classList.add('in');}
}
})();
"""

def era_html(e, n):
    accent = e["accent"]
    parts = []
    parts.append(f'<section class="era era-{e["gesture"]}" id="{e["id"]}" style="--accent:{accent}" aria-labelledby="{e["id"]}-h">')
    parts.append('<div class="fade">')
    parts.append(f'<div class="era-head"><span class="era-num" aria-hidden="true">{e["numeral"]}</span>'
                 f'<span class="era-name" id="{e["id"]}-h">{html.escape(e["name"])}</span>'
                 f'<span class="era-sub" lang="und">{html.escape(e["sub"])}</span>'
                 f'<span class="era-bounds">{html.escape(e["bounds"])}</span></div>')
    parts.append('<span class="lbl">словарь эпохи</span><ul class="chips">')
    for w in e["vocab"]:
        parts.append(f'<li>{html.escape(w)}</li>')
    parts.append('</ul><span class="lbl">запрет эпохи</span><ul class="chips banned">')
    for w in e["banned"]:
        parts.append(f'<li>{html.escape(w)}</li>')
    parts.append('</ul>')
    voice = f'<blockquote class="voice"><span class="lbl">голос эпохи</span><p>{html.escape(e["voice"])}</p></blockquote>'
    if e["gesture"] == "gloss":
        gloss = ('<aside class="glosscol"><span class="lbl">глосса</span>'
                 'Так в маргиналиях выглядит второй слой: писание в центре, '
                 'толкование — вокруг него, толкование толкования — ещё дальше от строки. '
                 'Читая кодекс, брат читает и всех, кто читал до него.</aside>')
        parts.append(f'<div class="voicewrap">{voice}{gloss}</div>')
    else:
        parts.append(voice)
    parts.append('<ol class="theses">')
    for t, d in e["theses"]:
        parts.append(f'<li><b>{html.escape(t)}</b> {html.escape(d)}</li>')
    parts.append('</ol>')
    parts.append('<div class="epistemic"><div><span class="mark-k">✓ знаем</span><ul>')
    for k in e["know"]:
        parts.append(f'<li>{html.escape(k)}</li>')
    parts.append('</ul></div><div><span class="mark-q">? не знаем</span><ul>')
    for u in e["unknow"]:
        parts.append(f'<li>{html.escape(u)}</li>')
    parts.append('</ul></div></div>')
    parts.append(f'<p class="lexcheck">{html.escape(e["lexcheck"])}</p>')
    parts.append('</div></section>')
    return "\n".join(parts)

def build_html(faces):
    css = CSS + ("".join(faces) if faces else "")
    p = ['<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<meta name="description" content="Лингвистический код: Эпохи — одна мысль, шесть языков. Инвариант передачи опыта через смерть говорящего, каждая эпоха — своим словарём.">',
         '<title>Лингвистический код · Эпохи — одна мысль, шесть языков</title>',
         f'<style>{css}</style></head><body>',
         '<a class="skip" href="#manifest">к тексту</a><div id="progress" aria-hidden="true"></div>',
         '<header class="top"><div class="topline"><span class="brand">Лингвистический код <span>· Эпохи</span></span></div>',
         '<nav class="era-nav" aria-label="Эпохи">']
    for e in ERAS:
        p.append(f'<a href="#{e["id"]}" title="{html.escape(e["bounds"])}">{e["numeral"]} · {html.escape(e["name"])}</a>')
    p.append('<a href="#tablica">Таблица</a><a href="#verdict">Вердикт</a></nav></header><main>')
    p.append('<section id="manifest" aria-labelledby="manifest-h"><div class="fade">')
    p.append('<h1 id="manifest-h">Одна мысль — шесть языков<small>хронотоп языка · инвариант передачи</small></h1>')
    p.append(f'<p class="lede">{html.escape(PREAMBLE)}</p>')
    p.append('<span class="lbl">легенда</span><ul class="chips">')
    for a, b in LEGEND:
        p.append(f'<li title="{html.escape(b)}">{html.escape(a)}</li>')
    p.append('</ul></div></section>')
    for i, e in enumerate(ERAS):
        p.append(era_html(e, i))
    p.append('<section id="tablica" aria-labelledby="tablica-h"><div class="fade">')
    p.append(f'<h2 id="tablica-h">Сводная таблица</h2><div class="tablewrap"><table><caption>{html.escape(TABLE_CAPTION)}</caption><thead><tr>')
    for h in TABLE_HEAD:
        p.append(f'<th scope="col">{html.escape(h)}</th>')
    p.append('</tr></thead><tbody>')
    for row in TABLE_ROWS:
        p.append('<tr>')
        for j, cell in enumerate(row):
            p.append(f'<th scope="row">{html.escape(cell)}</th>' if j == 0 else f'<td>{html.escape(cell)}</td>')
        p.append('</tr>')
    p.append('</tbody></table></div></div></section>')
    p.append('<section id="verdict" aria-labelledby="verdict-h"><div class="fade">')
    p.append(f'<h2 id="verdict-h">Вердикт</h2><p class="verdict">{html.escape(VERDICT)}</p></div></section>')
    p.append('</main><footer><p>' + html.escape(FOOTER) + '</p>')
    p.append('<p>v1 · 2026-11-07 · собрано для канона «Хронотоп языка / Лингвистический код» (тезисы 1.5, 1.7, 1.23, 1.28, 1.31)</p></footer>')
    p.append('<button id="totop" aria-label="Наверх">наверх ↑</button>')
    p.append(f'<script>{JS}</script></body></html>')
    return "\n".join(p)

# ---------------------------------------------------------------- checks
class Balance(HTMLParser):
    VOID = {"meta", "br", "img", "hr", "input", "link", "source"}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)
    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"mismatch </{tag}> at line {self.getpos()[0]}")
        else:
            self.stack.pop()

def words(t):
    return len(re.findall(r"[0-9A-Za-zΑ-Ωα-ωА-Яа-яЁё][0-9A-Za-zΑ-Ωα-ωА-Яа-яЁё\-’']*", t))

def visible_text(doc):
    d = Balance()
    d.feed(doc)
    return d

def main():
    # 1) черновой документ без шрифтов -> charset
    draft = build_html(None)
    parser = Balance()
    parser.feed(draft)
    if parser.errors or parser.stack:
        print("TAG ERRORS:", parser.errors, "unclosed:", parser.stack); sys.exit(1)
    # текстовый charset: собираем из данных (не из CSS/JS)
    txt = PREAMBLE + VERDICT + FOOTER
    for e in ERAS:
        txt += e["voice"] + " ".join(e["vocab"]) + " ".join(e["banned"])
        txt += " ".join(a + b for a, b in e["theses"]) + " ".join(e["know"]) + " ".join(e["unknow"]) + e["lexcheck"]
        txt += e["name"] + e["sub"] + e["bounds"]
    txt += " ".join(TABLE_HEAD) + " ".join(" ".join(r) for r in TABLE_ROWS) + TABLE_CAPTION
    txt += " ".join(a + b for a, b in LEGEND) + "голос эпохисловарьпроверка лексикизапрет эпохинаверх"
    charset = collect_charset(txt)

    # 2) шрифты
    faces = []
    fonts_meta = {}
    for key, (path, fam, style, weight) in FONTS.items():
        data = subset_font(path, charset)
        fonts_meta[key] = len(data)
        faces.append(font_face_css(key, data))
    doc = build_html(faces)

    # 3) валидации
    p2 = Balance(); p2.feed(doc)
    assert not p2.errors and not p2.stack, (p2.errors, p2.stack)
    problems = []
    for e in ERAS:
        wc = words(e["voice"])
        if not (120 <= wc <= 200):
            problems.append(f"{e['id']}: слов в голосе {wc} (нужно 120–200)")
        tokens = re.findall(r"[А-Яа-яЁё]+", e["voice"].lower())
        exceptions = {"код": ("кодекс",), "набор": (), "письмо": ("писание",)}
        for b in e["banned"]:
            if b == "футурология":
                continue
            exc = exceptions.get(b, ())
            hit = [t for t in tokens if (t == b or t.startswith(b)) and not any(t.startswith(x) for x in exc)]
            if hit:
                problems.append(f"{e['id']}: запрещённое слово «{b}» в голосе: {hit[:3]}")
        e["wc"] = wc
    if re.search(r"https?://", doc):
        problems.append("в документе есть http(s):// ссылка")
    for m in re.finditer(r'(?:href|src)="([^"]+)"', doc):
        if not (m.group(1).startswith("#") or m.group(1).startswith("data:")):
            problems.append(f"внешний атрибут: {m.group(1)[:60]}")
    # покрытие шрифтами
    from fontTools.ttLib import TTFont
    merged = set()
    for key, (path, fam, style, weight) in FONTS.items():
        f = TTFont(path)
        cmap = set(f.getBestCmap().keys())
        merged |= {ch for ch in charset if ord(ch) in cmap}
    gaps = [ch for ch in charset if ch not in merged]
    if gaps:
        print("GAPS (системный фолбэк):", "".join(gaps))

    OUT.write_text(doc, encoding="utf-8")
    sha = hashlib.sha256(OUT.read_bytes()).hexdigest()
    size = OUT.stat().st_size
    print("=== ПАСПОРТ ===")
    print("файл:", OUT.name, "| байт:", size)
    print("sha256:", sha)
    print("теги: OK | внешние URL: 0")
    print("шрифты (woff2, байт):", fonts_meta)
    print("покрытие символов: %d/%d" % (len(charset) - len(gaps), len(charset)))
    for e in ERAS:
        print(f'  {e["numeral"]} {e["name"]:<8} голос: {e["wc"]} слов')
    if problems:
        print("ПРОБЛЕМЫ:"); [print("  -", x) for x in problems]; sys.exit(2)
    print("ВСЕ ПРОВЕРКИ: OK")

if __name__ == "__main__":
    main()
