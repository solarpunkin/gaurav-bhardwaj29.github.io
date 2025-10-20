import os
import glob
import markdown
import yaml
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import re
import uuid

# --- Code block features ---

SCRIPT_ADDITIONS = '''
<script>
function copyCode(button, preId) {
    const preElement = document.getElementById(preId);
    if (preElement) {
        const codeElement = preElement.querySelector('code');
        if (!codeElement) return;
        const codeText = codeElement.innerText;
        navigator.clipboard.writeText(codeText).then(() => {
            const originalContent = button.innerHTML;
            button.innerHTML = 'Copied!';
            button.disabled = true;
            setTimeout(() => {
                button.innerHTML = originalContent;
                button.disabled = false;
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy code: ', err);
            const originalContent = button.innerHTML;
            button.innerHTML = 'Error!';
            button.disabled = true;
            setTimeout(() => {
                button.innerHTML = originalContent;
                button.disabled = false;
            }, 2000);
        });
    }
}
</script>'''

def add_code_block_features(html_content):
    """Add copy button and other features to code blocks."""
    processed_html = ""
    last_end = 0
    pattern = re.compile(r'<div class="codehilite[^"]*">')
    
    for match in pattern.finditer(html_content):
        start = match.start()
        processed_html += html_content[last_end:start]
        
        end_div_pos = html_content.find('</div>', start)
        if end_div_pos == -1:
            processed_html += html_content[start:]
            last_end = len(html_content)
            break

        end = end_div_pos + len('</div>')
        code_block_html = html_content[start:end]
        
        lang_match = re.search(r'language-([^\s"]+)', code_block_html)
        lang = lang_match.group(1) if lang_match else ''
        
        block_id = f"code-block-{uuid.uuid4().hex[:6]}"
        
        clipboard_svg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>'

        toolbar_html = f'''<div class="code-toolbar">
    <span class="language-name">{lang}</span>
    <button class="copy-btn" onclick="copyCode(this, \'{block_id}\')" aria-label="Copy code to clipboard">
        {clipboard_svg}
    </button>
    <a class="anchor-link" href="#{block_id}" aria-label="Link to this code block">🔗</a>
</div>'''
        
        modified_block = code_block_html.replace('class="codehilite', 'class="codehilite-container codehilite', 1)
        
        pre_pos = modified_block.find('<pre')
        if pre_pos != -1:
            modified_block = modified_block[:pre_pos] + toolbar_html + modified_block[pre_pos:]
            new_pre_pos = modified_block.find('<pre', pre_pos + len(toolbar_html))
            modified_block = modified_block[:new_pre_pos+4] + f' id="{block_id}"' + modified_block[new_pre_pos+4:]

        processed_html += modified_block
        last_end = end
        
    processed_html += html_content[last_end:]
    
    # Add the copy code script if not already present
    if 'function copyCode(' not in processed_html:
        processed_html += SCRIPT_ADDITIONS
        
    return processed_html

