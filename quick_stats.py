import sys
import json

if len(sys.argv) < 2:
    print('no file given', file=sys.stderr)
    sys.exit(1)
history_file = sys.argv[1]

try:
    with open(history_file, 'r') as fp:
        history = json.load(fp)
except IOError:
    print('could not open file {}'.format(history_file), file=sys.argv)
    sys.exit(1)

for nick, messages in history.items():
    print('{} {}'.format(nick, len(messages)))
