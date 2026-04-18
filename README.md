# CC+Obsidian — Personal Knowledge Intake System

> **Claude Code + Obsidian + DeepSeek** · Structured personal knowledge accumulation from any URL or PDF

[中文文档](README.zh.md)

---

## What This Is

A personal knowledge management workflow that turns raw web content and PDFs into structured Obsidian notes — with visual Canvas maps and database views — using AI extraction.

**Not a publishing tool.** This is a private knowledge base engine.

```
URL / PDF
    ↓  scrape (defuddle CLI)
_raw_sources/           ← immutable raw content
    ↓  extract (DeepSeek API)
[topic]/                ← structured .md notes with frontmatter
    ↓  place (you decide)
[topic].canvas          ← visual knowledge matrix
[topic].base            ← database view (Obsidian Bases)
```

**Orchestration:** Claude Code (or any Claude-compatible agent)
**Extraction:** DeepSeek API only — Claude handles everything else

---

## Architecture

```
CC+Obsidian/
├── .claude/
│   ├── commands/
│   │   └── knowledge-intake.md     ← /knowledge-intake slash command
│   └── skills/
│       ├── knowledge-intake.md     ← 5-step workflow skill
│       ├── defuddle/               ← web scraping skill (kepano)
│       ├── json-canvas/            ← Canvas manipulation skill (kepano)
│       ├── obsidian-bases/         ← Bases plugin skill (kepano)
│       ├── obsidian-cli/           ← Obsidian CLI skill (kepano)
│       └── obsidian-markdown/      ← Markdown formatting skill (kepano)
├── config/
│   ├── extraction_prompts.json     ← DeepSeek prompt templates
│   └── topics.json                 ← registered topic registry
├── scripts/
│   └── intake.py                   ← portable Python CLI (DeepSeek + scraping)
├── skills/                         ← universal skills (multi-agent)
├── skills-lock.json                ← skill version lock
├── CLAUDE.md                       ← vault context (always loaded by Claude)
├── [topic].canvas                  ← visual knowledge matrix per topic
└── [topic].base                    ← database view per topic
```

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| [Claude Code](https://claude.ai/code) | CLI or VS Code extension |
| [Obsidian](https://obsidian.md) | Desktop app |
| Obsidian **Canvas** plugin | Built-in core plugin — enable in settings |
| Obsidian **Bases** plugin | Community plugin — install from community marketplace |
| Python 3.10+ | For `scripts/intake.py` |
| Node.js 18+ | For `defuddle` CLI and `npx skills` |
| DeepSeek API key | [platform.deepseek.com](https://platform.deepseek.com) |

---

## Quick Start

### 1. Clone and open

```bash
git clone https://github.com/Xin-MediaGeek/CC-Obsidian.git
cd CC-Obsidian
```

Open the folder as an **Obsidian vault** and as a **Claude Code project**.

### 2. Install Python dependencies

```bash
pip install openai requests
```

### 3. Install defuddle CLI

```bash
npm install -g defuddle
```

### 4. Install Obsidian Skills (optional but recommended)

```bash
npx skills add git@github.com:kepano/obsidian-skills.git
```

Select all 5 skills → scope: **Project** → agent: **Claude Code**

### 5. Set DeepSeek API key

**Windows:**
```powershell
setx DEEPSEEK_API_KEY "your-key-here"
```

**macOS/Linux:**
```bash
export DEEPSEEK_API_KEY="your-key-here"
# Add to ~/.zshrc or ~/.bashrc for persistence
```

### 6. Run your first intake

Open Claude Code in this directory and type:

```
/knowledge-intake
```

Provide a URL or PDF path when prompted.

---

## The 5-Step Intake Workflow

| Step | What Happens | Who Does It |
|------|-------------|-------------|
| **1. Intake** | Scrape URL or read PDF → save raw content to `_raw_sources/` | Claude + defuddle CLI |
| **2. Dedup** | Check for duplicate or related existing notes | Claude |
| **3. Extract** | Confirm prompt → call DeepSeek API → generate `.md` notes | DeepSeek API |
| **4. Canvas** | Ask where to place each note → update `.canvas` JSON | Claude (you decide) |
| **5. Done** | Print summary, offer to open `.base` view | Claude |

---

## Note Frontmatter Schema

Every processed note includes:

```yaml
---
title: "Concept Title"
date: 2026-04-18
source_url: "https://..."
source_raw: "_raw_sources/20260418_domain_slug.md"
topic: ai-engineering
tags: [ai-engineering, llm]
summary: "One-sentence summary"
status: draft   # draft | reviewed
---
```

---

## Extraction Prompt Templates

Three built-in templates in `config/extraction_prompts.json`:

| Template | Best For |
|----------|---------|
| `default` | General articles and blog posts |
| `technical-deep-dive` | Technical docs, architecture, code-heavy content |
| `concept-map` | Content with many interconnected concepts |

The last-used prompt is shown before each extraction run — you confirm, modify, or switch templates.

---

## Adding a New Topic

When you intake content outside existing topics, Claude will offer to:
1. Add to an existing topic
2. Create a new topic (auto-scaffolds folder + `.canvas` + `.base`)
3. Stage in `_staging/` for later classification

---

## Canvas Node Format

Each node in `.canvas` JSON displays:

```
**Concept Title**
_One-line summary_

[[note-filename]]
```

Groups represent subtopics. Edges represent labeled relationships. Maximum 2 hierarchy levels: topic (Canvas) → subtopic (group inside Canvas).

---

## intake.py CLI Reference

For use without Claude (cross-environment compatibility):

```bash
# Scrape URL and save raw source only
python scripts/intake.py --url URL --slug my-slug --raw-only

# Extract from existing raw source
python scripts/intake.py --extract --source _raw_sources/file.md --topic my-topic

# Full pipeline: scrape + extract
python scripts/intake.py --url URL --topic my-topic

# Use a custom prompt
python scripts/intake.py --extract --source file.md --prompt "Your custom prompt here"

# Use a different DeepSeek model
python scripts/intake.py --extract --source file.md --model deepseek-reasoner
```

---

## Credits

- [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) — Obsidian skill files for Claude Code
- [defuddle](https://github.com/kepano/defuddle) — Clean web content extraction
- [DeepSeek](https://deepseek.com) — Extraction API
- Inspired by the article *Claude Code + Obsidian，打造个人一站式内容创作管理引擎*

---

## License

MIT
