import os
import glob
import markdown
import yaml
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import re

POSTS_DIR = 'til/posts'
TAGS_DIR = 'til/tags'
INDEX_FILE = 'til/index.html'
STYLE_FILE = 'til/til-style.css'

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
    if base.count('-') >= 3:
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

# Parse all TIL markdown files
for md_file in sorted(glob.glob(f"{POSTS_DIR}/*.md"), reverse=True):
    with open(md_file) as f:
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

# Sort posts by date descending
posts.sort(key=lambda p: p['date'], reverse=True)

# Generate tag pages
for tag, tag_posts in tags_dict.items():
    tag_posts_sorted = sorted(tag_posts, key=lambda p: p['date'], reverse=True)
    with open(f"{TAGS_DIR}/{tag}.html", 'w') as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
  <link rel=\"stylesheet\" href=\"../til-style.css\">
  <title>TIL: {tag}</title>
</head>
<body>
  <h1>#{tag}</h1>
  <ul class=\"til-list\"><li><a href="../">← TIL</a></li>
""")
        for post in tag_posts_sorted:
            url = f"../posts/{post['slug']}/"
            f.write(f'<li><a href="{url}">{post["title"]}</a> <span class="til-date">{post["date_str"]}</span></li>\n')
        f.write("</ul>\n</body></html>")

# Generate main index.html
with open(INDEX_FILE, 'w') as f:
    f.write(f"""<!DOCTYPE html>
<html>
<head>
  <link rel=\"stylesheet\" href=\"til-style.css\">
  <title>🧠 TIL</title>
</head>
<body>
  <h1>Gaurav: TIL</h1>
  <p>A TIL: <strong>Today I Learned</strong>, also check out my <a href=\"https://gaurv.me/blog/\">blog</a>.</p>
  <div class=\"til-search-container\">
    <form onsubmit=\"filterTILs(); return false;\" style=\"display: flex; width: 100%;\">
      <input type=\"search\" id=\"til-search\" placeholder=\"Search TILs...\" autofocus>
      <button id=\"til-search-btn\" type=\"submit\">Search</button>
    </form>
  </div>
  <div class=\"til-tags\">\n""")
    # Tags bar
    for tag, tag_posts in sorted(tags_dict.items()):
        f.write(f'<a class=\"til-tag\" href=\"tags/{tag}.html\">{tag} ({len(tag_posts)})</a><span class=\"til-tag-sep\">• </span>')
    f.write("</div>\n")

    # Recent TILs
    f.write('<h2>Recent TILs</h2>\n<ul class=\"til-list\" id=\"til-list\">\n')
    for post in posts[:10]:
        url = f"posts/{post['slug']}/"
        f.write(f'<li><a href=\"{url}\">{post["title"]}</a> <span class=\"til-date\">{post["date_str"]}</span></li>\n')
    f.write("</ul>\n")

    # All TILs (hidden, for search)
    f.write('<h2 style=\"display:none;\">All TILs</h2>\n<ul class=\"til-list\" id=\"all-tils\" style=\"display:none;\">\n')
    for post in posts:
        url = f"posts/{post['slug']}/"
        f.write(f'<li><a href=\"{url}\">{post["title"]}</a> <span class=\"til-date\">{post["date_str"]}</span></li>\n')
    f.write("</ul>\n")

    # Minimal JS for search (optional, can be removed for pure HTML)
    f.write("""
<script>
function filterTILs() {
  var input = document.getElementById('til-search');
  var filter = input.value.toLowerCase();
  var ul = document.getElementById('til-list');
  ul.innerHTML = '';
  var allLis = document.getElementById('all-tils').getElementsByTagName('li');
  var count = 0;
  for (var i = 0; i < allLis.length; i++) {
    var txt = allLis[i].textContent || allLis[i].innerText;
    if (txt.toLowerCase().indexOf(filter) > -1 && count < 5) {
      ul.appendChild(allLis[i].cloneNode(true));
      count++;
    }
  }
}
</script>
""")
    f.write("</body></html>")

# Generate HTML for each TIL post with slug-based URLs and sidebar with prev/next links
for i, post in enumerate(posts):
    slug = post['slug']
    out_dir = f"til/posts/{slug}"
    os.makedirs(out_dir, exist_ok=True)
    prev_post = posts[i-1] if i > 0 else None
    next_post = posts[i+1] if i < len(posts)-1 else None
    now_ist = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S (IST)')
    with open(f"{out_dir}/index.html", "w") as f_post:
        f_post.write(f"""<!DOCTYPE html>
      <html>
      <head>
        <link rel="stylesheet" href="../../til-style.css">
        <title>{post['title']}</title>
      </head>
      <body>
      <main>
        <h1>{post['title']}</h1>
        <div class="til-body">{post['body']}</div>
        <div class="til-date">Posted on {now_ist} · Follow me on <a href="https://x.com/bardgaurav">Twitter</a>.</div>
        <ul class="til-list">
          <li><a href="../../index.html">← TIL</a></li>
        </ul>
        <div class="til-sidebar">
          <h5>Jump to</h5>
          <ul>
      """)
        # Ensure prev/next links are wrapped in <li> tags if present
        if prev_post:
            prev_slug = prev_post['slug']
            prev_url = f"../{prev_slug}/"
            f_post.write(f'      <li><a href="{prev_url}">← Previous: {prev_post["title"]}</a></li>\n')
        if next_post:
            next_slug = next_post['slug']
            next_url = f"../{next_slug}/"
            f_post.write(f'      <li><a href="{next_url}">Next: {next_post["title"]} →</a></li>\n')
        f_post.write("""    </ul>
  </div>
  </main>
</body>
</html>
""")