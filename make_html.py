from yaml import load, dump, Loader, Dumper, SafeLoader
from hebrew_numbers import int_to_gematria
import os
import re
import sys
from bs4 import BeautifulSoup
sys.setrecursionlimit(100000)

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
    """
    try:
        re_brackets = re.compile(f'({old[0]}([\w\s\d.,!?:;\'\u00A0-\u0903"\-\<\>/\"]*){old[1]})')
        found_brackets = re_brackets.findall(string)
        new_string = string

        for brackets in found_brackets:
            new_string = new_string.replace(brackets[0], f'{new[0]}{brackets[1]}{new[1]}')

        return new_string
    except TypeError:
        ...
    """
    string = string.replace(old[0], new[0]).replace(old[1], new[1])
    return string

css_style = """
body{
        }
hr{
    border: none;
}
        h1 {
            font-size: 4em !important;
        }

        h1, h2, h3, h4 {
            text-align: center;
            margin: 0 auto;
            width: 50%;
            font-family: "Taamey Frank CLM";
            margin-bottom: 1em;
        }

            .verse {
                page-break-inside: avoid;
                break-inside: avoid;
                vertical-align: top;
      
                width: 100%;
            }

            .c_r, .c_l{
                width: 1rem;
                vertical-align: top;
                padding: 0.1rem;
                text-align: center !important;
                font-family: "Taamey Frank CLM";

                font-size: 0.92rem !important;
            }

            .c_l {
                font-family: 'EB Garamond';
                font-size: 0.8rem !important;
            }

            td{
                vertical-align: top;
            }

            .container{
                display: grid; 

                row-gap: 0.25em;
                grid-template-columns: 50% 50%;
                grid-template-areas: 
                    "czech hebrew"
                    "polish yiddish";
            }

            p{
                #display: inline-block;
                margin: 0;
                padding: 0 0.25rem;
       
            }

            [lang=he], [lang=yi]{
                direction: rtl;
                text-align: right;
                font-family: 'Taamey Frank CLM';
                font-size: 0.99em;
            }


            [lang=cs], [lang=pl], [lang=en]{
                direction: ltr;
                text-align: justify;
                font-family: 'EB Garamond';
                font-size: 0.92em;
                
            }


            p[lang=he]{
                grid-area: hebrew;
                font-size: 1.25em;
            }
            p[lang=yi]{
                text-align: justify;
                grid-area: yiddish;
            }
            p[lang=cs]{
                grid-area: czech;
            }
            p[lang=pl]{
                grid-area: polish;
            }
"""

soup = BeautifulSoup("<html><head></head><body></body></html>", 'lxml')
html_style = soup.new_tag("style")
html_style.string = css_style
soup.html.head.append(html_style)

with open("tanakh.yaml", "r") as f:
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
                    html_td_left.string = str(verse_index)

                    html_td_middle = soup.new_tag("td")
                    html_td_middle["class"] = "c_m"

                    html_td_right = soup.new_tag("td")
                    html_td_right["class"] = "c_r"
                    html_td_right.string = int_to_gematria(verse_index, gershayim=False)

                    html_container = soup.new_tag("div")
                    html_container["class"] = "container"

                    for lang, text in verse.items():
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
        

with open("tanakh.html", "w") as f:
    html=str(soup.prettify())
    html = html.replace("&gt;", ">").replace("&lt;", "<")
    f.write(html)