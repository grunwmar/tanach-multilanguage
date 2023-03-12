from yaml import load, dump, Loader, Dumper, SafeLoader
from hebrew_numbers import int_to_gematria
import os
import re
import sys
import json
import tempfile
import subprocess
from bs4 import BeautifulSoup

conf = json.loads(os.environ["PY_CONFIG"])


class Loader(SafeLoader):

    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(Loader, self).__init__(stream)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as f:
            return load(f, Loader)

Loader.add_constructor('!include', Loader.include)


def fix_yiddish_letters(string):
    try:
        substitute_list = [
            ["וו", "װ"],
            ["וי", "ױ"],
            ["יי", "ײ"],
            ["ײַ", "ײַ"],
            ["יִ", "יִ"],
        ]
        for s in substitute_list:
            subst_regx = re.compile("{}".format(s[0]), 0)
            string = subst_regx.sub(s[1], string)
    except TypeError:
        return string
    return string


def replace_brackets(string, old=('[', ']'), new=('<em>', '</em>')):
    string = string.replace(old[0], new[0]).replace(old[1], new[1])
    return string


def column_numbering(number, side):
    lang = conf["layout"]["numbering"][side]
    if lang == "hebrew":
        return int_to_gematria(number, gershayim=False)
    elif lang == "latin":
        return str(number)
    else:
        return ""


grid_cols_str = " ".join(conf["layout"]["columns"])
grid_areas_str = ''

for row in conf["layout"]["areas"]:
    grid_areas_str += '"{}"\n'.format(" ".join(row))

hebrew_font = conf["fonts"]["hebrew"][0]
latin_font = conf["fonts"]["latin"][0]

hebrew_font_size = conf["fonts"]["hebrew"][1]
latin_font_size = conf["fonts"]["latin"][1]


if  conf["layout"]["numbering"]["left"] == "latin":
    numbering_font_left = latin_font
elif conf["layout"]["numbering"]["left"] == "hebrew":
    numbering_font_left = "none"
else:
    numbering_font_left = conf["fonts"]["hebrew"]


if  conf["layout"]["numbering"]["right"] == "latin":
    numbering_font_right = latin_font
elif conf["layout"]["numbering"]["right"] == "hebrew":
    numbering_font_right = hebrew_font
else:
    numbering_font_right = "none"


css_style = f"""
            body{{
                    }}

            hr{{
                border: none;
            }}

            h1, h2, h3, h4 {{
                text-align: center;
                margin: 0 auto;
                width: 50%;
                font-family: "{hebrew_font}";
                margin-bottom: 1em;
            }}

            h1 {{
                font-size: 7em !important;
                margin-top: 2em;
            }}


            h2 {{
                font-size: 5em !important;
                margin-top: 1em;
            }}

            h3 {{
                font-size: 3em !important;
                margin-top: 1.5em;
            }}

            h4 {{
                font-size: 1em !important;
            }}

            .verse {{
                page-break-inside: avoid;
                break-inside: avoid;
                vertical-align: top;
                width: 100%;
            }}

            .c_r, .c_l{{
                width: 1rem;
                vertical-align: top;
                padding: 0.1rem;
                text-align: center !important;
            }}

            .c_l {{
                font-family: '{numbering_font_left}' !important;
            }}


            .c_r {{
                font-family: '{numbering_font_right}' !important;
            }}

            [data-lang=latin]{{
                font-size: {latin_font_size}pt !important;
            }}

            [data-lang=hebrew]{{
                font-size: {hebrew_font_size}pt !important;;
            }}

            .c_l i, .c_r i {{
                font-style: normal;
                font-size: 90% !important;
            }}

            td{{
                vertical-align: top;
            }}

            .container{{
                display: grid; 
                row-gap: 0.25em;
                grid-template-columns: {grid_cols_str};
                grid-template-areas: 
                {grid_areas_str};
            }}

            p{{
                margin: 0;
                padding: 0 0.25rem;
       
            }}

            [lang=he], [lang=yi]{{
                direction: rtl;
                text-align: right;
                font-family: '{hebrew_font}';
                font-size: {hebrew_font_size}pt;
            }}


            [lang=cs], [lang=pl], [lang=en]{{
                direction: ltr;
                text-align: justify;
                font-family: '{latin_font}';
                font-size: {latin_font_size}pt;
                
            }}

            p[lang=he]{{
                grid-area: he;
            }}

            p[lang=yi]{{
                text-align: justify;
                grid-area: yi;
            }}

            p[lang=cs]{{
                grid-area: cs;
            }}

            p[lang=pl]{{
                grid-area: pl;
            }}
"""

