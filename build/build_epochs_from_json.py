#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Детерминированная сборка экспозиции из данных (ПРЕДЛОЖЕНИЕ-41, issue #3).

data/epochs.json — единственный источник контента; этот скрипт (только stdlib)
рендерит из него HTML и MD. Детерминизм — честность экспозиции:
  - часов и случайности нет вовсе (никаких time/random/uuid);
  - порядок эпох/строк — порядок в JSON (фиксирован файлом), множеств не
    возникает; ключи манифеста сортируются (sort_keys=True);
  - идентификаторы секций — id эпох из данных (стабильны);
  - двойная сборка подряд = байт-идентичные артефакты (selftest_epochs.py).

Подвал страницы = пломба == манифест: JSON-манифест (script type=application/json
+ человекочитаемая таблица) с sha256 данных, сборщика и MD-артефакта. Хеш самого
HTML самовнутрь не влезает — он попадает в SHA256SUMS.txt после сборки.

Выход: linguistic-code-epochs-v2.html / .md в корне репо (артефакты коммитятся).
Режим --check: пересборка и байт-сравнение с закоммиченными (гейт docs-drift).
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "epochs.json"
OUT_HTML = REPO / "linguistic-code-epochs-v2.html"
OUT_MD = REPO / "linguistic-code-epochs-v2.md"
BUILDER = Path(__file__).resolve()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def esc(s: str) -> str:
    return html.escape(s, quote=True)


# ------------------------------------------------------------------ HTML
CSS = """
:root{--bg:#16130f;--paper:#1c1813;--ink:#d9d0c1;--muted:#8f8471;--rule:#372f24;
--mono:'DejaVu Mono',ui-monospace,Consolas,monospace;--serif:Georgia,'Times New Roman',serif}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font-family:var(--serif);font-size:clamp(16px,.55vw + 13.4px,20px);line-height:1.62}
header.top{position:sticky;top:0;background:rgba(22,19,15,.92);border-bottom:1px solid var(--rule);
padding:.55em clamp(12px,4vw,48px)}
.brand{font-weight:700;letter-spacing:.14em;font-size:clamp(13px,1.4vw,16px);text-transform:uppercase}
nav.era-nav{display:flex;flex-wrap:wrap;gap:.35em;margin-top:.45em}
nav.era-nav a{font-family:var(--mono);font-size:clamp(11px,1vw,13px);color:var(--muted);
text-decoration:none;border:1px solid var(--rule);border-radius:999px;padding:.25em .8em}
main{max-width:76ch;margin:0 auto;padding:0 clamp(12px,4vw,48px)}
section{padding:clamp(2.2em,5vh,4.5em) 0;border-bottom:1px solid var(--rule)}
h1{font-size:clamp(26px,4.2vw,44px);line-height:1.12;margin:.4em 0 .2em}
.kicker,.lbl{font-family:var(--mono);font-size:clamp(11px,.95vw,13px);color:var(--muted);letter-spacing:.08em}
.chips{display:flex;flex-wrap:wrap;gap:.4em;list-style:none;padding:.5em 0 0}
.chips li{font-family:var(--mono);font-size:clamp(11px,.95vw,13px);border:1px solid var(--rule);
border-radius:999px;padding:.22em .75em}
.chips.banned li{color:#b08d7e;border-style:dashed;text-decoration:line-through}
.voice{margin:1.2em 0;padding:1.1em 1.3em;background:var(--paper);border:1px solid var(--rule);
border-left:3px solid var(--accent,#c9a227);border-radius:0 6px 6px 0}
blockquote.voice p{margin:0}
.era-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:.4em .8em}
.era-num{font-family:var(--mono);font-size:clamp(30px,4vw,46px);line-height:1;color:var(--accent,#c9a227)}
.era-name{font-size:clamp(22px,3vw,34px);font-weight:700}
.era-sub{font-style:italic;color:var(--accent,#c9a227)}
.era-bounds{width:100%;color:var(--muted);font-size:clamp(12px,1.2vw,15px)}
table{border-collapse:collapse;width:100%;font-size:clamp(12px,1vw,15px)}
th,td{border:1px solid var(--rule);padding:.45em .6em;text-align:left;vertical-align:top}
th{font-family:var(--mono);color:var(--muted);font-weight:400}
footer{padding:2em clamp(12px,4vw,48px) 4em;color:var(--muted);font-family:var(--mono);
font-size:clamp(11px,.95vw,13px)}
footer pre{white-space:pre-wrap;background:var(--paper);border:1px solid var(--rule);
border-radius:6px;padding:1em;color:var(--ink)}
a{color:inherit}
"""


