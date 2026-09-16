#!/usr/bin/env python3
import datetime as dt
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "posts"
POSTS_JSON = POSTS_DIR / "posts.json"


def ask(label, default=""):
    prompt = label
    if default:
        prompt += f" [{default}]"
    prompt += ": "
    value = input(prompt).strip()
    return value or default


def slugify(value):
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "untitled-post"


def estimate_reading_time(body):
    words = re.findall(r"\w+", body)
    minutes = max(1, round(len(words) / 220))
    return f"{minutes} min"


def paragraph_html(body):
    paragraphs = [part.strip() for part in body.split("\n\n") if part.strip()]
    return "\n".join(f"        <p>{html.escape(paragraph)}</p>" for paragraph in paragraphs)


def main():
    POSTS_DIR.mkdir(exist_ok=True)

    title = ask("Title")
    description = ask("Short description")
    category = ask("Category", "Note")
    date = ask("Date", dt.date.today().isoformat())
    tags_raw = ask("Tags, comma-separated", "notes")
    body = ask("First draft paragraph", "Write the post here.")

    tags = [tag.strip().lstrip("#") for tag in tags_raw.split(",") if tag.strip()]
    slug = slugify(title)
    filename = f"{slug}.html"
    output_path = POSTS_DIR / filename

    if output_path.exists():
        raise SystemExit(f"Post already exists: {output_path}")

    reading_time = estimate_reading_time(body)
    tag_text = " ".join(f"#{tag}" for tag in tags)
    body_markup = paragraph_html(body)

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{html.escape(description, quote=True)}">
  <title>{html.escape(title)} - Overfit</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body class="post-page">
  <div class="page">
    <header>
      <a class="brand" href="../index.html">Overfit</a>
      <nav aria-label="Primary navigation">
        <a href="../index.html#experiments">Experiments</a>
        <a href="../index.html#notes">Notes</a>
        <a href="../index.html#about">About</a>
      </nav>
    </header>

    <main>
      <a class="back-link" href="../index.html#notes">Back to notes</a>
      <article class="post">
        <h1>{html.escape(title)}</h1>
        <p class="post-meta">{html.escape(date)} · {html.escape(category)} · {html.escape(reading_time)} · {html.escape(tag_text)}</p>

{body_markup}

        <h2>Notes</h2>
        <p>Add the setup, result, and lesson here.</p>
      </article>
    </main>
  </div>
</body>
</html>
"""

    output_path.write_text(page, encoding="utf-8")

    posts = []
    if POSTS_JSON.exists():
        posts = json.loads(POSTS_JSON.read_text(encoding="utf-8"))

    posts.insert(0, {
        "title": title,
        "description": description,
        "date": date,
        "category": category,
        "readingTime": reading_time,
        "tags": tags,
        "url": f"posts/{filename}"
    })

    posts.sort(key=lambda post: post["date"], reverse=True)
    POSTS_JSON.write_text(json.dumps(posts, indent=2) + "\n", encoding="utf-8")

    print(f"Created {output_path}")
    print("The homepage will show it automatically when served through localhost.")


if __name__ == "__main__":
    main()