# --- Main script ---

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
    # Get slug from frontmatter or generate from filename
    slug = meta.get('slug', parse_slug_from_filename(md_file))
    # Get date from filename if present, else use now
    date_obj = parse_date_from_filename(md_file)
    html_body = markdown.markdown(body, extensions=['fenced_code', 'codehilite'])
    html_body = add_code_block_features(html_body)
    post = {
        'title': meta['title'],
        'weblog_title': meta.get('weblog_title', meta['title']),
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

# Generate individual post pages
for post in posts:
    post_dir = os.path.join('weblog', 'posts', post['slug'])
    os.makedirs(post_dir, exist_ok=True)
    
    with open(os.path.join(post_dir, 'index.html'), 'w', encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="../../weblog-style.css">
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
  <title>{post['title']}</title>
</head>
<body>
  <div class="weblog-post">
    <h1>{post['title']}</h1>
    <div class="weblog-meta">
      <span class="weblog-date">{post['date_str']}</span>
      <span class="weblog-tags">
        {''.join(f'<a href="../../tags/{tag}.html" class="weblog-tag">{tag}</a>' for tag in post['tags'])}
      </span>
    </div>
    <div class="weblog-content">
      {post['body']}
    </div>
    <div class="weblog-footer">
      <a href="../../" class="weblog-back">← Back to all posts</a>
    </div>
  </div>
  {SCRIPT_ADDITIONS}
</body>
</html>""")


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
  <ul class="weblog-list"><li><a href="../">← LOGS</a></li>""")
        for post in tag_posts_sorted:
            url = f"../posts/{post['slug']}/"
            f.write(f'<li><a href="{url}">{post["title"]}</a> <span class="weblog-date">{post["date_str"]}</span></li>\n')
        f.write(f"</ul>\n{SCRIPT_ADDITIONS}</body></html>")

# Generate main index.html (recent weblogs: newest first)
posts_desc = sorted(posts, key=lambda p: p['date'], reverse=True)

# Read the existing index.html to preserve its structure
with open(INDEX_FILE, 'r', encoding="utf-8") as f:
    content = f.read()

# Find the tags div and replace its content
tags_start = content.find('<div class="weblog-tags"')
tags_end = content.find('</div>', tags_start) + len('</div>')

# Generate new tags content
new_tags = []
for tag, tag_posts in sorted(tags_dict.items()):
    new_tags.append(f'<button class="weblog-tag" data-tag="{tag}" onclick="toggleTag(this)">{tag} ({len(tag_posts)})</button>')

# Generate recent posts
recent_posts = []
for post in posts_desc[:10]:
    url = f"posts/{post['slug']}/"
    tags_str = ','.join(post['tags'])
    recent_posts.append(f'<li data-tags="{tags_str}"><a href="{url}">{post["title"]}</a> <span class="weblog-date">{post["date_str"]}</span></li>')

# Generate all posts for search
all_posts = []
for post in posts_desc:
    url = f"posts/{post['slug']}/"
    tags_str = ','.join(post['tags'])
    all_posts.append(f'<li data-tags="{tags_str}"><a href="{url}">{post["title"]}</a> <span class="weblog-date">{post["date_str"]}</span></li>')

# Replace the tags section
new_content = (
    content[:tags_start] +
    f'<div class="weblog-tags" role="region" aria-label="Post tags">\n' +
    '\n'.join(new_tags) +
    '\n</div>\n' +
    content[tags_end:]
)

# Replace the recent posts list
recent_start = new_content.find('<ul class="weblog-list" id="weblog-list">') + len('<ul class="weblog-list" id="weblog-list">')
recent_end = new_content.find('</ul>', recent_start)
new_content = (
    new_content[:recent_start] +
    '\n' + '\n'.join(recent_posts) + '\n' +
    new_content[recent_end:]
)

# Replace the all posts list (for search)
all_start = new_content.find('<ul class="weblog-list" id="all-weblogs"')
if all_start > 0:  # Only if the all-weblogs list exists
    all_start = new_content.find('>', all_start) + 1
    all_end = new_content.find('</ul>', all_start)
    new_content = (
        new_content[:all_start] +
        '\n' + '\n'.join(all_posts) + '\n' +
        new_content[all_end:]
    )

# Check if JavaScript is already present in the content
js_start_marker = 'let selectedTags = [];'
if js_start_marker not in new_content:
    # JavaScript for filtering
    new_content += """
<script>
let selectedTags = [];

function toggleTag(tagEl) {
  const tagName = tagEl.dataset.tag;
  const index = selectedTags.indexOf(tagName);
  if (index > -1) {
    selectedTags.splice(index, 1);
    tagEl.classList.remove('selected');
  } else {
    selectedTags.push(tagName);
    tagEl.classList.add('selected');
  }
  filterPosts();
}

function filterPosts() {
  const searchQuery = document.getElementById('weblog-search').value.toLowerCase();
  const allLis = document.getElementById('all-weblogs').getElementsByTagName('li');
  
  let anyFilterActive = searchQuery !== '' || selectedTags.length > 0;

  if (anyFilterActive) {
    document.getElementById('most-recent-heading').style.display = 'none';
    document.getElementById('weblog-list').style.display = 'none';
    document.getElementById('all-logs-heading').style.display = 'block';
    document.getElementById('all-weblogs').style.display = 'block';
    document.getElementById('all-weblogs').style.maxHeight = '400px';
    document.getElementById('all-weblogs').style.overflowY = 'auto';

    for (let i = 0; i < allLis.length; i++) {
      const li = allLis[i];
      const postText = (li.textContent || li.innerText).toLowerCase();
      const postTags = (li.dataset.tags || '').split(',');

      const searchMatch = postText.includes(searchQuery);
      const tagMatch = selectedTags.length === 0 || selectedTags.every(tag => postTags.includes(tag));
      
      if (searchMatch && tagMatch) {
        li.style.display = '';
      } else {
        li.style.display = 'none';
      }
    }
  } else {
    showDefaultView();
  }
}

function showDefaultView() {
    document.getElementById('most-recent-heading').innerText = "Most Recent";
    document.getElementById('most-recent-heading').style.display = 'block';
    document.getElementById('weblog-list').style.display = 'block';
    document.getElementById('weblog-list').style.maxHeight = '';
    document.getElementById('weblog-list').style.overflowY = '';
    document.getElementById('all-logs-heading').style.display = 'none';
    document.getElementById('all-weblogs').style.display = 'none';

    const allLis = document.getElementById('all-weblogs').getElementsByTagName('li');
    for (let i = 0; i < allLis.length; i++) {
        allLis[i].style.display = "";
    }

    const ul = document.getElementById('weblog-list');
    ul.innerHTML = '';
    for (let i = 0; i < 10 && i < allLis.length; i++) {
      ul.appendChild(allLis[i].cloneNode(true));
    }
}

function handleSearchInput(input) {
  filterPosts();
}

function showAllLogs() {
  document.getElementById('most-recent-heading').style.display = 'none';
  document.getElementById('weblog-list').style.display = 'none';
  document.getElementById('all-logs-heading').style.display = 'block';
  document.getElementById('all-weblogs').style.display = 'block';
  const weblogList = document.getElementById('all-weblogs');
  weblogList.style.maxHeight = '400px';
  weblogList.style.overflowY = 'auto';
}

// Initial setup
document.addEventListener('DOMContentLoaded', () => {
    showDefaultView();
});
</script>"""

# Write the updated content back to the file
with open(INDEX_FILE, 'w', encoding="utf-8") as f:
    f.write(new_content)

print("Weblog index updated successfully!")
