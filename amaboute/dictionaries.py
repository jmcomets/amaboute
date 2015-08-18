import os
from textblob_custom import TextBlob

__all__ = ('load_datasets', 'DICTS',)

this_dir = os.path.dirname(os.path.realpath(__file__))

DICTS = 'Rousseau'
DATASETS = ('rousseau.txt',)

def load_datasets():
    for dataset in DATASETS:
        with open(os.path.join(this_dir, 'dicts', dataset), 'r') as fp:
            content = fp.read()
        yield dataset, TextBlob(content)
