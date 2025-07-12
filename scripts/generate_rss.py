import os
import glob
import markdown
import yaml
from datetime import datetime, timedelta, timezone
import re
from xml.sax.saxutils import escape

SITE_URL = "https://gaurv.me"
RSS_FILE = "rss.xml"

# Helper for IST
IST = timezone(timedelta(hours=5, minutes=30))

def parse_frontmatter(md_file):
    with open(md_file, encoding="utf-8") as f:
        content = f.read()
    try:
        _, fm, body = content.split('---', 2)
        meta = yaml.safe_load(fm)
        return meta, body
    except Exception:
        return None, None

def parse_date_from_filename(filename):
    base = os.path.basename(filename)
    parts = base.split('-')
    if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit():
        year, month, day = parts[0], parts[1], parts[2]
        return datetime(int(year), int(month), int(day), tzinfo=IST)
    else:
        return datetime.now(IST)

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

# Gather blog posts
blog_posts = []
for md_file in sorted(glob.glob("blog/*.md")):
    meta, body = parse_frontmatter(md_file)
    if not meta: continue
    slug = os.path.splitext(os.path.basename(md_file))[0]
    date_obj = parse_date_from_filename(md_file)
    url = f"{SITE_URL}/blog/{slug}.html"
    blog_posts.append({
        "title": meta.get("title", slug),
        "link": url,
        "description": escape(meta.get("description", "") or body[:180]),
        "pubDate": date_obj.strftime('%a, %d %b %Y %H:%M:%S %z'),
        "category": "blog"
    })

# Gather TILs
til_posts = []
for md_file in sorted(glob.glob("til/posts/*.md")):
    meta, body = parse_frontmatter(md_file)
    if not meta: continue
    slug = os.path.splitext(os.path.basename(md_file))[0]
    date_obj = parse_date_from_filename(md_file)
    url = f"{SITE_URL}/til/posts/{slug}/"
    til_posts.append({
        "title": meta.get("title", slug),
        "link": url,
        "description": escape(body[:180]),
        "pubDate": date_obj.strftime('%a, %d %b %Y %H:%M:%S %z'),
        "category": "til"
    })

# Gather code projects (from code/index.html)
code_projects = []
code_html = "code/index.html"
if os.path.exists(code_html):
    from bs4 import BeautifulSoup
    with open(code_html, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        for div in soup.select(".project"):
            a = div.find("a")
            desc = div.find(class_="subheading")
            if a:
                code_projects.append({
                    "title": a.text.strip(),
                    "link": a["href"],
                    "description": escape(desc.text.strip() if desc else ""),
                    "pubDate": datetime.now(IST).strftime('%a, %d %b %Y %H:%M:%S %z'),
                    "category": "code"
                })

# Combine and sort all items by date (desc)
all_items = blog_posts + til_posts + code_projects
all_items.sort(key=lambda x: x["pubDate"], reverse=True)

# Write RSS XML
with open(RSS_FILE, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<rss version="2.0">\n<channel>\n')
    f.write('<title>Gaurav Bhardwaj - Updates</title>\n')
    f.write(f'<link>{SITE_URL}/</link>\n')
    f.write('<description>Unified RSS feed for blog, TILs, and code updates.</description>\n')
    for item in all_items[:30]:
        f.write('<item>\n')
        f.write(f'<title>{escape(item["title"])}</title>\n')
        f.write(f'<link>{item["link"]}</link>\n')
        f.write(f'<description>{item["description"]}</description>\n')
        f.write(f'<pubDate>{item["pubDate"]}</pubDate>\n')
        f.write(f'<category>{item["category"]}</category>\n')
        f.write('</item>\n')
    f.write('</channel>\n</rss>\n')
