import sys

sys.path.append('.')
from models import merge_profiles

if len(sys.argv) < 2:
    print('usage: merge_profiles.py NICKNAME [NICKNAMES_TO_MERGE...]', file=sys.stderr)
    sys.exit(1)

nickname = sys.argv[1]
other_nicknames = sys.argv[2:]

for other_nickname in other_nicknames:
    merge_profiles(nickname, other_nickname)
