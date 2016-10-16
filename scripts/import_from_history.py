import sys
import json

sys.path.append('.')
from models import add_message

if len(sys.argv) < 2:
    print('no file given', file=sys.stderr)
    sys.exit(1)
history_file = sys.argv[1]

with open(history_file, 'r') as fp:
    history = json.load(fp)

for nickname, timed_messages in history.items():
    print('adding %s messages for %s' % (len(timed_messages), nickname))
    for time, message in timed_messages:
        add_message(nickname, message, time)
