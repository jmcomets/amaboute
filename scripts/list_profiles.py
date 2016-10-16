import sys

sys.path.append('.')
from models import get_registered_profiles_and_message_count

registered_profiles = get_registered_profiles_and_message_count()
registered_profiles = sorted(registered_profiles, reverse=True, key=lambda x: x[1])
format_profile = lambda x: '%s : %s messages' % (x[0], x[1])
print('\n'.join(map(format_profile, registered_profiles)))