soup = BeautifulSoup("<html><head></head><body></body></html>", 'lxml')
html_style = soup.new_tag("style")
html_style.string = css_style
soup.html.head.append(html_style)

with open("yaml/tanakh.yaml", "r") as f:
    jdict = load(f, Loader=Loader)
    html_main_title = soup.new_tag("h1")
    html_main_title.string = jdict["title"]["he"]
    soup.html.body.append(html_main_title)

    for volume in jdict["volumes"]:
        html_separator = soup.new_tag("hr")
        soup.html.body.append(html_separator)
        volume_title = volume["title"]["he"]
        html_volume_title = soup.new_tag("h2")
        html_volume_title.string = volume_title
        soup.html.body.append(html_volume_title)

        for book in volume["books"]:
            html_separator = soup.new_tag("hr")
            soup.html.body.append(html_separator)
            book_title = book["title"]["he"]
            html_book_title = soup.new_tag("h3")
            html_book_title.string = book_title
            soup.html.body.append(html_book_title)

            for chapter_index, chapter in book["text"].items():
                html_separator = soup.new_tag("hr")
                soup.html.body.append(html_separator)

                html_chapter_index = soup.new_tag("h4")
                html_chapter_index.string = book_title + " " + int_to_gematria(chapter_index, gershayim=False) + " : " + str(chapter_index)
                soup.html.body.append(html_chapter_index)

                for verse_index, verse in chapter.items():
                    html_verse = soup.new_tag("table")
                    html_verse["class"] = "verse"
                    html_tr = soup.new_tag("tr")

                    html_td_left = soup.new_tag("td")
                    html_td_left["class"] = "c_l"
                    html_td_left["data-lang"] = conf["layout"]["numbering"]["left"]

                    html_td_i_left = soup.new_tag("i")
                    html_td_i_left.string = column_numbering(verse_index, side="left")
                    html_td_left.append(html_td_i_left)

                    html_td_middle = soup.new_tag("td")
                    html_td_middle["class"] = "c_m"

                    html_td_right = soup.new_tag("td")
                    html_td_right["class"] = "c_r"
                    html_td_right["data-lang"] = conf["layout"]["numbering"]["right"]

                    html_td_i_right = soup.new_tag("i")
                    html_td_i_right.string = column_numbering(verse_index, side="right")
                    html_td_right.append(html_td_i_right)

                    html_container = soup.new_tag("div")
                    html_container["class"] = "container"

                    for lang, text in verse.items():
                        if lang not in conf["languages"]: continue
                        html_p = soup.new_tag("p")
                        html_p["lang"] = lang

                        if lang == "yi":
                            text = fix_yiddish_letters(text)
                        
                        text = replace_brackets(text, old=('[(', ')]'), new=('<em>(', ')</em>'))
                        text = replace_brackets(text, old=('(', ')'), new=('<em>(', ')</em>'))
                        text = replace_brackets(text, old=('[', ']'), new=('<em>', '</em>'))

                        html_p.string = text
                        html_container.append(html_p) 
                        #print(volume_title, book_title, chapter_index, verse_index, lang, text)
                        ...
                    html_td_middle.append(html_container)
                    html_tr.append(html_td_left)
                    html_tr.append(html_td_middle)
                    
                    html_tr.append(html_td_right)
                    html_verse.append(html_tr)
                    soup.html.body.append(html_verse)
        

    with tempfile.TemporaryDirectory() as tmpd:
        tmp_file = os.path.join(tmpd, "book.html")
        lang_signature = "-".join(conf["languages"])
        os.environ["PY_BOOK_TMPFILE"] = tmp_file
        os.environ["PY_BOOK_FILENAME"] = conf["output"]["filename"]
        os.environ["PY_BOOK_FORMAT"] = conf["output"]["format"]

        os.environ["PY_BOOK_MARGIN_TOP"] = str(conf["margins"]["top"])
        os.environ["PY_BOOK_MARGIN_BOTTOM"] = str(conf["margins"]["bottom"])
        os.environ["PY_BOOK_MARGIN_LEFT"] = str(conf["margins"]["left"])
        os.environ["PY_BOOK_MARGIN_RIGHT"] = str(conf["margins"]["right"])

        os.environ["PY_BOOK_FONT_SIZE"] = str(conf["font_size"])

        os.environ["PY_BOOK_TITLE"] = jdict["title"]["he"]
        os.environ["PY_BOOK_LANGSIGNATURE"] = lang_signature

        with open(tmp_file, "w") as f:
            html=str(soup.prettify())
            html = html.replace("&gt;", ">").replace("&lt;", "<")
            f.write(html)

        subprocess.run(["bash", "scripts/make_book.sh"])
    