# AGENTS.md

Instructions for AI coding agents working in this repository.

## Project overview

Автономная HTML-экспозиция «Язык сквозь эпохи»: семь способов мыслить язык —
от логоса к телесному предсказанию. 7 эпох × 7 гарнитур, эпистемические комментарии
отделяют историю от интерпретации. Ноль внешних запросов: 8 гарнитур (21 лицо)
зашиты base64 woff2 (подрезка pyftsubset по символам документа). Правила аккаунта — в rtynbirf/repo-doctrine.

## Commands

Верификация пломб: `sha256sum -c SHA256SUMS.txt` (GNU).
Резерв артефактов: `language-through-the-ages.zip` (deflate -9).

## Conventions

- Keep changes minimal and focused; one logical change per commit.
- Never commit secrets, tokens, or credentials.
- Аддитивность: добавлять можно, удалять и переписывать — нельзя (доктрина, раздел 02).
- Артефакт самодостаточен: правки текста — не руками в артефакте, а со сборкой
  и обновлением пломб; после любых изменений — SHA256SUMS + паспорт README.
- Если текст меняется — контроль идентичности прозы (слова в порядке, без искажений).
