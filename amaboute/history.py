import os
import re
import time
import json
from quoting import url_regex

__all__ = ('save_report', 'load_latest_report', 'load_latest_history',
           'history_times', 'history_messages',)

this_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(this_dir, 'data')

def save_report(report, base_dir=data_dir):
    filename = 'state-{}.json'.format(int(time.time()))
    with open(os.path.join(base_dir, filename), 'w') as fp:
        json.dump(report, fp)

def list_available_reports(base_dir):
    filenames = os.listdir(base_dir)
    filenames = filter(lambda s: s.startswith('state-') and s.endswith('.json'), filenames)
    filenames = map(lambda f: os.path.join(base_dir, f), filenames)
    return filenames

def load_latest_report(base_dir=data_dir):
    filenames = list_available_reports(base_dir)
    if not filenames:
        raise IOError('no report available')

    filename = sorted(filenames)[-1]

    with open(filename, 'r') as fp:
        report = json.load(fp)
    filter_history(report['history'])
    return report

# history

def load_latest_history():
    report = load_latest_report(data_dir)
    return report['history']

history_times = lambda timed_messages: map(lambda tm: tm[0], timed_messages)
history_messages = lambda timed_messages: map(lambda tm: tm[1], timed_messages)

# private stuff

def filter_history(history):
    filter_smileys(history['etkadt'])

    filter_actions(history)
    #filter_mentions(history)
    filter_commands(history)

    #filter_nicks(history)
    filter_links(history)

    filter_characters(history)

def history_message_filter(f):
    def inner(history):
        for nick, timed_messages in history.items():
            for i, tm in enumerate(timed_messages):
                t, message = tm
                message = f(message)
                timed_messages[i] = i, message
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
        timed_messages[i] = i, message

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
