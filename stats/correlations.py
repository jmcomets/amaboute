import itertools as it

import numpy as np
from scipy.signal import medfilt

def compute_present_classes_by_timestamp(data_by_nickname):
    time_classes = None
    classes = {}

    for i, (nickname, timestamps) in enumerate(data_by_nickname.items()):
        classes[i] = nickname
        C = np.zeros(len(timestamps))
        C.fill(i)

        T = np.array(timestamps)

        # compute local derivatives
        DT = np.array([0] + list(map(lambda x: x[0] - x[1], zip(T[1:], T[:-1]))))
        # TODO: apply smoothing ?
        if np.max(DT) == 0:
            continue
        DT = (DT - np.min(DT)) / (np.max(DT) - np.min(DT))
        # FIXME: use average filter instead, there's probably many low ds
        P = np.vectorize(lambda x: x < 0.5, otypes=[np.bool])(medfilt(DT))

        F = np.column_stack((T, P, C))
        F = np.array(list(filter(lambda x: x[1], F)))
        F = np.delete(F, 1, 1)

        if time_classes is None:
            time_classes = F
        else:
            time_classes = np.vstack((time_classes, F))
    time_classes = sorted(time_classes, key=lambda x: x[0])
    time_classes = list(map(lambda tc: (tc[0], classes[tc[1]]), time_classes))
    return time_classes

def compute_presence_matrix(data_by_nickname, window_duration, as_probability=True):
    time_classes = compute_present_classes_by_timestamp(data_by_nickname)

    windows = []
    window, start_time = None, 0.

    for t, class_ in time_classes:
        if window is None:
            window, start_time = set([class_]), t
            continue

        duration = abs(t - start_time)
        if duration < window_duration:
            window.add(class_)
        else:
            windows.append(window)
            window, start_time = set([class_]), t

    classes = list(set(it.chain.from_iterable(windows)))
    presence_matrix = { c : { c : 0 for c in classes } for c in classes }

    for window in windows:
        for c1, c2 in it.product(window, window):
            if c1 == c2:
                continue

            presence_matrix[c1].setdefault(c2, 0)
            presence_matrix[c2].setdefault(c1, 0)
            presence_matrix[c1][c2] += 1
            presence_matrix[c2][c1] += 1

    if as_probability:
        for nickname, adjacencies in presence_matrix.items():
            total = sum(adjacencies.values())
            for other_nickname in adjacencies:
                adjacencies[other_nickname] /= total
    return presence_matrix, classes

if __name__ == '__main__':
    import sys
    import csv

    sys.path.append('.')
    from history import load_history, history_times

    if len(sys.argv) < 2:
        print('no file given', file=sys.stderr)
        sys.exit(1)

    source_filename = sys.argv[1]
    dest_filename = None

    if len(sys.argv) > 2:
        dest_filename = sys.argv[2]

    data = load_history(source_filename)

    # format data by nickname
    data_by_nickname = { n : list(history_times(tm)) for n, tm in data.items() }

    presence_matrix, classes = compute_presence_matrix(data_by_nickname, window_duration=1200)

    def write_presence_matrix(presence_matrix, fp):
        writer = csv.DictWriter(fp, sorted(classes))
        writer.writeheader()
        for nickname, adjacencies in sorted(presence_matrix.items(), key=lambda x: x[0]):
            writer.writerow(adjacencies)

    if dest_filename is not None:
        with open(dest_filename, 'w') as fp:
            write_presence_matrix(presence_matrix, fp)
    else:
        write_presence_matrix(presence_matrix, sys.stdout)
