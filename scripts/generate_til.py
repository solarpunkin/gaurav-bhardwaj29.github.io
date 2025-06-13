import os
import glob
import markdown
import yaml
from collections import defaultdict
from datetime import datetime

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
    html_body = markdown.markdown(body, extensions=['fenced_code', 'codehilite'])
    post = {
        'title': meta['title'],
        'date': meta['date'],
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
            f.write(f'<li><span class="til-date">{post["date"]}</span> <a href="../posts/{post["filename"]}">{post["title"]}</a></li>\n')
        f.write("</ul>\n<a href='../index.html'>← Back to TIL</a>\n</body></html>")

# Generate main index.html
with open(INDEX_FILE, 'w') as f:
    f.write(f"""<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="til-style.css">
  <title>TIL</title>
</head>
<body>
  <h1>TIL</h1>
  <input type="search" id="til-search" placeholder="Search TILs..." oninput="filterTILs()" autofocus>
  <div class="til-tags">
""")
    # Tags bar
    for tag, tag_posts in sorted(tags_dict.items()):
        f.write(f'<a class="til-tag" href="tags/{tag}.html">{tag} ({len(tag_posts)})</a> ')
    f.write("</div>\n")

    # Recent TILs
    f.write('<h2>Recent TILs</h2>\n<ul class="til-list" id="til-list">\n')
    for post in posts[:5]:
        f.write(f'<li><span class="til-date">{post["date"]}</span> <a href="posts/{post["filename"]}">{post["title"]}</a></li>\n')
    f.write("</ul>\n")

    # All TILs (hidden, for search)
    f.write('<h2 style="display:none;">All TILs</h2>\n<ul class="til-list" id="all-tils" style="display:none;">\n')
    for post in posts:
        f.write(f'<li><span class="til-date">{post["date"]}</span> <a href="posts/{post["filename"]}">{post["title"]}</a></li>\n')
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