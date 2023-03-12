from yaml import load, dump, Loader, Dumper, SafeLoader
import os 


class Loader(SafeLoader):

    def __init__(self, stream):s
        self._root = os.path.split(stream.name)[0]
        super(Loader, self).__init__(stream)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as f:
            return load(f, Loader)

Loader.add_constructor('!include', Loader.include)

with open("../yaml/tanakh.yaml", "r") as f:
    jdict = load(f, Loader=Loader)

    with open("../yaml/super_merged.yaml", "w") as f:
        f.write(dump(jdict, Dumper=Dumper, allow_unicode=True, sort_keys=False))