import os
import re
import time
import json

__all__ = ('save_history', 'load_latest_history',
           'history_times', 'history_messages',)

this_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(this_dir, 'data')

def save_history(history, base_dir=data_dir):
    filename = 'state-{}.json'.format(int(time.time()))
    with open(os.path.join(base_dir, filename), 'w') as fp:
        json.dump(history, fp)
    return filename

def list_available_histories(base_dir=data_dir):
    filenames = os.listdir(base_dir)
    filenames = filter(lambda s: s.startswith('state-') and s.endswith('.json'), filenames)
    filenames = map(lambda f: os.path.join(base_dir, f), filenames)
    filenames = list(filenames)
    return filenames

def load_latest_history(base_dir=data_dir):
    filenames = list_available_histories(base_dir)
    if not filenames:
        raise IOError('no history available')

    filename = sorted(filenames)[-1]
    return load_history(filename)

def load_history(filename):
    with open(filename, 'r') as fp:
        history = json.load(fp)

    # filter history
    for nick, timed_messages in history.items():
        for i, tm in enumerate(timed_messages):
            t, message = tm
            message = filter_message(message)
            timed_messages[i] = t, message
    return history

history_times = lambda timed_messages: map(lambda tm: tm[0], timed_messages)
history_messages = lambda timed_messages: map(lambda tm: tm[1], timed_messages)

url_regex = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")

def filter_message(message):
    # actions
    message = message.replace('\u0001ACTION', '[action]')
    message = message.replace('\u0001', '')

    # links
    message = url_regex.sub('[lien]', message)

    return message
