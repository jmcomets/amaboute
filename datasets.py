import os
import sys
import json

__all__ = ('load_datasets',)

this_dir = os.path.dirname(os.path.realpath(__file__))
datasets_dir = os.path.join(this_dir, 'data', 'celebrities')
datasets_file = os.path.join(datasets_dir, 'index.json')

def load_datasets():
    with open(datasets_file, 'r') as fp:
        datasets = json.load(fp)
    for nick, dataset in datasets.items():
        try:
            with open(os.path.join(datasets_dir, dataset), 'r') as fp:
                content = fp.read()
        except IOError as e:
            print(e, file=sys.stderr)
        else:
            yield nick, content

if __name__ == '__main__':
    print([x[0] for x in load_datasets()])
