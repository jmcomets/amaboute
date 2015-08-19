import os

__all__ = ('load_datasets',)

this_dir = os.path.dirname(os.path.realpath(__file__))

DATASETS = {
        'Rousseau': 'rousseau.txt',
        }

def load_datasets():
    for nick, dataset in DATASETS.items():
        with open(os.path.join(this_dir, 'dicts', dataset), 'r') as fp:
            content = fp.read()
        yield nick, content
