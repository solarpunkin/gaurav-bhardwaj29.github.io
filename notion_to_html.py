import os
import datetime
from notion_client import Client
from pathlib import Path
from markdownify import markdownify as md
from html import escape
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

notion = Client(auth=NOTION_TOKEN)
OUTPUT_DIR = Path("til")
STYLE_CSS = "til/til-style.css"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_text(rich):
    if not rich:
        return ""
    return "".join([r.get("plain_text", "") for r in rich])


def fetch_til_posts():
    response = notion.databases.query(
        database_id=DATABASE_ID,
        filter={
            "and": [
                {"property": "Published", "checkbox": {"equals": True}},
                {"property": "Category", "rich_text": {"equals": "til"}}
            ]
        },
        sorts=[{"property": "Posted on", "direction": "ascending"}]
    )
    return response["results"]


def convert_to_markdown(blocks):
    markdown = ""
    for block in blocks:
        block_type = block.get("type")
        content = block.get(block_type, {})

        if block_type == "paragraph":
            markdown += get_text(content.get("rich_text", [])) + "\n\n"

        elif block_type == "heading_1":
            markdown += "# " + get_text(content.get("rich_text", [])) + "\n\n"

        elif block_type == "heading_2":
            markdown += "## " + get_text(content.get("rich_text", [])) + "\n\n"

        elif block_type == "heading_3":
            markdown += "### " + get_text(content.get("rich_text", [])) + "\n\n"

        elif block_type == "bulleted_list_item":
            markdown += "- " + get_text(content.get("rich_text", [])) + "\n"

        elif block_type == "numbered_list_item":
            markdown += "1. " + get_text(content.get("rich_text", [])) + "\n"

        elif block_type == "quote":
            markdown += "> " + get_text(content.get("rich_text", [])) + "\n\n"

        elif block_type == "code":
            lang = content.get("language", "text")
            code_text = get_text(content.get("rich_text", []))
            markdown += f"```{lang}\n{code_text}\n```\n\n"

        elif block_type == "image":
            url = content.get("external", {}).get("url") or content.get("file", {}).get("url")
            markdown += f"![image]({url})\n\n"

        elif block_type == "equation":
            expr = content.get("expression", "")
            markdown += f"$$ {expr} $$\n\n"

        else:
            markdown += f"<!-- skipped block: {block_type} -->\n\n"

    return markdown


def generate_html(post, blocks, previous_post=None, next_post=None):
    props = post["properties"]
    title = props["Title"]["title"][0]["text"]["content"]
    slug = props["Slug"]["rich_text"][0]["text"]["content"]
    date = props["Posted on"]["date"]["start"]
    tags = [t["name"] for t in props.get("Tags", {}).get("multi_select", [])]
    date_str = datetime.datetime.fromisoformat(date).strftime("%B %d, %Y")
    tag_html = " ".join(f"<code>{escape(tag)}</code>" for tag in tags)

    markdown = convert_to_markdown(blocks)
    html_body = md(markdown)

    nav = "<nav>"
    if previous_post:
        nav += f'<a href="../{previous_post}/">← Previous</a>'
    if next_post:
        nav += f'<a href="../{next_post}/">Next →</a>'
    nav += "</nav>"

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <title>{escape(title)}</title>
  <link rel=\"stylesheet\" href=\"{STYLE_CSS}\">
</head>
<body>
  <main>
    <h1>{escape(title)}</h1>
    <p><small>{date_str}</small></p>
    <p>{tag_html}</p>
    <article>{html_body}</article>
    {nav}
  </main>
</body>
</html>"""


def write_html(slug, html):
    path = OUTPUT_DIR / slug / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    posts = fetch_til_posts()
    slugs = [post["properties"]["Slug"]["rich_text"][0]["text"]["content"] for post in posts]

    for i, post in enumerate(posts):
        blocks = notion.blocks.children.list(post["id"])['results']
        prev_slug = slugs[i - 1] if i > 0 else None
        next_slug = slugs[i + 1] if i < len(slugs) - 1 else None
        html = generate_html(post, blocks, prev_slug, next_slug)
        slug = slugs[i]
        write_html(slug, html)
        print(f"Wrote til/{slug}/index.html")


if __name__ == "__main__":
    main()
