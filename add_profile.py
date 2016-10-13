import sys
from models import does_nickname_exist, add_message

if len(sys.argv) < 2:
    print('usage: add_profile.py NICKNAME', file=sys.stderr)
    sys.exit(1)
nickname = sys.argv[1]

if does_nickname_exist(nickname):
    print('nickname {} already exists'.format(nickname))
    sys.exit(1)

for line in sys.stdin.readlines():
    add_message(nickname, line)
