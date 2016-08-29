import sys
import json
import itertools as it

if len(sys.argv) < 2:
    print('no input file given', file=sys.stderr)
    sys.exit(1)
input_file = sys.argv[1]

if len(sys.argv) < 3:
    print('no output file given', file=sys.stderr)
    sys.exit(1)
output_file = sys.argv[2]

try:
    with open(input_file, 'r') as fp:
        history = json.load(fp)
except IOError:
    print('could not open file {}'.format(input_file), file=sys.argv)
    sys.exit(1)

same_names = (
        # source -> destination
        ('vic-x', 'victor-clement'),
        ('jeremy-eder', 'jeremy-edert'),
        )

for names in same_names:
    all_timed_messages = sorted(list(it.chain.from_iterable(map(lambda n: history.get(n, []), names))), key=lambda tm: tm[0])
    most_recent = lambda n: max(history.get(n, []), key=lambda tm: tm[0])[0]
    most_recent_name = max(map(lambda n: (n, most_recent(n)), names), key=lambda nt: nt[1])[0]
    for n in names:
        if n != most_recent_name:
            del history[n]
    history[most_recent_name] = all_timed_messages

with open(output_file, 'w') as fp:
    json.dump(history, fp)
