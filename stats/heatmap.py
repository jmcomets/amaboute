# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# ------------------------------------------------------------------------
# Filename   : heatmap.py
# Date       : 2013-04-19
# Updated    : 2014-01-04
# Author     : @LotzJoe >> Joe Lotz
# Description: My attempt at reproducing the FlowingData graphic in Python
# Source     : http://flowingdata.com/2010/01/21/how-to-make-a-heatmap-a-quick-and-easy-solution/
#
# Other Links:
#     http://stackoverflow.com/questions/14391959/heatmap-in-matplotlib-with-pcolor
#
# ------------------------------------------------------------------------

import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

try:
    if len(sys.argv) < 2:
        data = pd.read_csv(sys.stdin)
    else:
        with open(sys.argv[1], 'r') as fp:
            data = pd.read_csv(fp)
except pd.io.common.EmptyDataError:
    print('no csv given', file=sys.stderr)
    sys.exit(1)
except pd.io.common.CParserError:
    print('invalid csv given', file=sys.stderr)
    sys.exit(1)
labels = list(data.columns.values)

dest_filename = None
if len(sys.argv) > 2:
    dest_filename = sys.argv[2]

# Normalize data columns
data = (data - data.mean()) / (data.max() - data.min())

# Plot it out
fig, ax = plt.subplots()
heatmap = ax.pcolor(data, cmap=plt.cm.Blues, alpha=0.8)

# Format
fig = plt.gcf()
fig.set_size_inches(8, 11)

# turn off the frame
ax.set_frame_on(False)

# put the major ticks at the middle of each cell
ax.set_yticks(np.arange(data.shape[0]) + 0.5, minor=False)
ax.set_xticks(np.arange(data.shape[1]) + 0.5, minor=False)

# want a more natural, table-like display
ax.invert_yaxis()
ax.xaxis.tick_top()

# note I could have used data.columns but made "labels" instead
ax.set_xticklabels(labels, minor=False)
ax.set_yticklabels(labels, minor=False)

plt.xticks(rotation=90)

ax.grid(False)

# Turn off all the ticks
ax = plt.gca()

for t in ax.xaxis.get_major_ticks():
    t.tick1On = False
    t.tick2On = False
for t in ax.yaxis.get_major_ticks():
    t.tick1On = False
    t.tick2On = False

if dest_filename is not None:
    plt.savefig(dest_filename)
else:
    plt.show()
