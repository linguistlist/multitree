import argparse
import pathlib
import collections

from cldfbench import Dataset as BaseDataset
from lxml import etree
import newick
from clldutils.misc import lazyproperty
from clldutils.markup import add_markdown_text
from unidecode import unidecode
from pycldf.sources import Sources
from commonnexus import Nexus
from commonnexus.blocks.trees import Trees

NOTES = """
From the former MultiTree website:

### Why MultiTree?

MultiTree provides a unique approach to historical linguistic research, representing the most
complete collection of language relationship hypotheses in a user-friendly, visually-appealing,
and interactive format. Not only is it fun and informative, but it is a useful resource that gathers
scholarly work and makes it accessible to academics and the public alike.
                            
MultiTree is also an innovative tool for typological analysis, especially among lesser-known
languages. It facilitates interdisciplinary collaboration with linguists to reach
more accurate conclusions about human language, culture, and history.


### Disclaimer

The trees in MultiTree are intended to be faithful representations of their sources,
but sometimes it can be difficult to capture a scholar's intentions in a graphical
representation. Whenever possible, editors have added comments to disambiguate or
clarify their interpretations. However, it is always recommended that users refer to the
original source for a better understanding of the scholar's hypothesis.
                            
MultiTree aims to collect as many hypotheses about language relationships as possible
so that users may compare them. Inclusion of a tree does not indicate validity of the
scholar's hypothesis or acceptance by the academic community.
                            
**Regarding contact languages (creoles, pidgins, mixed languages) and language isolates**
Although isolates have no known genetic affiliation, and the origins of contact
languages are heavily contested, they have been included in the MultiTree
database in order to make information about them available to scholars and to accurately
represent whatever hypothesis the original scholar is making. "Trees" that include these
languages do not reflect genetic affiliation unless this was the intention of the author.
"""


def text(e, tag):
    n = e.find(tag)
    if n is not None:
        return n.text or None


def norm_codes(c):
    codes = [
        unidecode(s.strip().replace('.', '-').replace(' ', '_')) for s in c.split(',') if s.strip()]
    return '_'.join(sorted(codes))


class Node:
    """
    codes 102561

    sureness 75682   ['-1', '0', '1', '2']
    confidence 75669

    other-codes 2501   ['0g3', '0h2', '0x1', '1jm', 'aab']
    start-date 665
    end-date 663
    """
    __metadata__ = [
        ('Comment', 'pub-comments'),
        ('Geography', 'geography'),
        ('Status', 'status'),
        ('Alternative_Names', 'alt-names'),
        ('Other_Codes', 'other-codes'),
        ('Start_Date', 'start-date'),
        ('End_Date', 'end-date'),
    ]

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

    def cmd_readme(self, args):
        return add_markdown_text(super().cmd_readme(args), '', section='Description')

    def cmd_makecldf(self, args):
        self.schema(args.writer.cldf)

        args.writer.cldf.sources = Sources.from_file(self.etc_dir / 'sources.bib')
        pubs2source = {
            r['Citations']: r['Source'].split(';') if r['Source'] else []
            for r in self.etc_dir.read_csv('sources.csv', dicts=True)}

        langs = collections.defaultdict(set)
        trees = collections.OrderedDict()
        for p in sorted(self.raw_dir.glob('*.xml'), key=lambda pp: int(pp.stem)):
            tree = Tree(p)
            pubs = (text(tree.root, 'publications') or '').strip()
            trees[p.stem] = tree.newick
            if len(tree.nodes) < 2:
                # A handful of trees have only one node. We skip these.
                del trees[p.stem]
                continue

            node_metadata = set()

            for n in tree.nodes:
                if n.codes not in langs:
                    args.writer.objects['LanguageTable'].append(dict(ID=n.codes, Name=n.codes))
                md = {}
                for attr, key in Node.__metadata__:
                    if n[key]:
                        node_metadata.add(attr)
                        md[attr] = n[key]

                args.writer.objects['nodes.csv'].append(dict(
                    ID=n.id,
                    Language_ID=n.codes,
                    Name=n.name,
                    Tree_ID=p.stem,
                    Node_Type=n.type,
                    **md))
                langs[n.codes].add(n.name)

            args.writer.objects['TreeTable'].append(dict(
                ID=p.stem,
                Name=p.stem,
                Description=tree.description,
                Media_ID='trees',
                Region=tree.regions,
                Source=pubs2source[pubs],
                Node_Metadata=sorted(node_metadata)
            ))

        args.writer.objects['MediaTable'].append(dict(
            ID='trees',
            Media_Type='text/plain',
            Download_URL='trees.nex',
        ))

        nex = Nexus('#NEXUS')
        nex.append_block(Trees.from_data(*[(name, t, True) for name, t in trees.items()]))
        args.writer.cldf_spec.dir.joinpath('trees.nex').write_text(str(nex))

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
            },
            {
                'name': 'Node_Metadata',
                'dc:description': "",
                'separator': ';',
            }
        )
        cldf.add_component('MediaTable')
        t = cldf.add_table(
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
            {
                "name": "Status",
                "dc:description": "Endangerment status of the languoid",
                "datatype": {"base": "string", "format":
                    "Critically Endangered|Extinct|Extinct but still in Use|Extinct with children|Nearly Extinct|Revived|Vulnerable"},
            },
            {
                "name": "Other_Codes",
                "dc:description": "Other language codes assigned to the languoid",
            },
            {
                "name": "Start_Date",
                "dc:description": "Earliest time of documentation",
            },
            {
                "name": "End_Date",
                "dc:description": "Latest time of documentation",
            },
            {
                "name": "Confidence",
                "dc:description": "",
            },
            {
                "name": "Sureness",
                "dc:description": "",
            },
        )
        t.common_props['dc:description'] = \
            ("Nodes in MultiTree trees are associated with a languoid, i.e. a language group, "
             "language or dialect, and carry metadata.")
        cldf.add_foreign_key('nodes.csv', 'Tree_ID', 'TreeTable', 'ID')
