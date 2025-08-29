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
    with open(f"{TAGS_DIR}/{tag}.html", 'w', encoding="utf-8") as f:
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
    document.addEventListener("DOMContentLoaded", function() {{
      if (window.renderMathInElement) {{
        renderMathInElement(document.body, {{
          delimiters: [
            {{left: '$$', right: '$$', display: true}},
            {{left: '$', right: '$', display: false}}
          ]
        }});
      }}
    }});
  </script>
  <title>Weblog: {tag}</title>
</head>
<body>
  <h1>#{tag}</h1>
  <ul class="weblog-list"><li><a href="../">← LOGS</a></li>
""")
        for post in tag_posts_sorted:
            url = f"../posts/{post['slug']}/"
            f.write(f'<li><a href="{url}">{post["title"]}</a> <span class="weblog-date">{post["date_str"]}</span></li>\n')
        f.write("</ul>\n</body></html>")

# Generate main index.html (recent weblogs: newest first)
posts_desc = sorted(posts, key=lambda p: p['date'], reverse=True)
with open(INDEX_FILE, 'w', encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="weblog-style.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
  <script>
    document.addEventListener("DOMContentLoaded", function() {{
      if (window.renderMathInElement) {{
        renderMathInElement(document.body, {{
          delimiters: [
            {{left: '$$', right: '$$', display: true}},
            {{left: '$', right: '$', display: false}}
          ]
        }});
      }}
    }});
  </script>
  <title>gaurav's weblog</title>
</head>
<body>
  <h1>Weblog</h1>
  <p>also check out my <a href="https://gaurv.me/blog/">blog</a> page or <a href="https://hypnotic-single-224.notion.site/2176392011f0804caebee47240886285?v=2176392011f08043bbb6000c58ab5167&source=copy_link">reading list</a>.</p>
  <div class="weblog-search-container">
    <form onsubmit="filterweblogs(); return false;" style="display: flex; width: 100%;">
      <input type="search" id="weblog-search" placeholder="Filter Logs..." autofocus>
      <button id="weblog-search-btn" type="submit">Search</button>
    </form>
  </div>
  <div class="weblog-tags">\n""")
    # Tags bar
    for tag, tag_posts in sorted(tags_dict.items()):
        f.write(f'<a class="weblog-tag" href="tags/{tag}.html">{tag} ({len(tag_posts)})</a><span class="weblog-tag-sep">• </span>')
    f.write("</div>\n")

    # Recent weblogs
    f.write('<h2>Most Recent</h2>\n<ul class="weblog-list" id="weblog-list">\n')
    for post in posts_desc[:10]:
        url = f"posts/{post['slug']}/"
        f.write(f'<li><a href="{url}">{post["title"]}</a> <span class="weblog-date">{post["date_str"]}</span></li>\n')
    f.write("</ul>\n")

    # All weblogs (hidden, for search)
    f.write('<h2 style="display:none;">All logs</h2>\n<ul class="weblog-list" id="all-weblogs" style="display:none;">\n')
    for post in posts_desc:
        url = f"posts/{post['slug']}/"
        f.write(f'<li><a href="{url}">{post["title"]}</a> <span class="weblog-date">{post["date_str"]}</span></li>\n')
    f.write("</ul>\n")

    # Minimal JS for search (optional, can be removed for pure HTML)
    f.write("""
<script>
function filterweblogs() {
  var input = document.getElementById('weblog-search');
  var filter = input.value.toLowerCase();
  var ul = document.getElementById('weblog-list');
  ul.innerHTML = '';
  var allLis = document.getElementById('all-weblogs').getElementsByTagName('li');
  var count = 0;
  for (var i = 0; i < allLis.length; i++) {
    var txt = allLis[i].textContent || allLis[i].innerText;
    if (txt.toLowerCase().indexOf(filter) > -1 && count < 10) {
      ul.appendChild(allLis[i].cloneNode(true));
      count++;
    }
  }
}
</script>
        <nav style="margin-top: 2em;">
            <a href="../">&larr; home</a>
        </nav>
""")
    f.write("</body></html>")

