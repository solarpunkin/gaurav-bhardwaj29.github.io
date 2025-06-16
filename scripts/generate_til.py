import os, glob, re, yaml, markdown
from collections import defaultdict
from datetime import datetime, timedelta, timezone

# ---------- CONSTANTS ----------
POSTS_DIR  = 'til/posts'
TAGS_DIR   = 'til/tags'
INDEX_FILE = 'til/index.html'
STYLE_FILE = 'til/til-style.css'

# Indian Standard Time helper
IST = timezone(timedelta(hours=5, minutes=30))

# ---------- UTILS ----------
def slugify(text: str) -> str:
    """URL-friendly slug."""  # [1]
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def parse_slug_from_filename(filename: str) -> str:
    """slug comes after YYYY-MM-DD- in a md file name."""  # [1]
    base = os.path.basename(filename)
    if base.count('-') >= 3 and base[:4].isdigit():
        parts = base.split('-')
        return '-'.join(parts[3:]).replace('.md', '')
    return base.replace('.md', '')

def parse_date_from_filename(filename: str) -> datetime:
    """extract date or fall back to now."""  # [1]
    base = os.path.basename(filename)
    parts = base.split('-')
    if len(parts) >= 3 and all(p.isdigit() for p in parts[:3]):
        y, m, d = map(int, parts[:3])
        return datetime(y, m, d, tzinfo=IST)
    return datetime.now(IST)

# ---------- COLLECT POSTS ----------
posts, tags_dict = [], defaultdict(list)
for md_file in sorted(glob.glob(f"{POSTS_DIR}/*.md")):
    with open(md_file, encoding="utf-8") as f:
        raw = f.read()

    try:
        _, fm, body = raw.split('---', 2)
    except ValueError:                # bad front-matter
        print(f"Skipping {md_file}")
        continue

    meta = yaml.safe_load(fm) or {}

    # —— clean & tweak markdown before conversion ——
    # 1) strip first Notion table (index)                          # [2]
    body = re.sub(r'^\|.*\n(\|.*\n)+', '', body, 1, flags=re.M)
    # 2) title patch
    body = re.sub(r'^# +github-actions', 
                  '# Creating Image textures using perlin noise', 
                  body, flags=re.I | re.M)

    md = markdown.Markdown(extensions=[
        'fenced_code',               # code fences            # [1]
        'codehilite',                # pygments highlight     # [1]
        'attr_list',                 # keep {width=…}         # [2]
        'mdx_math'                   # inline/$$ math         # [3]
    ])
    html_body = md.convert(body)

    slug = parse_slug_from_filename(md_file)
    date_obj = parse_date_from_filename(md_file)

    post = dict(
        title      = meta.get('title', slug.replace('-', ' ').title()),
        date       = date_obj,
        date_str   = date_obj.strftime('%Y-%m-%d'),
        tags       = meta.get('tags', []),
        collection = meta.get('collection'),
        body       = html_body,
        filename   = os.path.basename(md_file),
        slug       = slug
    )
    posts.append(post)
    for tag in post['tags']:
        tags_dict[tag].append(post)

# ---------- NAVIGATION ----------
posts.sort(key=lambda p: p['date'])                # oldest→newest
for i, p in enumerate(posts):
    p['prev_slug'] = posts[i-1]['slug'] if i else None
    p['next_slug'] = posts[i+1]['slug'] if i < len(posts)-1 else None

# ---------- TAG PAGES ----------
os.makedirs(TAGS_DIR, exist_ok=True)
for tag, tag_posts in tags_dict.items():
    tag_posts_sorted = sorted(tag_posts, key=lambda p: p['date'], reverse=True)
    with open(f"{TAGS_DIR}/{tag}.html", 'w', encoding="utf-8") as f:
        f.write(f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><title>#{tag}</title>
<link rel="stylesheet" href="/{STYLE_FILE}">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.17.0/dist/katex.min.css"> <!-- math --> <!-- [3] -->
</head><body><main>
<h1>#{tag}</h1>
<ul class="til-list">
""" + '\n'.join(
f'<li><a href="/til/{p["slug"]}.html">{p["title"]}</a> '
f'<span class="til-date">{p["date_str"]}</span></li>'
for p in tag_posts_sorted) + """
</ul></main></body></html>""")

# ---------- INDEX ----------
with open(INDEX_FILE, 'w', encoding="utf-8") as f:
    idx = sorted(posts, key=lambda p: p['date'], reverse=True)
    f.write(f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><title>TIL</title>
<link rel="stylesheet" href="/{STYLE_FILE}">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.17.0/dist/katex.min.css"> <!-- [3] -->
</head><body><main>
<h1>Today I Learned</h1>
<ul class="til-list">
""" + '\n'.join(
f'<li><a href="/til/{p["slug"]}.html">{p["title"]}</a> '
f'<span class="til-date">{p["date_str"]}</span></li>'
for p in idx) + """
</ul></main></body></html>""")

# ---------- INDIVIDUAL PAGES ----------
for p in posts:
    with open(f"til/{p['slug']}.html", 'w', encoding="utf-8") as f:
        f.write(f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><title>{p['title']}</title>
<link rel="stylesheet" href="/{STYLE_FILE}">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.17.0/dist/katex.min.css"> <!-- [3] -->
</head><body><main>
<nav class="til-nav">""" +
 (f'<a href="/til/{p["prev_slug"]}.html">← Previous</a>' if p['prev_slug'] else '') +
 (f'<a href="/til/{p["next_slug"]}.html" style="float:right">Next →</a>' if p['next_slug'] else '') +
 f"""</nav>
<h1>{p['title']}</h1>
<p class="til-date">{p['date_str']}</p>
<div class="til-tags">""" +
 ' '.join(f'<a class="til-tag" href="/til/tags/{t}.html">#{t}</a>' for t in p['tags']) +
 f"""</div>
{p['body']}
</main></body></html>""")
