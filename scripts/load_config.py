from yaml import load, dump, Loader, Dumper, SafeLoader
import os
import subprocess
import json

def load_config():
    with open("build_conf.yaml", "r") as f:
        ydict = load(f, Loader=Loader)
        return ydict

os.environ["PY_CONFIG"] = json.dumps(load_config())

subprocess.run(["python", "scripts/make_html.py"])