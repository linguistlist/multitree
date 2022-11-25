import pathlib
import collections

from cldfbench import Dataset as BaseDataset
from lxml import etree
import newick
from clldutils.misc import lazyproperty
from clldutils.iso_639_3 import ISO
from pyglottolog import Glottolog
from unidecode import unidecode
from csvw.dsv import UnicodeWriter


def text(e, tag):
    n = e.find(tag)
    if n is not None:
        return n.text


def norm_codes(c):
    codes = [s.strip() for s in c.split(',') if s.strip()]
    return '_'.join(sorted(codes))


class Node:
    def __init__(self, e):
        self.name = text(e, 'pri-name').replace('”', '')
        self.codes = norm_codes(text(e, 'codes'))
        self.type = text(e, 'node-type')
        assert self.name and self.codes
        #self.newick_name = self.codes.replace('(', '_').replace(')', '_').replace(',', '_').replace(':', '_').replace(';', '_')


    def __hash__(self):
        return hash(self.codes)


class Tree:
    def __init__(self, p):
        self.tree = etree.parse(str(p)).find('./tree')
        self.root = self.tree.find('root')
        self.description = self.tree.find('description').text
        self.nodes = []

    @staticmethod
    def priname_and_codes(self, e):
        res = []
        for tag in ['pri-name', 'codes']:
            n = e.find(tag)
            res.append(n.text if n else None)
        return res

    @lazyproperty
    def newick(self):
        def tree(e):
            nn = Node(e)
            self.nodes.append(nn)
            n = newick.Node(nn.codes)
            for c in e.findall('children/child'):
                n.add_descendant(tree(c))
            return n

        return tree(self.root)


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "multitree"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        return super().cldf_specs()

    def cmd_download(self, args):
        """
        Download files to the raw/ directory. You can use helpers methods of `self.raw_dir`, e.g.

        >>> self.raw_dir.download(url, fname)
        """
        pass

    def cmd_makecldf(self, args):
        #
        # FIXME: We need a table "names" with fk into LanguageTable and list-valued fk into TreeTable
        #
        args.writer.cldf.add_component('LanguageTable')
        args.writer.cldf.add_component(
            'TreeTable',
            'region',  # FIXME: list-valued!
            # publications -> Source
        )
        args.writer.cldf.add_component('MediaTable')
        args.writer.cldf.add_table(
            'nodes.csv',
            # id
            # languageReference
            # tree-reference
            # pri-name
            # node-type
            #<node-type>Dialect Group</node-type>
            #<node-type>Dialect</node-type>
            #<node-type>Language</node-type>
            #<node-type>Language Subgroup</node-type>
            #<node-type>Macro Code</node-type>
            #<node-type>Stock</node-type>
            #<node-type>Subgroup</node-type>
            # pub-comments
            # geography
            # confidence
            #<confidence>0.0</confidence>
            #<confidence>0</confidence>
            #<confidence>-1.0</confidence>
            #<confidence></confidence>
            #<confidence>n</confidence>
            #<confidence>N</confidence>
            #<confidence nil="true"/>
            #<confidence nil="true"></confidence>
            #<confidence>v</confidence>
            #<confidence>y</confidence>
            #<confidence>Y</confidence>
            # sureness
            #<sureness type="integer">0</sureness>
            #<sureness type="integer">-1</sureness>
            #<sureness type="integer">1</sureness>
            #<sureness type="integer">2</sureness>
            # other-codes
            # status
            # alt-names
            # node-type
            # start-date
            # end-date
        )

        names = collections.defaultdict(list)
        langs = collections.defaultdict(set)
        gl = Glottolog('/home/robert_forkel/projects/glottolog/glottolog')
        by_mt = {}
        by_name = {}
        for lang in gl.languoids():
            try:
                for name in lang.names['multitree']:
                    #assert name not in by_name, 'duplicate multitree name!'
                    by_name[unidecode(name)] = lang
            except KeyError:
                pass
            try:
                by_mt[lang.identifier['multitree']] = lang
            except KeyError:
                pass

        src = set()
        for p in self.dir.joinpath('xml_django_app').glob('*.xml'):
            tree = Tree(p)
            pubs = text(tree.root, 'publications')
            if pubs.strip():
                src.add(pubs.strip())
            s = tree.newick#.ascii_art()

            for n in tree.nodes:
                langs[n.codes].add(n.name)
                if n.type == 'Language':
                    names[n.name].append(n.codes)

        #print(len(langs))
        unmatched = {k: v for k, v in langs.items() if k not in by_mt}
        #print(len(unmatched))
        unmatched = {k: v for k, v in unmatched.items() if not any(unidecode(n) in by_name for n in v)}
        #print(len(unmatched))

        i = 0
        for k, v in unmatched.items():
            i += 1
            if i > 10:
                break
            #print(k, v)

        #for lg in langs:
        #    if lg.codes not in iso:
        #        print(lg.name, lg.codes)

        #for code, names in by_code.items():
        #    if len(names) > 1:
        #        print(code, names)

        #for name, occs in sorted(names.items(), key=lambda i: -len(i[1])):
        #    if len(occs) > 10:
        #        print(name, occs)