def manifest_common(data_bytes: bytes, n_eras: int) -> dict:
    """Общая часть пломбы-манифеста. Без self-ссылок и без ссылок на коммит:
    одинаковые данные + сборщик = одинаковые байты на любом коммите."""
    return {
        "builder": "build/build_epochs_from_json.py",
        "builder_sha256": sha256_bytes(BUILDER.read_bytes()),
        "data": "data/epochs.json",
        "data_sha256": sha256_bytes(data_bytes),
        "determinism": "двойная сборка = байт-идентично (selftest_epochs.py)",
        "eras": n_eras,
        "schema": "ltta.seal-manifest/1",
    }


def render_html(doc: dict, man: dict) -> bytes:
    e = esc
    nav = "".join(
        f'<a href="#{e(era["id"])}">{e(era["numeral"])}. {e(era["name"])}</a>'
        for era in doc["eras"]
    )
    parts: list[str] = []
    parts.append("<!doctype html>\n")
    parts.append('<html lang="ru">\n<head>\n<meta charset="utf-8">\n')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">\n')
    parts.append(f"<title>{e(doc['title'])}</title>\n")
    parts.append(f"<style>{CSS}</style>\n</head>\n<body>\n")
    parts.append('<header class="top"><div class="brand">Язык сквозь эпохи <span>· '
                 'семь способов мыслить язык · экспозиция-сиблинг</span></div>\n')
    parts.append(f'<nav class="era-nav">{nav}</nav></header>\n<main>\n')
    parts.append(f"<h1>{e(doc['title'])}</h1>\n")
    parts.append(f'<p class="lede">{e(doc["preamble"])}</p>\n')
    parts.append('<p class="lbl">легенда: ' + " · ".join(
        f"{e(term)} — {e(meaning)}" for term, meaning in doc["legend"]
    ) + "</p>\n")
    for era in doc["eras"]:
        parts.append(f'<section class="era" id="{e(era["id"])}">\n')
        parts.append('<div class="era-head">'
                     f'<span class="era-num">{e(era["numeral"])}</span>'
                     f'<span class="era-name">{e(era["name"])}</span>'
                     f'<span class="era-sub">{e(era["sub"])}</span>'
                     f'<span class="era-bounds">{e(era["bounds"])}</span></div>\n')
        parts.append('<ul class="chips">' + "".join(f"<li>{e(w)}</li>" for w in era["vocab"]) + "</ul>\n")
        parts.append('<p class="lbl">запрет эпохи:</p>\n')
        parts.append('<ul class="chips banned">' + "".join(f"<li>{e(w)}</li>" for w in era["banned"]) + "</ul>\n")
        parts.append('<blockquote class="voice" style="--accent:' + e(era["accent"]) + '">'
                     f'<span class="lbl">голос эпохи</span>\n<p>{e(era["voice"])}</p></blockquote>\n')
        parts.append('<p class="lbl">тезисы:</p>\n<ol>\n')
        for thesis, detail in era["theses"]:
            parts.append(f"<li><strong>{e(thesis)}</strong> {e(detail)}</li>\n")
        parts.append("</ol>\n")
        parts.append('<p class="lbl">✓ знаем:</p>\n<ul>\n')
        for k in era["know"]:
            parts.append(f"<li>{e(k)}</li>\n")
        parts.append("</ul>\n")
        parts.append('<p class="lbl">? не знаем:</p>\n<ul>\n')
        for u in era["unknow"]:
            parts.append(f"<li>{e(u)}</li>\n")
        parts.append("</ul>\n")
        parts.append(f'<p class="lbl">лексика: {e(era["lexcheck"])}</p>\n')
        parts.append("</section>\n")
    parts.append(f'<section><h2>{e(doc["table_caption"])}</h2>\n<table>\n<thead><tr>')
    parts.append("".join(f"<th>{e(h)}</th>" for h in doc["table_head"]))
    parts.append("</tr></thead>\n<tbody>\n")
    for row in doc["table_rows"]:
        parts.append("<tr>" + "".join(f"<td>{e(cell)}</td>" for cell in row) + "</tr>\n")
    parts.append("</tbody></table>\n")
    parts.append(f'<p><strong>Вердикт.</strong> {e(doc["verdict"])}</p>\n</section>\n</main>\n')
    # подвал = пломба == манифест (в HTML-версии — и хеш MD-артефакта)
    man_json = json.dumps(man, ensure_ascii=False, sort_keys=True, indent=1)
    parts.append("<footer>\n<p>Пломба-манифест (данные → артефакт, append-only, детерминированно):</p>\n")
    parts.append('<script type="application/json" id="seal-manifest">\n' + man_json + "\n</script>\n")
    parts.append("<pre>" + e(man_json) + "</pre>\n")
    parts.append(f"<p>{e(doc['footer_note'])}</p>\n</footer>\n</body>\n</html>\n")
    return "".join(parts).encode("utf-8")


