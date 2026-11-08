#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest детерминированной сборки (ПРЕДЛОЖЕНИЕ-41, issue #3) — только stdlib.

Приёмка машинная:
  1. двойная сборка подряд = байт-идентичные артефакты (HTML и MD);
  2. закоммиченные артефакты == пересборка (docs-drift не проходит);
  3. SHA256SUMS.txt пересчитан и совпадает по обоим артефактам;
  4. подвал = пломба == манифест: встроенный JSON манифеста воспроизводится
     из данных и сборщика (data_sha256/builder_sha256/artifact_md_sha256);
  5. в разметке нет часов (паттерн YYYY-MM-DD отсутствует).
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "build"))
import build_epochs_from_json as B  # noqa: E402

DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def fail(msg: str) -> int:
    print(f"SELFTEST FAIL: {msg}")
    return 1


def main() -> int:
    # 1. двойная сборка
    h1, m1 = B.build()
    h2, m2 = B.build()
    if h1 != h2 or m1 != m2:
        return fail("двойная сборка не байт-идентична")
    print("1 PASS: двойная сборка байт-идентична (HTML и MD)")

    # 2. закоммиченные артефакты == пересборка (плюс независимый subprocess --check)
    for path, fresh in ((B.OUT_HTML, h1), (B.OUT_MD, m1)):
        if not path.exists():
            return fail(f"{path.name} не закоммичен")
        if path.read_bytes() != fresh:
            return fail(f"{path.name} расходится с пересборкой")
    r = subprocess.run([sys.executable, str(BUILDER := B.BUILDER), "--check"], capture_output=True, text=True)
    if r.returncode != 0:
        return fail(f"--check вернул {r.returncode}:\n{r.stdout}{r.stderr}")
    print("2 PASS: закоммиченные артефакты == пересборка (включая subprocess --check)")

    # 3. SHA256SUMS
    sums = REPO / "SHA256SUMS.txt"
    entries: dict[str, str] = {}
    for line in sums.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, _, name = line.partition("  ")
            entries[name.strip()] = digest.strip()
    for path, fresh in ((B.OUT_HTML, h1), (B.OUT_MD, m1)):
        want = hashlib.sha256(fresh).hexdigest()
        got = entries.get(path.name)
        if got != want:
            return fail(f"SHA256SUMS: {path.name} = {str(got)[:12]}…, живой байт = {want[:12]}…")
    print("3 PASS: SHA256SUMS.txt пересчитан и совпадает (2 артефакта)")

    # 4. пломба == манифест
    doc = json.loads(B.DATA.read_bytes().decode("utf-8"))
    common = B.manifest_common(B.DATA.read_bytes(), len(doc["eras"]))
    md_man = json.loads(re.search(r"```json\n(.*?)\n```", B.OUT_MD.read_text(encoding="utf-8"), re.S).group(1))
    if md_man != common:
        return fail("манифест в MD не воспроизводится из данных+сборщика")
    html_text = B.OUT_HTML.read_text(encoding="utf-8")
    html_man = json.loads(re.search(
        r'<script type="application/json" id="seal-manifest">\n(.*?)\n</script>', html_text, re.S).group(1))
    want_html_man = dict(common)
    want_html_man["artifact_md"] = B.OUT_MD.name
    want_html_man["artifact_md_sha256"] = hashlib.sha256(m1).hexdigest()
    if html_man != want_html_man:
        return fail("манифест в HTML не воспроизводится (или не содержит хеш MD)")
    print("4 PASS: подвал = пломба == манифест (воспроизводим из данных и сборщика)")

    # 5. без часов
    for name, blob in ((B.OUT_HTML.name, h1), (B.OUT_MD.name, m1)):
        if DATE_RE.search(blob.decode("utf-8")):
            return fail(f"в {name} найден паттерн даты-времени — детерминизм под угрозой")
    print("5 PASS: часов в разметке нет (паттерн YYYY-MM-DD отсутствует)")

    print("SELFTEST PASS: сборка детерминированна, пломбы сходятся, SHA256SUMS честный")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
