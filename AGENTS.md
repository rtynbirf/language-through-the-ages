# AGENTS.md

Instructions for AI coding agents working in this repository.

## Project overview

Автономная HTML-экспозиция «Язык сквозь эпохи»: семь способов мыслить язык —
от логоса к телесному предсказанию. 7 эпох × 7 гарнитур, эпистемические
комментарии отделяют историю от интерпретации. Правила аккаунта — в rtynbirf/repo-doctrine.

## Commands

Верификация пломб: `sha256sum -c SHA256SUMS.txt` (GNU).
Резерв артефактов: `language-through-the-ages.zip` (deflate -9).

## Conventions

- Keep changes minimal and focused; one logical change per commit.
- Never commit secrets, tokens, or credentials.
- Аддитивность: добавлять можно, удалять и переписывать — нельзя (доктрина, раздел 02).
- Артефакт v2 самодостаточен по разметке/CSS/JS; шрифты — CDN Google Fonts,
  офлайн-деградация на системные serif/sans. Зашить шрифты base64 — задача v2.1
  (по образцу web-evolution-1991-2026).
- После любых изменений артефакта — обновить SHA256SUMS и паспорт в README.
