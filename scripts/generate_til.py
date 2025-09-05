import os
import glob
import markdown
import yaml
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import re

POSTS_DIR = 'weblog/posts'
TAGS_DIR = 'weblog/tags'
INDEX_FILE = 'weblog/index.html'
STYLE_FILE = 'weblog/weblog-style.css'

os.makedirs(TAGS_DIR, exist_ok=True)

posts = []
tags_dict = defaultdict(list)

# Helper for IST
IST = timezone(timedelta(hours=5, minutes=30))

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def parse_slug_from_filename(filename):
    # expects yyyy-mm-dd-slug.md or slug.md
    base = os.path.basename(filename)
    if base.count('-') >= 3 and base[:4].isdigit():
        parts = base.split('-')
        slug = '-'.join(parts[3:]).replace('.md', '')
    else:
        slug = base.replace('.md', '')
    return slug

def parse_date_from_filename(filename):
    # expects yyyy-mm-dd-slug.md
    base = os.path.basename(filename)
    parts = base.split('-')
    if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit():
        year, month, day = parts[0], parts[1], parts[2]
        return datetime(int(year), int(month), int(day), tzinfo=IST)
    else:
        return datetime.now(IST)

# Parse all weblog markdown files
for md_file in sorted(glob.glob(f"{POSTS_DIR}/*.md")):
    with open(md_file, encoding="utf-8") as f:
        content = f.read()
    try:
        _, fm, body = content.split('---', 2)
    except ValueError:
        print(f"Skipping {md_file}: invalid frontmatter")
        continue
    meta = yaml.safe_load(fm)
    # Get slug from filename
    slug = parse_slug_from_filename(md_file)
    # Get date from filename if present, else use now
    date_obj = parse_date_from_filename(md_file)
    html_body = markdown.markdown(body, extensions=['fenced_code', 'codehilite'])
    post = {
        'title': meta['title'],
        'weblog_title': meta.get('weblog_title', meta['title']),  # Use weblog_title if exists, else fallback to title
        'date': date_obj,
        'date_str': date_obj.strftime('%Y-%m-%d'),
        'tags': meta.get('tags', []),
        'collection': meta.get('collection', None),
        'body': html_body,
        'filename': os.path.basename(md_file),
        'slug': slug
    }
    posts.append(post)
    for tag in post['tags']:
        tags_dict[tag].append(post)

# Sort posts by date ascending for navigation (oldest to newest)
posts.sort(key=lambda p: p['date'])

# Generate tag pages
for tag, tag_posts in tags_dict.items():
    tag_posts_sorted = sorted(tag_posts, key=lambda p: p['date'], reverse=True)
    with open(f"{TAGS_DIR}/{{tag}}.html", 'w', encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="../weblog-style.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
  <script>
    document.addEventListener("DOMContentLoaded", function() {{{
      if (window.renderMathInElement) {{{{
        renderMathInElement(document.body, {{{{
          delimiters: [
            {{{{left: '$$', right: '$$', display: true}}}},
            {{{{left: '$', right: '$', display: false}}}}
          ]
        }}}});
      }}}}
    }}}});
  </script>
  <title>Weblog: {{tag}}</title>
</head>
<body>
  <h1>#{{tag}}</h1>
  <ul class="weblog-list"><li><a href="../">← LOGS</a></li>
")
        for post in tag_posts_sorted:
            url = f"../posts/{{post['slug']}}/"
            f.write(f'<li><a href="{{url}}">{{post["title"]}}</a> <span class="weblog-date">{{post["date_str"]}}</span></li>\n')
        f.write(