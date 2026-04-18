# Vault Context — Personal Knowledge Base

## Purpose
This vault accumulates structured personal knowledge from raw sources (URLs, PDFs).
It is NOT a publishing system. All orchestration is done by Claude/agents; DeepSeek API handles extraction only.

## Working Directory
`e:/Xin_Tool/Claude Code/CC+Obsidian/` — this IS the Obsidian vault root AND Claude Code project root.

## Directory Structure
```
CC+Obsidian/
├── _raw_sources/          # Immutable scraped/PDF content (flat, never delete)
├── [topic-slug]/          # Processed notes per topic (e.g., vibe-coding/)
├── [topic].canvas         # Visual knowledge matrix (Obsidian Canvas JSON)
├── [topic].base           # Database view config (Obsidian Bases plugin)
├── config/
│   ├── extraction_prompts.json  # Last-used DeepSeek prompt + templates
│   └── topics.json              # Registered topics registry
└── scripts/
    └── intake.py          # Portable Python CLI for DeepSeek extraction
```

## File Naming Conventions

### Raw Sources (`_raw_sources/`)
Format: `YYYYMMDD_[source-domain]_[concept-slug].md`
Example: `20260418_arxiv_vibe-coding-intro.md`

### Processed Notes (`[topic-slug]/`)
Format: `YYYYMMDD_[concept-slug].md`
Example: `vibe-coding/20260418_llm-as-compiler.md`

## Note Frontmatter Schema
Every processed note MUST have this frontmatter:
```yaml
---
title: "Concept Title"
date: YYYY-MM-DD
source_url: "https://..."          # optional, if scraped from URL
source_raw: "_raw_sources/YYYYMMDD_domain_slug.md"
topic: topic-slug
tags: [topic-slug, relevant-tag]
summary: "One-sentence summary"
status: draft                      # draft | reviewed
---
```

## Canvas Node Format
Each node's `text` field in `.canvas` JSON:
```
**Concept Title**
_One-line summary_

[[note-filename]]
```
Groups represent subtopics. Edges represent relationships (labeled).
Max 2 levels: topic (Canvas file) → subtopic (group inside Canvas).

## Rules for Claude

1. **Always read `config/extraction_prompts.json` before any extraction step** — show the last-used prompt and ask user to confirm or modify.
2. **Always read `config/topics.json` before creating any topic folder** — check if topic is already registered.
3. **Always ask the user where to place nodes** on the Canvas — never auto-place without confirmation.
4. **Max 2 hierarchy levels** — if user requests deeper nesting, redirect to creating a new topic instead.
5. **Dedup check required** — before saving a new raw source, grep `_raw_sources/` and topic folders for keyword overlap.
6. **DeepSeek API is for extraction only** — Claude/agents handle all orchestration (steps 1, 2, 4, 5 of the intake workflow).

## Intake Workflow Summary
1. **Intake** — Scrape URL or read PDF → save to `_raw_sources/`
2. **Dedup** — Check for duplicate/related content
3. **Extract** — Run DeepSeek via `scripts/intake.py` (confirm prompt first)
4. **Canvas** — Ask user for placement → update `.canvas` JSON
5. **Done** — Print summary, offer to open `.base` view

## DeepSeek API
- Model: `deepseek-chat` (or `deepseek-reasoner` for complex topics)
- Base URL: `https://api.deepseek.com/v1` (OpenAI-compatible)
- Key: `DEEPSEEK_API_KEY` environment variable
- Note separator in output: `---NOTE---`

## Registered Topics
See `config/topics.json` for the current list of topics and their associated files.
