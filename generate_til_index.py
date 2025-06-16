import os
import datetime
import json
from html import escape
from pathlib import Path
from collections import defaultdict

TIL_DIR = Path("til")
INDEX_FILE = TIL_DIR / "index.html"
STYLE_PATH = "/til/til-style.css"


def collect_tils():
    posts = []
    for path in sorted(TIL_DIR.iterdir(), reverse=True):
        if not path.is_dir() or path.name == "assets":
            continue
        index_file = path / "index.html"
        if not index_file.exists():
            continue
        with open(index_file, "r", encoding="utf-8") as f:
            html = f.read()
        title = extract_title(html)
        date = extract_date(html)
        tags = extract_tags(html)
        slug = path.name
        posts.append({"title": title, "date": date, "slug": slug, "tags": tags})
    return posts


def extract_title(html):
    start = html.find("<h1>") + 4
    end = html.find("</h1>")
    return html[start:end].strip()


def extract_date(html):
    start = html.find("<small>") + 7
    end = html.find("</small>")
    return html[start:end].strip()


def extract_tags(html):
    tags = []
    start = html.find("<code>")
    while start != -1:
        end = html.find("</code>", start)
        if end == -1:
            break
        tag = html[start+6:end].strip()
        tags.append(tag)
        start = html.find("<code>", end)
    return tags


def generate_index(posts):
    tag_map = defaultdict(list)
    for post in posts:
        for tag in post["tags"]:
            tag_map[tag].append(post)

    content = "<h1>Today I Learned</h1>\n"
    for tag in sorted(tag_map):
        content += f"<h2>{escape(tag)}</h2>\n<ul>\n"
        for p in tag_map[tag]:
            content += f'<li><a href="/til/{p["slug"]}/">{escape(p["title"])}</a> <small>{p["date"]}</small></li>\n'
        content += "</ul>\n"

    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <title>TIL Index</title>
  <link rel=\"stylesheet\" href=\"{STYLE_PATH}\">
</head>
<body>
  <main>
    {content}
  </main>
</body>
</html>"""

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    posts = collect_tils()
    generate_index(posts)
    print(f"✅ Updated TIL index with {len(posts)} posts → {INDEX_FILE}")


if __name__ == "__main__":
    main()
