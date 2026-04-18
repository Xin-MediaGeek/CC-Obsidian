"""
Knowledge Intake Script — DeepSeek API extraction + web scraping
Usage:
  python intake.py --url URL [--slug SLUG] [--topic SLUG] [--prompt-file PATH] [--out-dir DIR]
  python intake.py --file PDF_OR_MD_PATH [--slug SLUG] [--topic SLUG] [--prompt-file PATH] [--out-dir DIR]
  python intake.py --extract --source RAW_PATH [--topic SLUG] [--prompt-file PATH] [--prompt TEXT] [--out-dir DIR]

Environment:
  DEEPSEEK_API_KEY  — required for --extract mode
"""

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


def slugify(text: str) -> str:
    """ASCII-safe slug. Chinese/CJK chars are stripped; use --slug to override."""
    text = text.lower().strip()
    # Remove CJK and other non-ASCII word chars
    text = re.sub(r"[^\x00-\x7F\w\s-]", "", text)
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    slug = text[:60].strip("-")
    return slug if slug else "untitled"


def get_domain(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    return slugify(domain.split(".")[0])


def scrape_url(url: str) -> str:
    """Scrape URL to markdown. Uses defuddle CLI if available, else requests+html2text."""
    try:
        import subprocess
        import shutil
        defuddle_bin = shutil.which("defuddle") or shutil.which("defuddle.cmd")
        if defuddle_bin:
            result = subprocess.run(
                [defuddle_bin, "parse", url, "--md"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
    except Exception:
        pass

    try:
        import requests
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        html = resp.text
    except ImportError:
        print("ERROR: 'requests' not installed. Run: pip install requests", file=sys.stderr)
        sys.exit(1)

    try:
        import html2text
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        return h.handle(html)
    except ImportError:
        pass

    # Minimal HTML strip fallback
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def read_raw_source(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def call_deepseek(content: str, prompt: str, model: str = "deepseek-chat") -> str:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: 'openai' not installed. Run: pip install openai", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": content},
    ]

    print(f"Calling DeepSeek API (model: {model})...", file=sys.stderr)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=8000,
    )
    return response.choices[0].message.content


def split_notes(raw_output: str) -> list[str]:
    parts = re.split(r"\n?---NOTE---\n?", raw_output)
    return [p.strip() for p in parts if p.strip()]


def infer_title(note_md: str) -> str:
    for line in note_md.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return "untitled"


def build_frontmatter(title: str, topic: str, source_raw: str, source_url: str = "") -> str:
    today = date.today().isoformat()
    tag_list = f"[{topic}]" if topic else "[]"
    url_line = f'source_url: "{source_url}"' if source_url else "source_url: \"\""
    return f"""---
title: "{title}"
date: {today}
{url_line}
source_raw: "{source_raw}"
topic: {topic}
tags: {tag_list}
summary: ""
status: draft
---

"""


def save_note(note_md: str, topic: str, source_raw: str, out_dir: Path, source_url: str = "") -> Path:
    title = infer_title(note_md)
    slug = slugify(title)
    today = date.today().strftime("%Y%m%d")
    filename = f"{today}_{slug}.md"
    out_path = out_dir / filename

    frontmatter = build_frontmatter(title, topic, source_raw, source_url)

    # Remove leading H1 if it duplicates the title in frontmatter
    body = note_md
    first_line = note_md.splitlines()[0].strip() if note_md.splitlines() else ""
    if first_line.startswith("# "):
        body = "\n".join(note_md.splitlines()[1:]).strip()

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(frontmatter + body)

    return out_path


def load_prompt_file(prompt_file: str) -> dict:
    with open(prompt_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_last_used(prompt_file: str, prompt: str, topic: str):
    data = load_prompt_file(prompt_file)
    data["last_used"] = {
        "prompt": prompt,
        "topic": topic,
        "used_at": date.today().isoformat(),
    }
    with open(prompt_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Knowledge intake — scrape + DeepSeek extract")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="URL to scrape and optionally extract")
    group.add_argument("--file", help="Local PDF or Markdown file to ingest")
    group.add_argument("--extract", action="store_true", help="Extract from an existing raw source")

    parser.add_argument("--source", help="Raw source file path (required with --extract)")
    parser.add_argument("--slug", default="", help="Override auto-generated raw filename slug")
    parser.add_argument("--topic", default="", help="Topic slug (e.g. vibe-coding)")
    parser.add_argument("--prompt", default="", help="Extraction prompt text (overrides last_used in prompt-file)")
    parser.add_argument("--prompt-file", default="config/extraction_prompts.json")
    parser.add_argument("--out-dir", default=None, help="Output dir for notes (default: topic folder or cwd)")
    parser.add_argument("--model", default="deepseek-chat", help="DeepSeek model to use")
    parser.add_argument("--raw-only", action="store_true", help="Only save raw source, skip extraction")
    parser.add_argument("--raw-out", default="_raw_sources", help="Directory to save raw source files")

    args = parser.parse_args()

    raw_out = Path(args.raw_out)
    raw_out.mkdir(parents=True, exist_ok=True)

    today = date.today().strftime("%Y%m%d")
    source_url = ""

    # --- Step 1: Get raw content ---
    if args.url:
        source_url = args.url
        domain = get_domain(args.url)
        slug = args.slug if args.slug else f"{domain}-scraped"
        print(f"Scraping {args.url}...", file=sys.stderr)
        content = scrape_url(args.url)
        raw_filename = f"{today}_{slug}.md"
        raw_path = raw_out / raw_filename
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(f"# Raw Source: {args.url}\n\n{content}")
        print(f"Raw source saved: {raw_path}")

    elif args.file:
        src = Path(args.file)
        slug = args.slug if args.slug else slugify(src.stem)
        raw_filename = f"{today}_{slug}.md"
        raw_path = raw_out / raw_filename
        content = read_raw_source(args.file)
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Raw source saved: {raw_path}")

    elif args.extract:
        if not args.source:
            print("ERROR: --extract requires --source", file=sys.stderr)
            sys.exit(1)
        raw_path = Path(args.source)
        content = read_raw_source(args.source)
        print(f"Loaded raw source: {raw_path}", file=sys.stderr)

    if args.raw_only:
        sys.exit(0)

    # --- Step 3: Extract via DeepSeek ---
    prompt_data = load_prompt_file(args.prompt_file)
    prompt = args.prompt if args.prompt else prompt_data["last_used"]["prompt"]

    raw_output = call_deepseek(content, prompt, model=args.model)

    notes = split_notes(raw_output)
    print(f"\nExtracted {len(notes)} concept(s):", file=sys.stderr)
    for i, note in enumerate(notes, 1):
        print(f"  {i}. {infer_title(note)}", file=sys.stderr)

    # Determine output directory
    if args.out_dir:
        out_dir = Path(args.out_dir)
    elif args.topic:
        out_dir = Path(args.topic)
    else:
        out_dir = Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)

    source_raw_rel = str(raw_path)

    saved = []
    for note in notes:
        out_path = save_note(note, args.topic, source_raw_rel, out_dir, source_url)
        saved.append(out_path)
        print(f"Saved: {out_path}")

    save_last_used(args.prompt_file, prompt, args.topic)
    print(f"\nDone. {len(saved)} note(s) created.", file=sys.stderr)


if __name__ == "__main__":
    main()
