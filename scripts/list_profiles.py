import sys

sys.path.append('.')
from models import get_registered_profiles

registered_profiles = get_registered_profiles()
registered_profiles = sorted(registered_profiles, reverse=True,
                             key=lambda p: (len(p.messages), p.nickname))
format_profile = lambda p: '%s : %s messages' % (p.nickname, len(p.messages))
print('\n'.join(map(format_profile, registered_profiles)))
