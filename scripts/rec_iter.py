from yaml import load, dump, Loader, Dumper, SafeLoader
from hebrew_numbers import int_to_gematria
import os
import re
import sys
import json
import tempfile
import subprocess
from bs4 import BeautifulSoup
from lxml import etree


class Loader(SafeLoader):

    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(Loader, self).__init__(stream)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as f:
            return load(f, Loader)

Loader.add_constructor('!include', Loader.include)


def iterate(in_obj, out_obj, level=0, key=None, insert=False):
    if isinstance(in_obj, dict):
        for k, v in in_obj.items():

            if k == "text":
                insert = insert | True

            if insert:
                html_level = etree.Element(f"h{level+1}")
                html_level.text=str(k)
                out_obj.append(html_level)
            iterate(v, out_obj, level=level+1, key=k, insert=insert)

    elif isinstance(in_obj, list):
        for i in in_obj:
            iterate(i, out_obj, level, insert=insert)
    else:
        print(in_obj, f"[{level}]", key)


with open("yaml/torah/bereshit.yaml", "r") as f:
    jdict = load(f, Loader=Loader)
    odict = {}

    root = etree.Element("body")

    iterate(jdict, root)
    print(etree.tostring(root, pretty_print=True))