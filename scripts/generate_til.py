import os
import glob
import markdown
import yaml
from collections import defaultdict
from datetime import datetime
import re

POSTS_DIR = 'til/posts'
TAGS_DIR = 'til/tags'
INDEX_FILE = 'til/index.html'
STYLE_FILE = 'til/til-style.css'

os.makedirs(TAGS_DIR, exist_ok=True)

posts = []
tags_dict = defaultdict(list)

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
    # Parse date as datetime object for sorting
    date_str = str(meta['date'])
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            print(f"Skipping {md_file}: invalid date format {date_str}")
            continue
    html_body = markdown.markdown(body, extensions=['fenced_code', 'codehilite'])
    post = {
        'title': meta['title'],
        'date': date_obj,
        'date_str': date_str,
        'tags': meta.get('tags', []),
        'collection': meta.get('collection', None),
        'body': html_body,
        'filename': os.path.basename(md_file),
        'slug': os.path.splitext(os.path.basename(md_file))[0]
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
  <link rel="stylesheet" href="../til-style.css">
  <title>TIL: {tag}</title>
</head>
<body>
  <h1>#{tag}</h1>
  <ul class="til-list">
""")
        for post in tag_posts_sorted:
            f.write(f'<li><a href="../posts/{post["filename"]}">{post["title"]}</a> <span class="til-date">{post["date_str"]}</span></li>\n')
        f.write("</ul>\n<a href='../index.html'>← TIL</a>\n</body></html>")

# Generate main index.html
with open(INDEX_FILE, 'w') as f:
    f.write(f"""<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="til-style.css">
  <title>🧠 TIL</title>
</head>
<body>
  <h1>Gaurav: TIL</h1>
  <p>A TIL: <strong>Today I Learned</strong>, also check out my <a href="https://gaurv.me/blog/">blog</a>.</p>
  <div style="display: flex; align-items: center; gap: 0.5em; margin-bottom: 1em;">
    <input type="search" id="til-search" placeholder="Search TILs..." oninput="filterTILs()" autofocus>
    <button id="til-search-btn" onclick="filterTILs()">Search</button>
  </div>
  <div class="til-tags">
""")
    # Tags bar
    for tag, tag_posts in sorted(tags_dict.items()):
        f.write(f'<a class="til-tag" href="tags/{tag}.html">{tag} ({len(tag_posts)}) •</a> ')
    f.write("</div>\n")

    # Recent TILs
    f.write('<h2>Recent TILs</h2>\n<ul class="til-list" id="til-list">\n')
    for post in posts[:10]:
        f.write(f'<li><a href="posts/{post["filename"]}">{post["title"]}</a> <span class="til-date">{post["date_str"]}</span></li>\n')
    f.write("</ul>\n")

    # All TILs (hidden, for search)
    f.write('<h2 style="display:none;">All TILs</h2>\n<ul class="til-list" id="all-tils" style="display:none;">\n')
    for post in posts:
        f.write(f'<li><a href="posts/{post["filename"]}">{post["title"]}</a> <span class="til-date">{post["date_str"]}</span></li>\n')
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

def slugify(title):
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

# Generate HTML for each TIL post with indexed URLs and sidebar with prev/next links
for i, post in enumerate(posts):
    dt = post['date']
    slug = slugify(post['title'])
    out_dir = f"til/posts/{dt.year}/{dt.month:02d}/{dt.day:02d}/{slug}"
    os.makedirs(out_dir, exist_ok=True)
    prev_post = posts[i-1] if i > 0 else None
    next_post = posts[i+1] if i < len(posts)-1 else None
    with open(f"{out_dir}/index.html", "w") as f_post:
        f_post.write(f"""<!DOCTYPE html>
<html>
<head>
  <link rel=\"stylesheet\" href=\"../../../til-style.css\">
  <title>{post['title']}</title>
</head>
<body>
  <h1>{post['title']}</h1>
  <div class=\"til-date\">{post['date_str']}</div>
  <div class=\"til-body\">{post['body']}</div>
  <div class=\"til-sidebar\">
    <h3>Navigation</h3>
    <ul>
""")
        if prev_post:
            prev_dt = prev_post['date']
            prev_slug = slugify(prev_post['title'])
            prev_url = f"../../{prev_dt.year}/{prev_dt.month:02d}/{prev_dt.day:02d}/{prev_slug}/"
            f_post.write(f'<li><a href="{prev_url}">← Previous: {prev_post["title"]}</a></li>\n')
        if next_post:
            next_dt = next_post['date']
            next_slug = slugify(next_post['title'])
            next_url = f"../../{next_dt.year}/{next_dt.month:02d}/{next_dt.day:02d}/{next_slug}/"
            f_post.write(f'<li><a href="{next_url}">Next: {next_post["title"]} →</a></li>\n')
        f_post.write("""
    </ul>
  </div>
</body>
</html>
""")