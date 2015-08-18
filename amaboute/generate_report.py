#!/usr/bin/env python3

import re
import statistics
import itertools
from textblob_custom import TextBlob
from history import load_latest_history, history_times, history_messages
from matching import matches_share, matches_hashtag, url_regex

flatten = itertools.chain.from_iterable
pairs = lambda ls: zip(ls[::2], ls[1::2])

_history = None
def load_latest_history_lazily():
    global _history
    if _history is None:
        _history = load_latest_history()
    return _history

def using_history(f):
    def inner(*args):
        history = load_latest_history_lazily()
        return f(history, *args)
    return inner

@using_history
def nicks_by_positivity(history):
    nicks = history.keys()

    polarities = {}
    for nick, timed_messages in history.items():
        messages = map(lambda i: i[1], timed_messages)
        messages = map(lambda msg: url_regex.sub('', msg), messages)
        #messages = map(lambda msg: msg.lower(), messages)
        messages = list(messages)
        blobs = map(TextBlob, messages)
        polarity = sum(map(lambda blob: blob.polarity, blobs))
        polarities[nick] = polarity

    nicks_polarized = polarities.items()
    min_pol, max_pol = min(polarities.values()), max(polarities.values())
    nicks_polarized = map(lambda np: (np[0], (np[1] - min_pol) / (max_pol - min_pol)), nicks_polarized)
    nicks_polarized = sorted(nicks_polarized, key=lambda i: i[1], reverse=True)
    return nicks_polarized

@using_history
def nicks_by_activity(history):
    activities = {}
    for nick, timed_messages in history.items():
        times = list(history_times(timed_messages))
        #time_diffs = list(map(lambda x: x[1] - x[0], pairs(times)))
        #activities[nick] = sum(time_diffs) / len(time_diffs)
        if len(times) > 1:
            activities[nick] = statistics.stdev(times)

    min_, max_ = min(activities.values()), max(activities.values())
    activities = activities.items()
    #activities = map(lambda na: (na[0], (na[1] - min_) / (max_ - min_)), activities)
    activities = sorted(activities, key=lambda i: i[1], reverse=True)
    return activities

stupidity_words = ('ouais', 'bah', 'ah', 'ok',)

@using_history
def nicks_by_stupidity(history):
    stupidities = {}
    for nick, timed_messages in history.items():
        messages = history_messages(timed_messages)
        stupidities[nick] = sum(flatten(((message.count(word) for word in stupidity_words)
                      for message in messages)))
    min_, max_ = min(stupidities.values()), max(stupidities.values())
    stupidities = stupidities.items()
    stupidities = map(lambda ns: (ns[0], (ns[1] - min_) / (max_ - min_)), stupidities)
    stupidities = sorted(stupidities, key=lambda i: i[1], reverse=True)
    return stupidities

@using_history
def hashtag_count(history):
    counts = map(lambda i: (i[0], sum(map(matches_hashtag, history_messages(i[1])))), history.items())
    counts = sorted(counts, key=lambda i: i[1], reverse=True)
    counts = filter(lambda c: c[1], counts)
    return counts

def message(*args):
    print('!message', *args)

if __name__ == '__main__':
    message('Positivité:')
    for nick, positivity in nicks_by_positivity():
        message(nick, positivity)

    message('')
    message('Hashtags:')
    for nick, count in hashtag_count():
        message(nick, count)

    message('')
    message('Activity:')
    for nick, activity in nicks_by_activity():
        message(nick, activity)

    message('')
    message('Stupidity:')
    for nick, stupidity in nicks_by_stupidity():
        message(nick, stupidity)
