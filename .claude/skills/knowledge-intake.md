# Skill: knowledge-intake

Triggered by: `/knowledge-intake`, "intake", "add to knowledge base", "process this URL/PDF", or user provides a URL or PDF path with knowledge-related intent.

## Overview
This skill orchestrates the 5-step personal knowledge intake workflow. DeepSeek API handles extraction only; you handle all other steps.

**Always read `config/extraction_prompts.json` and `config/topics.json` at the start of every intake session.**

---

## Step 1 — Intake (Get Raw Content)

**CRITICAL: Raw sources must contain the ORIGINAL scraped text, not AI-processed summaries. Always use the Python script as the primary scraping method. WebFetch is a fallback ONLY.**

**If URL provided:**
1. Ask user to confirm or provide the slug for the raw filename (e.g., `programmer-to-ai-engineer`)
2. Run the Python script to scrape and save raw content:
   ```
   python scripts/intake.py --url [URL] --slug [slug] --raw-only
   ```
   This saves to `_raw_sources/YYYYMMDD_[domain]-[slug].md` using `requests` + HTML→text conversion.
3. **Fallback only if the script fails** (site blocks requests, SSL error, etc.):
   - Use `WebFetch` to retrieve content
   - Prepend a warning header: `> ⚠️ This raw source was captured via AI-assisted fetch (WebFetch), not raw HTML scraping. Some content may be summarized or missing.`
   - Save to `_raw_sources/[filename].md`
4. Read the saved file and show the user the first 20 lines to confirm content quality

**If PDF or local file provided:**
1. Ask user to confirm the slug
2. Run: `python scripts/intake.py --file [path] --slug [slug] --raw-only`
3. Fallback: Read the file directly with `Read` tool and save to `_raw_sources/`

**Announce:** "Raw source saved: `_raw_sources/[filename]` ([N] chars)"

---

## Step 2 — Dedup Check

1. List filenames in `_raw_sources/` — check for date/domain overlap
2. Extract 3-5 key terms from the new content's title/abstract
3. Grep topic folders for those terms
4. Report findings:
   - "No related content found. Proceeding."
   - OR: "Found [N] potentially related notes: [list]. Proceed anyway, supplement, or skip?"
5. Wait for user confirmation before continuing

---

## Step 3 — Extraction

1. Read `config/extraction_prompts.json`
2. Show the user the `last_used.prompt`:
   ```
   Current extraction prompt:
   "[prompt text]"
   
   Topic: [last_used.topic] | Last used: [last_used.used_at]
   
   Options: [C]onfirm / [M]odify / [T]emplate (default/technical-deep-dive/concept-map)
   ```
3. Wait for user input
4. Once prompt is confirmed, determine the topic:
   - Read `config/topics.json`
   - If topic matches an existing slug → use it
   - If no match → offer: add to existing topic, create new topic, or use `_staging/`
   - If creating new topic: update `config/topics.json`, create `[topic]/` folder, `[topic].canvas`, `[topic].base`

5. Run extraction:
   ```
   python scripts/intake.py --extract --source _raw_sources/[filename] --topic [slug] --prompt-file config/extraction_prompts.json
   ```
   
   **IMPORTANT:** Read the output files after creation. Show user:
   ```
   Extracted [N] concept(s):
   1. [Title 1] → [topic]/YYYYMMDD_[slug].md
   2. [Title 2] → [topic]/YYYYMMDD_[slug].md
   ...
   Proceed with canvas placement?
   ```

6. Update `config/extraction_prompts.json` `last_used` with confirmed prompt and topic

---

## Step 4 — Canvas Placement (always ask)

For each extracted note (sequentially):

1. Read the current `[topic].canvas` JSON file
2. Parse existing groups (nodes with `type: "group"`) and their labels
3. Present to user:
   ```
   Placing: "[Concept Title]"
   Summary: "[one-line summary]"
   
   Existing groups in [topic].canvas:
   - [Group A] (N nodes)
   - [Group B] (N nodes)
   
   Where should I place this note?
   [1] Group A  [2] Group B  [N] New group  [S] No group (top level)
   Also add to multiple groups? (y/n)
   ```
4. Wait for user selection
5. If new group: ask for group name

6. Update the `.canvas` JSON:
   - Add a new node with:
     ```json
     {
       "id": "[8-char hex id]",
       "type": "text",
       "text": "**[Concept Title]**\n_[One-line summary]_\n\n[[note-filename-without-extension]]",
       "x": [calculated],
       "y": [calculated],
       "width": 250,
       "height": 120
     }
     ```
   - Node placement rules:
     - Each node: width=280, height=160, margin=20px from group edges and between nodes
     - Groups with 1-2 nodes: arrange side by side (horizontal), group width = (nodes × 300) + 20
     - Groups with 3+ nodes: arrange vertically (stacked), group height = (nodes × 180) + 60
     - New group: position to the right of the rightmost existing group, gap=60px
     - Never place a node where its right edge exceeds (group.x + group.width - 20)
   - If creating new group: add group node first, position it to the right of existing groups

7. **Canvas JSON update rules:**
   - Generate a unique 8-char hex ID for each new node: use timestamp + counter
   - Read the full current canvas JSON before writing
   - Merge new nodes/edges into existing arrays
   - Write back the complete valid JSON

8. **Ask about edges:** "Should this note link to any existing nodes? (specify relationships or skip)"

---

## Step 5 — Summary

Print a clean summary:
```
✓ Intake complete
  Raw source: _raw_sources/[filename]
  Notes created:
    - [topic]/[note1].md → Canvas: [group name]
    - [topic]/[note2].md → Canvas: [group name]
  
Open [topic].base in Obsidian to review the database view? (y/n)
```

Check if any existing notes in the topic folder reference the source topic — if so, offer to add `[[note-filename]]` links to them.

---

## Canvas JSON Format Reference

Valid Obsidian Canvas JSON structure:
```json
{
  "nodes": [
    {
      "id": "a1b2c3d4",
      "type": "group",
      "label": "Subtopic Name",
      "x": 0,
      "y": 0,
      "width": 600,
      "height": 400,
      "color": "1"
    },
    {
      "id": "e5f6g7h8",
      "type": "text",
      "text": "**Concept Title**\n_One-line summary_\n\n[[note-filename]]",
      "x": 20,
      "y": 50,
      "width": 250,
      "height": 120
    }
  ],
  "edges": [
    {
      "id": "i9j0k1l2",
      "fromNode": "e5f6g7h8",
      "fromSide": "right",
      "toNode": "m3n4o5p6",
      "toSide": "left",
      "label": "relates to"
    }
  ]
}
```

Color codes for groups: "1"=red, "2"=orange, "3"=yellow, "4"=green, "5"=cyan, "6"=purple

---

## Error Handling

- **WebFetch fails:** Ask user to paste content manually or provide PDF
- **DeepSeek API error:** Show error, ask to retry or skip extraction
- **Topic not in topics.json:** Offer to register it before proceeding
- **Canvas file not found:** Create a new empty canvas: `{"nodes":[],"edges":[]}`

---

## Cross-Environment Notes

This skill works in Claude Code, OpenClaw, and GitHub Agent. The Python script `scripts/intake.py` handles the DeepSeek call — always invoke it as a subprocess rather than calling DeepSeek directly, so the workflow is portable.

In environments without `WebFetch`, fall back to `python scripts/intake.py --url [URL] --raw-only` to scrape.
