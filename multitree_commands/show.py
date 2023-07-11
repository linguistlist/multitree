"""

"""
from pycldf.trees import TreeTable
from pycldf.sources import Sources
from termcolor import colored
from clldutils.clilib import Table, add_format

from cldfbench_multitree import Dataset


def register(parser):
    parser.add_argument('tree_id')
    add_format(parser, 'simple')


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

            print(tree.newick().ascii_art())
            print('')

            with Table(args, 'Label', 'Name', 'Glottocode', 'Type', 'Status', 'Geography') as t:
                for row in nodes:
                    t.append([
                        row['Language_ID'],
                        row['Name'],
                        langs[row['Language_ID']]['Glottocode'],
                        row['Node_Type'],
                        row['Status'],
                        row['Geography']])
            print('')

            if refs:
                print(colored('References:', attrs=['bold']))
                for ref in refs:
                    print(ref)
