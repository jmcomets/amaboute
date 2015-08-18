import os
import re
import time
import json
from matching import url_regex

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
    return filter_history(history)

history_times = lambda timed_messages: map(lambda tm: tm[0], timed_messages)
history_messages = lambda timed_messages: map(lambda tm: tm[1], timed_messages)

# private stuff

def filter_history(history):
    history = {nick: [(t, message) for t, message in timed_messages]
               for nick, timed_messages in history.items()}

    filter_smileys(history['etkadt'])

    filter_actions(history)
    #filter_mentions(history)
    filter_commands(history)

    #filter_nicks(history)
    filter_links(history)

    filter_characters(history)
    return history

def history_message_filter(f):
    def inner(history):
        for nick, timed_messages in history.items():
            for i, tm in enumerate(timed_messages):
                t, message = tm
                message = f(message)
                timed_messages[i] = t, message
    return inner

@history_message_filter
def filter_actions(message):
    message = message.replace('\u0001ACTION', '/me')
    message = message.replace('\u0001', '')
    return message

mention_regex = re.compile(r'^\w+:?')

@history_message_filter
def filter_mentions(message):
    return mention_regex.sub('MENTION', message)

characters_regex = re.compile(r'"|<|>|:|\^')

@history_message_filter
def filter_characters(message):
    return characters_regex.sub('', message)

smileys = (':)', '^^', '=)', ':-)',)

def filter_smileys(timed_messages):
    for i, tm in enumerate(timed_messages):
        t, message = tm
        for smiley in smileys:
            message = message.replace(smiley, '')
        timed_messages[i] = t, message

def filter_commands(history):
    for nick, timed_messages in history.items():
        history[nick] = [(t, message) for t, message in timed_messages
                         if not message.startswith('!')]

def filter_nicks(history):
    for nick, timed_messages in history.items():
        for i, tm in enumerate(timed_messages):
            t, message = tm
            for nick in history.keys():
                message = message.replace(nick, 'MENTION')
            timed_messages[i] = t, message

def filter_links(history):
    for nick, timed_messages in history.items():
        for i, tm in enumerate(timed_messages):
            t, message = tm
            message = url_regex.sub('LIEN', message)
            timed_messages[i] = t, message
