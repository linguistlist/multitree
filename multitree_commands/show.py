"""
Print a summary of a MultiTree to the screen.
"""
from pycldf.trees import TreeTable
from pycldf.sources import Sources
from termcolor import colored
from clldutils.clilib import Table, add_format

from cldfbench_multitree import Dataset


def register(parser):
    parser.add_argument('tree_id')
    add_format(parser, 'simple')
    parser.add_argument('--named-nodes', action='store_true', default=False)


def run(args):
    cldf = Dataset().cldf_reader()

    nodes = [row for row in cldf['nodes.csv'] if row['Tree_ID'] == args.tree_id]
    lids = [r['Language_ID'] for r in nodes]
    langs = {r['ID']: r for r in cldf['LanguageTable'] if r['ID'] in lids}

    for tree in TreeTable(cldf):
        if tree.id == args.tree_id:
            refs = []
            print('')
            print(colored(tree.row['Description'], attrs=['bold', 'underline']))
            print('')

            for i, src in enumerate(tree.row['Source']):
                if i == 0:
                    print(colored('Source:', attrs=['bold']))
                sid, pages = Sources.parse(src)
                src = cldf.sources[sid]
                print('    {}{}'.format(src.refkey(), ' [{}]'.format(pages) if pages else ''))
                refs.append(src)

            nwk = tree.newick()
            if args.named_nodes:
                # rename nodes
                nwk.rename(auto_quote=True, **{row['Language_ID']: row['Name'] for row in nodes})

            print(nwk.ascii_art())
            print('')

            with Table(args, 'Label', 'Name', 'Glottocode', 'Type', *tree.row['Node_Metadata']) as t:
                for row in nodes:
                    t.append([
                        row['Language_ID'],
                        row['Name'],
                        langs[row['Language_ID']]['Glottocode'],
                        row['Node_Type'],
                    ] + [row[key] for key in tree.row['Node_Metadata']])
            print('')

            if refs:
                print(colored('References:', attrs=['bold']))
                for ref in refs:
                    print(ref)
