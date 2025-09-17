import os
import glob
import yaml
from datetime import datetime, timedelta, timezone
import re
from xml.sax.saxutils import escape
from bs4 import BeautifulSoup, BeautifulStoneSoup
from typing import Dict, List, Optional
from urllib.parse import urlparse

SITE_URL = "https://gaurv.me"
RSS_FILE = "rss.xml"
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

# ----------- Blog posts (HTML-based) -----------
blog_posts = []
for html_file in sorted(glob.glob("blog/*.html")):
    if os.path.basename(html_file) == "index.html":
        continue
    with open(html_file, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        title = soup.title.string.strip() if soup.title else os.path.splitext(os.path.basename(html_file))[0]
        slug = os.path.splitext(os.path.basename(html_file))[0]
        url = f"{SITE_URL}/blog/{slug}.html"
        description = soup.find("meta", attrs={"name": "description"})
        desc_text = description["content"].strip() if description else ""
        mtime = os.path.getmtime(html_file)
        pub_date = datetime.fromtimestamp(mtime, tz=IST)
        blog_posts.append({
            "title": title,
            "link": url,
            "description": escape(desc_text),
            "pubDate_obj": pub_date,
            "pubDate": pub_date.strftime('%a, %d %b %Y %H:%M:%S %z'),
            "category": "blog"
        })

# ----------- weblog posts (Markdown) -----------
weblog_posts = []
for md_file in sorted(glob.glob("weblog/posts/*.md")):
    meta, body = parse_frontmatter(md_file)
    if not meta:
        continue
    filename = os.path.basename(md_file)
    name = os.path.splitext(filename)[0]
    match = re.match(r'^\d{4}-\d{2}-\d{2}-(.+)', name)
    slug = match.group(1) if match else name
    date_obj = parse_date_from_filename(md_file)
    url = f"{SITE_URL}/weblog/p/{slug}/"
    weblog_posts.append({
        "title": meta.get("title", slug.replace('-', ' ').title()),
        "link": url,
        "description": escape(body[:180]),
        "pubDate": date_obj.strftime('%a, %d %b %Y %H:%M:%S %z'),
        "category": "weblog"
    })

# ----------- Code Projects (from HTML listing) -----------
code_projects = []
code_html = "code/index.html"
if os.path.exists(code_html):
    mtime = os.path.getmtime(code_html)
    code_pub_date = datetime.fromtimestamp(mtime, tz=IST)
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
                    "pubDate_obj": code_pub_date,
                    "pubDate": code_pub_date.strftime('%a, %d %b %Y %H:%M:%S %z'),
                    "category": "code"
                })

# ----------- Combine All -----------
all_items = blog_posts + weblog_posts + code_projects
all_items.sort(key=lambda x: x.get("pubDate_obj") or datetime.strptime(x["pubDate"], '%a, %d %b %Y %H:%M:%S %z'), reverse=True)

def get_existing_feed_items() -> Dict[str, dict]:
    """Read existing RSS feed and return a dictionary of items keyed by link."""
    if not os.path.exists(RSS_FILE):
        return {}
    
    with open(RSS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulStoneSoup(content, 'xml')
    items = {}
    
    for item in soup.find_all('item'):
        link = item.find('link')
        if link and link.text:
            items[link.text] = {
                'title': item.find('title').text if item.find('title') else '',
                'description': item.find('description').text if item.find('description') else '',
                'pubDate': item.find('pubDate').text if item.find('pubDate') else '',
                'category': item.find('category').text if item.find('category') else ''
            }
    return items

def generate_rss():
    # Get existing feed items
    existing_items = get_existing_feed_items()
    
    # Combine and sort all items
    combined_items = blog_posts + weblog_posts + code_projects
    
    # Create a dictionary of new items, preserving existing ones
    all_items = {}
    
    # First add existing items to preserve their order and dates
    for link, item in existing_items.items():
        all_items[link] = item
    
    # Then add/update with new items
    for item in combined_items:
        link = item['link']
        if link not in all_items:  # Only add if it's a new item
            all_items[link] = {
                'title': item['title'],
                'description': item['description'],
                'pubDate': item.get('pubDate', datetime.now(IST).strftime('%a, %d %b %Y %H:%M:%S %z')),
                'category': item['category']
            }
    
    # Convert to list and sort by date
    sorted_items = []
    for link, item in all_items.items():
        pub_date = item.get('pubDate', '')
        pub_date_obj = None
        try:
            pub_date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
        except (ValueError, TypeError):
            pub_date_obj = datetime.now(IST)
            pub_date = pub_date_obj.strftime('%a, %d %b %Y %H:%M:%S %z')
        
        sorted_items.append({
            'title': item['title'],
            'link': link,
            'description': item['description'],
            'pubDate': pub_date,
            'category': item['category'],
            'pubDate_obj': pub_date_obj
        })
    
    # Sort by date, newest first
    sorted_items.sort(key=lambda x: x['pubDate_obj'], reverse=True)
    
    # Write the RSS feed
    with open(RSS_FILE, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<rss version="2.0">\n<channel>\n')
        f.write('<title>Gaurav - updates</title>\n')
        f.write(f'<link>{SITE_URL}/</link>\n')
        f.write('<description>RSS feed for blog, weblogs, and code updates.</description>\n')
        f.write(f'<lastBuildDate>{datetime.now(IST).strftime("%a, %d %b %Y %H:%M:%S %z")}</lastBuildDate>\n')
        
        for item in sorted_items[:30]:  # Limit to 30 most recent items
            f.write('<item>\n')
            f.write(f'<title>{escape(item["title"])}</title>\n')
            f.write(f'<link>{item["link"]}</link>\n')
            f.write(f'<description>{item["description"]}</description>\n')
            f.write(f'<pubDate>{item["pubDate"]}</pubDate>\n')
            f.write(f'<category>{item["category"]}</category>\n')
            f.write('</item>\n')
        
        f.write('</channel>\n</rss>\n')

# Generate the RSS feed
generate_rss()