def render_md(doc: dict, man: dict) -> bytes:
    lines: list[str] = []
    lines.append(f"# {doc['title']}\n")
    lines.append(doc["preamble"] + "\n")
    lines.append("**Легенда:** " + " · ".join(f"{t} — {m}" for t, m in doc["legend"]) + "\n")
    for era in doc["eras"]:
        lines.append(f"## {era['numeral']}. {era['name']} ({era['sub']}) — {era['bounds']}\n")
        lines.append(f"**Словарь эпохи:** {', '.join(era['vocab'])}\n")
        lines.append(f"**Запрет эпохи:** {', '.join(era['banned'])}\n")
        lines.append(f"> {era['voice']}\n")
        for thesis, detail in era["theses"]:
            lines.append(f"- **{thesis}** {detail}")
        lines.append("")
        lines.append("**✓ знаем:**\n")
        for k in era["know"]:
            lines.append(f"- {k}")
        lines.append("")
        lines.append("**? не знаем:**\n")
        for u in era["unknow"]:
            lines.append(f"- {u}")
        lines.append("")
        lines.append(f"*Лексика: {era['lexcheck']}*\n")
    lines.append(f"## {doc['table_caption']}\n")
    lines.append("| " + " | ".join(doc["table_head"]) + " |")
    lines.append("|" + "---|" * len(doc["table_head"]))
    for row in doc["table_rows"]:
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines.append(f"**Вердикт.** {doc['verdict']}\n")
    lines.append("## Пломба-манифест\n")
    lines.append("```json")
    lines.append(json.dumps(man, ensure_ascii=False, sort_keys=True, indent=1))
    lines.append("```\n")
    lines.append(doc["footer_note"] + "\n")
    return ("\n".join(lines).encode("utf-8"))


def build() -> tuple[bytes, bytes]:
    data_bytes = DATA.read_bytes()
    doc = json.loads(data_bytes.decode("utf-8"))
    common = manifest_common(data_bytes, len(doc["eras"]))
    # MD несёт общую часть манифеста (свой хеш в себя не влезает);
    # HTML как целое несёт и хеш MD — пломба == манифест.
    md_bytes = render_md(doc, common)
    man_html = dict(common)
    man_html["artifact_md"] = OUT_MD.name
    man_html["artifact_md_sha256"] = sha256_bytes(md_bytes)
    html_bytes = render_html(doc, man_html)
    return html_bytes, md_bytes


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Детерминированная сборка epochs-v2 из data/epochs.json")
    ap.add_argument("--check", action="store_true", help="пересобрать и сравнить с закоммиченными байтами")
    args = ap.parse_args(argv)

    html_bytes, md_bytes = build()
    if args.check:
        ok = True
        for path, fresh in ((OUT_HTML, html_bytes), (OUT_MD, md_bytes)):
            if not path.exists():
                print(f"CHECK FAIL: {path.name} не существует")
                ok = False
                continue
            if path.read_bytes() != fresh:
                print(f"CHECK FAIL: {path.name} расходится с пересборкой (docs-drift)")
                ok = False
            else:
                print(f"CHECK OK: {path.name} == пересборка байт-в-байт")
        return 0 if ok else 1

    OUT_HTML.write_bytes(html_bytes)
    OUT_MD.write_bytes(md_bytes)
    print(f"OK: {OUT_HTML.name} ({len(html_bytes)} B), {OUT_MD.name} ({len(md_bytes)} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
