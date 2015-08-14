import re

_simple_quote_regex = re.compile(r"'([^']*)'")
_double_quote_regex = re.compile(r'"([^"]*)"')
_http_regex = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")

url_regex = _http_regex

def matches_quote(text):
    regexes = (_http_regex,)
    return any(map(lambda r: r.findall(text), regexes))
