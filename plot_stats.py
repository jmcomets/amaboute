import sys
import json
import datetime
import random
import itertools as it
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import colors

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

# for nick, messages in sorted(history.items(), key=lambda x: len(x[1]), reverse=True):
#     print('{} {}'.format(nick, len(messages)))

fig, ax = plt.subplots()

#import pprint; pprint.pprint(plt.style.available)
plt.style.use('ggplot')

# cleanup the axes
ax.spines["top"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)

# set the limits
min_time = min(map(lambda tm: tm[0], it.chain.from_iterable(history.values())))
max_time = max(map(lambda tm: tm[0], it.chain.from_iterable(history.values())))
min_date, max_date = map(datetime.datetime.fromtimestamp, (min_time, max_time))
ax.set_xlim(min_date, max_date)

# format the ticks
# ax.xaxis.set_major_locator(mdates.MonthLocator())
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%m'))
# ax.xaxis.set_minor_locator(mdates.DayLocator())

available_colors = [name for name in colors.cnames if 'dark' in name]
random.shuffle(available_colors)
colors_picked = available_colors[:len(history)]
nick_colors = dict(zip(history, colors_picked))

for nick, timed_messages in history.items():
    if len(timed_messages) < 30:
        continue
    dates = np.array(list(map(lambda tm: datetime.datetime.fromtimestamp(tm[0]), timed_messages)))
    nb_messages = np.arange(1, len(timed_messages) + 1)
    ax.plot_date(dates, nb_messages, nick_colors.get(nick, '-'), label=nick)

ax.get_xaxis().tick_bottom()
ax.get_yaxis().tick_left()
plt.xticks(fontsize=14)
plt.yticks(range(0, 4001, 500), fontsize=14)

# legend
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
#ax.grid(True)

plt.xlabel("Date", fontsize=16)
plt.ylabel("Messages sent", fontsize=16)

ax.legend(loc='center right', bbox_to_anchor=(1.4, 0.5),
        ncol=1, fancybox=True, shadow=True)

# rotates and right aligns the x labels, and moves the bottom of the
# axes up to make room for them
fig.autofmt_xdate()

plt.show()
#plt.savefig("graph.png", bbox_inches="tight");
