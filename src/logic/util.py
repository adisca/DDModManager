import os
import re


def mods_path(gameFolder: str) -> str:
    return os.path.join(gameFolder, "mods")


def mod_page_url(mod_id: str) -> str:
    return f"https://steamcommunity.com/sharedfiles/filedetails/?id={mod_id}"


def convert_bbcode_to_html(text: str) -> str:
    # Replace headings [h1]
    bbcode_text = re.sub(r'\[h1](.*?)\[/h1]', r'<div class="bb_h1">\1</div>', text)

    # Replace bold tags [b]
    bbcode_text = re.sub(r'\[b](.*?)\[/b]', r'<strong>\1</strong>', bbcode_text)

    # Replace images [img]
    bbcode_text = re.sub(r'\[img](.*?)\[/img]', r'<img src="\1">', bbcode_text)

    # Replace links [url]
    bbcode_text = re.sub(r'\[url=(.*?)](.*?)\[/url]', r'<a href="\1">\2</a>', bbcode_text)

    # Handle newlines
    bbcode_text = bbcode_text.replace('\n', '<br>')

    # Handle nested tags (e.g., [url][img][/url])
    while re.search(r'\[url=(.*?)](.*?)\[/url]', bbcode_text):
        bbcode_text = re.sub(r'\[url=(.*?)](.*?)\[/url]', r'<a href="\1">\2</a>', bbcode_text)

    return bbcode_text