# Generate HTML for each weblog post with slug-based URLs and sidebar with prev/next links
for i, post in enumerate(posts):
    slug = post['slug']
    out_dir = f"weblog/posts/{slug}"
    os.makedirs(out_dir, exist_ok=True)
    prev_post = posts[i+1] if i < len(posts)-1 else None
    next_post = posts[i-1] if i > 0 else None
    # Use the post's date for display, not current time
    display_time = post['date'].strftime('%d %B %Y (IST)')
    with open(f"{out_dir}/index.html", "w", encoding="utf-8") as f_post:
        f_post.write(f"""<!DOCTYPE html>
<html>
<head>
   <meta name="fediverse:creator" content="@wiredguy@mastodon.social">                  
  <link rel="stylesheet" href="../../weblog-style.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
  <script>
    document.addEventListener("DOMContentLoaded", function()  {{
      if (window.renderMathInElement) {{
        renderMathInElement(document.body, {{
          delimiters: [
            {{left: '$$', right: '$$', display: true}},
            {{left: '$', right: '$', display: false}}
          ]
        }});
      }}
    }});
  </script>
  <title>{post['title']}</title>
</head>
<body>
<main>
  <h1>{post['title']}</h1>
  <div class="weblog-body">{post['body']}

  <!-- Perlin noise image row (only for the perlin-noise post) -->
  {'' if post['slug'] != 'perlin-noise' else '''
  <div style="display: flex; justify-content: center; gap: 2em; margin: 2em 0;">
    <figure style="flex: 1; text-align: center; max-width: 200px;">
      <img src="https://pub-91e1a485198740aabff1705e89606dc3.r2.dev/perlin%20noise/input_image.jpg" alt="Input Image" style="width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px #0001;">
      <figcaption style="margin-top: 0.7em; font-size: 1em; color: #555;">Input Image (400x400)</figcaption>
    </figure>
    <figure style="flex: 1; text-align: center; max-width: 200px;">
      <img src="https://pub-91e1a485198740aabff1705e89606dc3.r2.dev/perlin%20noise/fractal_terrain_400x400.png" alt="x Perlin noise" style="width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px #0001;">
      <figcaption style="margin-top: 0.7em; font-size: 1em; color: #555;">x Perlin noise</figcaption>
    </figure>
    <figure style="flex: 1; text-align: center; max-width: 200px;">
      <img src="https://pub-91e1a485198740aabff1705e89606dc3.r2.dev/perlin%20noise/output_distorted_400x400.png" alt="Output Image" style="width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px #0001;">
      <figcaption style="margin-top: 0.7em; font-size: 1em; color: #555;">= Output Image</figcaption>
    </figure>
  </div>
  '''}
    <!-- simplex noise image row (only for the simplex-noise post) -->
  {'' if post['slug'] != 'simplex-noise' else '''
  <div style="display: flex; justify-content: center; gap: 2em; margin: 2em 0;">
    <figure style="flex: 1; text-align: center; max-width: 200px;">
      <img src="https://pub-91e1a485198740aabff1705e89606dc3.r2.dev/simplex-octaves/Gxg2zyjbwAAj3dN.png" alt="Input Image" style="width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px #0001;">
      <figcaption style="margin-top: 0.7em; font-size: 1em; color: #555;"></figcaption>
    </figure>
    <figure style="flex: 1; text-align: center; max-width: 200px;">
      <img src="https://pub-91e1a485198740aabff1705e89606dc3.r2.dev/simplex-octaves/Gxg4eP9awAIyrKT.png" alt="x Perlin noise" style="width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px #0001;">
      <figcaption style="margin-top: 0.7em; font-size: 1em; color: #555;"></figcaption>
    </figure>
  </div>
  '''}
  </div>
  <div class="weblog-date">Posted on {display_time} · Follow me on <a href="https://x.com/wiredguys">Twitter</a> or <a rel="me" href="https://mastodon.social/@wiredguy">Mastodon</a></div>

  <ul class="weblog-list">
    <li><a href="../../index.html">&laquo; LOGS</a></li>
  </ul>
  <div class="weblog-sidebar">
    <h5>Jump to</h5>
    <ul>
""")
        if prev_post:
            prev_slug = prev_post['slug']
            prev_url = f"../{prev_slug}/"
            f_post.write(f'      <li><a href="{prev_url}">Next: {prev_post["title"]} &rarr;</a></li>\n')
        if next_post:
            next_slug = next_post['slug']
            next_url = f"../{next_slug}/"
            f_post.write(f'      <li><a href="{next_url}">&larr; Previous: {next_post["title"]}</a></li>\n')
        f_post.write("""    </ul>
  </div>
</main>
</body>
</html>
""")