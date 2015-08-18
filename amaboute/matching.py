import re

hashtag_regex = re.compile(r'^#\w+')

url_regex = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")

def matches_share(text):
    matches = url_regex.findall(text)
    return bool(matches)

def matches_hashtag(text):
    matches = hashtag_regex.findall(text)
    return bool(matches)
