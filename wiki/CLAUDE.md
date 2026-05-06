# LLM Wiki — протокол за Claude

> Базирано на [Karpathy's LLM Wiki idea](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

## Архитектура

```
sources/              ← Layer 1: RAW. Не се редактират.
source-summaries/     ← Layer 2: 1 summary файл за всеки source.
entities/, concepts/  ← Layer 3: Synthesized знание от множество sources.
index.md              ← Layer 4: Каталог.
```

## Команди

- **"ingest wiki/sources/\<file\>"** → прочети, генерирай summary, обнови entities
- **"summarize what we know about \<topic\>"** → прочети entities/concepts и отговори
- **"recompile entities/\<name\>"** → регенерирай от всички sources

## Frontmatter за entity pages

```yaml
---
type: entity
kind: component | module | vehicle-system | concept
title: Заглавие
aliases: [алт. имена]
sources: [source-slug]
related: [entity-slug]
last_updated: YYYY-MM-DD
---
```

## Правила

- Не изтривай файлове от `sources/`
- Всяко твърдение citeва source
- При противоречие — запази старото с бележка, log в `log.md`
