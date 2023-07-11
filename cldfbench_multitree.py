import pathlib
import collections

from cldfbench import Dataset as BaseDataset
from lxml import etree
import newick
from clldutils.misc import lazyproperty
from pyglottolog import Glottolog
from unidecode import unidecode
import nexus
from nexus.handlers.tree import Tree as NexusTree
from pycldf.sources import Sources


def text(e, tag):
    n = e.find(tag)
    if n is not None:
        return n.text or None


def norm_codes(c):
    codes = [
        unidecode(s.strip().replace('.', '-').replace(' ', '_')) for s in c.split(',') if s.strip()]
    return '_'.join(sorted(codes))


class Node:
    def __init__(self, e):
        self.e = e
        self.id = text(e, 'id')
        self.name = text(e, 'pri-name').replace('”', '')
        self.raw_codes = text(e, 'codes')
        self.codes = norm_codes(self.raw_codes)
        self.type = text(e, 'node-type')
        assert self.name and self.codes

    def __getitem__(self, item):
        return text(self.e, item)

    def __hash__(self):
        return hash(self.codes)


class Tree:
    def __init__(self, p):
        self.p = p
        self.tree = etree.parse(str(p)).find('./tree')
        self.root = self.tree.find('root')
        self.description = self.tree.find('description').text
        self.regions = [e.text for e in self.root.findall('region')]
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
        nodes = {}

        def tree(e):
            nn = Node(e)
            nid = (nn.id, nn.name)
            children = len(e.findall('children/child'))
            if nid in nodes:
                # There are a couple of duplicate nodes in the trees. If they have the same
                # number of children, we just drop them.
                assert nodes[nid] == children, 'duplicate node with different number of children!'
                return
            nodes[nid] = children
            self.nodes.append(nn)
            n = newick.Node(nn.codes)
            for c in e.findall('children/child'):
                nn = tree(c)
                if nn:
                    n.add_descendant(nn)
            return n

        return tree(self.root)


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "multitree"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        return super().cldf_specs()

    def cmd_download(self, args):
        pass

    def cmd_makecldf(self, args):
        self.schema(args.writer.cldf)

        args.writer.cldf.sources = Sources.from_file(self.etc_dir / 'sources.bib')
        pubs2source = {
            r['Citations']: r['Source'].split(';') if r['Source'] else []
            for r in self.etc_dir.read_csv('sources.csv', dicts=True)}

        langs = collections.defaultdict(set)
        trees = collections.OrderedDict()
        # We read the XML from the django app, because the other directories contain non-XML, like
        # "read timeout at /usr/share/perl5/Net/HTTP/Methods.pm".
        for p in sorted(
                self.dir.joinpath('xml_django_app').glob('*.xml'), key=lambda pp: int(pp.stem)):
            tree = Tree(p)
            pubs = (text(tree.root, 'publications') or '').strip()
            trees[p.stem] = tree.newick#.ascii_art()
            if len(tree.nodes) < 2:
                # A handful of trees have only one node. We skip these.
                del trees[p.stem]
                continue

            for n in tree.nodes:
                if n.codes not in langs:
                    args.writer.objects['LanguageTable'].append(dict(ID=n.codes))
                args.writer.objects['nodes.csv'].append(dict(
                    ID=n.id,
                    Language_ID=n.codes,
                    Name=n.name,
                    Tree_ID=p.stem,
                    Node_Type=n.type,
                    Comment=n['pubcomments'],
                    Geography=n['geography'],
                    Status=n['status'],
                    Alternative_Names=n['alt-names'],
                ))
                langs[n.codes].add(n.name)

            args.writer.objects['TreeTable'].append(dict(
                ID=p.stem,
                Name=p.stem,
                Description=tree.description,
                Media_ID='trees',
                Region=tree.regions,
                Source=pubs2source[pubs],
            ))

        args.writer.objects['MediaTable'].append(dict(
            ID='trees',
            Media_Type='text/plain',
            Download_URL='trees.nex',
        ))

        nex = nexus.NexusWriter()
        for name, t in trees.items():
            nex.trees.append(NexusTree.from_newick(t, name=name, rooted=True))
        nex.write_to_file(args.writer.cldf_spec.dir / 'trees.nex')

        # Now we try to supplement the language metadata with data from Glottolog.
        by_mt = {}
        by_name = {}
        # To match multitree languoids with Glottolog, we use ...
        for lang in args.glottolog.api.languoids():
            try:
                # ... alternative names of type "multitree" ...
                for name in lang.names['multitree']:
                    by_name[unidecode(name)] = lang
            except KeyError:
                pass
            try:
                # ... and identifiers of type "multitree" in Glottolog.
                by_mt[lang.identifier['multitree']] = lang
            except KeyError:
                pass

        for lg in args.writer.objects['LanguageTable']:
            glang = by_mt.get(lg['ID'])
            if not glang:
                for name in langs[lg['ID']]:
                    if unidecode(name) in by_name:
                        glang = by_name[unidecode(name)]
                        break
            if glang:
                lg['Name'] = glang.name
                lg['Latitude'] = glang.latitude
                lg['Longitude'] = glang.longitude
                lg['Glottocode'] = glang.id

    def schema(self, cldf):
        cldf.add_component('LanguageTable')
        cldf.add_component(
            'TreeTable',
            {
                'name': 'Region',
                'separator': ';',
                'propertyUrl': "http://purl.org/dc/terms/spatial",
            }
        )
        cldf.add_component('MediaTable')
        cldf.add_table(
            'nodes.csv',
            {
                "datatype": {
                    "base": "string",
                    "format": "[a-zA-Z0-9_\\-]+"
                },
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id",
                "required": True,
                "name": "ID"
            },
            {
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#languageReference",
                "name": "Language_ID"
            },
            {
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#comment",
                "name": "Comment"
            },
            "Tree_ID",
            {
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#name",
                "name": "Name"
            },
            {
                "name": "Node_Type",
                "datatype": {
                    "base": "string",
                    "format": "Dialect Group|Dialect|Language|Language Subgroup|Macro Code|Stock|Subgroup"}
            },
            "Geography",
            "Alternative_Names",
            "Status",
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
            # other-codes -> most probably WALS codes
            # start-date
            # end-date
        )
