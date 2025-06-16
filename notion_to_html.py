import os
import datetime
from notion_client import Client
from markdownify import markdownify as md
import html
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

notion = Client(auth=NOTION_TOKEN)

def slugify(text):
    return text.strip().lower().replace(" ", "-")

def fetch_published_posts():
    response = notion.databases.query(
        **{
            "database_id": DATABASE_ID,
            "filter": {
                "property": "Published",
                "checkbox": {"equals": True}
            }
        }
    )
    return response["results"]

def convert_to_html(post):
    props = post["properties"]
    title = props["Name"]["title"][0]["text"]["content"]
    slug = props["Slug"]["rich_text"][0]["text"]["content"]
    date = props["Posted on"]["date"]["start"]
    tags = [t["name"] for t in props["Tags"]["multi_select"]]

    blocks = notion.blocks.children.list(post["id"])["results"]
    markdown = ""
    for block in blocks:
        block_type = block["type"]
        if block_type == "paragraph":
            markdown += block["paragraph"]["rich_text"][0]["text"]["content"] + "\n\n"
        elif block_type == "heading_1":
            markdown += "# " + block[block_type]["rich_text"][0]["text"]["content"] + "\n\n"
        elif block_type == "heading_2":
            markdown += "## " + block[block_type]["rich_text"][0]["text"]["content"] + "\n\n"
        elif block_type == "bulleted_list_item":
            markdown += "- " + block[block_type]["rich_text"][0]["text"]["content"] + "\n"
        # Add more types if needed

    html_body = md(markdown)
    tags_html = " ".join(f"<code>{t}</code>" for t in tags)
    formatted_date = datetime.datetime.fromisoformat(date).strftime("%B %d, %Y")

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="/style.css" />
</head>
<body>
  <main>
    <h1>{html.escape(title)}</h1>
    <p><small>{formatted_date}</small></p>
    <p>{tags_html}</p>
    <article>{html_body}</article>
  </main>
</body>
</html>
"""
    return slug, html_template

def main():
    Path("public").mkdir(exist_ok=True)
    for post in fetch_published_posts():
        slug, content = convert_to_html(post)
        output_dir = Path("public") / slug
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / "index.html", "w") as f:
            f.write(content)

if __name__ == "__main__":
    main()
