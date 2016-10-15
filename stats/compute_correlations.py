import os
import datetime
import itertools as it
import numpy as np

from scipy.signal import medfilt

def load_from_csv(filename):
    import csv
    from dateutil.parser import parse as parse_date
    # print('loading from "%s"' % filename)
    with open(filename, 'r') as fp:
        data = list(csv.DictReader(fp))

    # print('formatting dates as timestamps')
    data_by_nickname = {}
    for d in data:
        nickname = d['nickname']
        data_by_nickname.setdefault(nickname, [])
        data_by_nickname[nickname].append(parse_date(d['time']).timestamp())
    return data_by_nickname

def save_as_json(filename):
    import json
    # print('saving to "%s"' % filename)
    with open(filename, 'w') as fp:
        json.dump(data_by_nickname, fp)

def load_from_json(filename):
    import json
    # print('loading from "%s"' % filename)
    with open(filename, 'r') as fp:
        return json.load(fp)

csv_filename = 'state-1472997957.csv'
json_filename = 'data-by-nickname.json'

if os.path.exists(json_filename):
    data_by_nickname = load_from_json(json_filename)
else:
    data_by_nickname = load_from_csv(csv_filename)
    save_as_json(json_filename)

# print('building matrix')

classes = {}

M = None

for i, (nickname, timestamps) in enumerate(data_by_nickname.items()):
    C = np.zeros(len(timestamps))
    C.fill(i)

    T = np.array(timestamps)
    D = np.array([0] + list(map(lambda x: x[0] - x[1], zip(T[1:], T[:-1]))))
    D = medfilt(D)

    if np.max(D) == 0:
        # print('ignoring: %s' % nickname)
        continue

    classes[i] = nickname

    D = (D - np.min(D)) / (np.max(D) - np.min(D))
    f = np.vectorize(lambda x: x < 0.5, otypes=[np.bool])
    D = f(D)

    F = np.column_stack((T, D, C))
    F = np.array(list(filter(lambda x: x[1], F)))
    F = np.delete(F, 1, 1)

    if M is None:
        M = F
    else:
        M = np.vstack((M, F))
M = list(map(list, list(M)))
M = sorted(M, key=lambda x: x[0])
# import pprint; pprint.pprint(M)
# raise SystemExit

window_duration = 300 # 5 minutes

windows = []
window, start_time = None, 0.

format_t = lambda t: datetime.datetime.fromtimestamp(t).strftime('%d/%m/%y %H:%M')

for t, class_ in M:
    # default case
    if window is None:
        window, start_time = set([class_]), t
        continue

    duration = abs(t - start_time)
    if duration < window_duration:
        window.add(class_)
    else:
        windows.append({
            'start': format_t(start_time),
            'end': format_t(t),
            'window': list(map(lambda c: classes[c], window))
            })
        window, start_time = set([class_]), t
# import pprint; pprint.pprint(windows)
# raise SystemExit

presence_matrix = { c : { c : 0 for c in classes.values() } for c in classes.values() }
for c in presence_matrix:
    del presence_matrix[c][c]

for window_info in windows:
    window = window_info['window']
    for c1, c2 in it.product(window, window):
        if c1 == c2:
            continue

        # presence_matrix.setdefault(c1, {})
        # presence_matrix.setdefault(c2, {})
        presence_matrix[c1].setdefault(c2, 0)
        presence_matrix[c2].setdefault(c1, 0)
        presence_matrix[c1][c2] += 1
        presence_matrix[c2][c1] += 1

for nickname, adjacencies in presence_matrix.items():
    total = sum(adjacencies.values())
    for other_nickname in adjacencies:
        adjacencies[other_nickname] /= total

import pprint; pprint.pprint(presence_matrix)

# import csv
# with open('test.csv', 'w') as fp:
#     writer = csv.DictWriter(fp, sorted(classes.values()))
#     writer.writeheader()
#     for nickname, adjacencies in sorted(presence_matrix.items(), key=lambda x: x[0]):
#         writer.writerow(adjacencies)
