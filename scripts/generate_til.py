import os
import glob
import markdown
import yaml
from collections import defaultdict

POSTS_DIR = 'til/posts'
TAGS_DIR = 'til/tags'
INDEX_FILE = 'til/index.html'
STYLE_FILE = 'til/til-style.css'

os.makedirs(TAGS_DIR, exist_ok=True)

posts = []
tags_dict = defaultdict(list)

for md_file in sorted(glob.glob(f"{POSTS_DIR}/*.md"), reverse=True):
    with open(md_file) as f:
        content = f.read()
    fm, body = content.split('---', 2)[1:]
    meta = yaml.safe_load(fm)
    html_body = markdown.markdown(body)
    post = {
        'title': meta['title'],
        'date': meta['date'],
        'tags': meta['tags'],
        'body': html_body,
        'filename': os.path.basename(md_file)
    }
    posts.append(post)
    for tag in meta['tags']:
        tags_dict[tag].append(post)

# Generate index.html
with open(INDEX_FILE, 'w') as f:
    f.write(f"""<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="til-style.css">
  <title>TIL</title>
</head>
<body>
  <h1>TIL</h1>
  <div class="til-tags">
""")
    for tag, tag_posts in sorted(tags_dict.items()):
        f.write(f'<a class="til-tag" href="tags/{tag}.html">{tag} ({len(tag_posts)})</a> ')
    f.write("</div>\n")

    # Latest post
    latest = posts[0]
    f.write(f"""<div class="main-til-content">
  <h2>{latest['title']}</h2>
  <div>{latest['body']}</div>
  <div class="til-footer">
    Posted {latest['date']} · Follow me on <a href="#">Twitter</a>, <a href="#">GitHub</a>, <a href="#">Mastodon</a> or subscribe to my <a href="#">RSS</a>
  </div>
  <div class="til-sidebar">
    <h3>Past TILs</h3>
    <ul>
""")
    for post in posts[1:]:
        f.write(f'<li><a href="../til/posts/{post["filename"]}">{post["title"]}</a> ({post["date"]})</li>\n')
    f.write("</ul></div></div></body></html>")

# Generate tag pages
for tag, tag_posts in tags_dict.items():
    with open(f"{TAGS_DIR}/{tag}.html", 'w') as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="../til-style.css">
  <title>TIL: {tag}</title>
</head>
<body>
  <h1>#{tag}</h1>
  <ul>
""")
        for post in tag_posts:
            f.write(f'<li><a href="../posts/{post["filename"]}">{post["title"]}</a> ({post["date"]})</li>\n')
        f.write("</ul></body></html>")