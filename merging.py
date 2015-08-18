from history import load_history, list_available_histories

def merge_all_histories():
    available_histories = list_available_histories()
    return merge_histories(available_histories)

def merge_histories(histories):
    full_history = {}
    for filename, history in zip(histories, map(load_history, histories)):
        for nick, timed_messages in history.items():
            full_history.setdefault(nick, set())
            for tm in timed_messages:
                full_history[nick].add(tm)
    return dict(map(lambda x: (x[0], list(sorted(x[1], key=lambda tm: tm[0]))),
                    full_history.items()))

if __name__ == '__main__':
    import os
    import sys
    from history import save_history

    this_dir = os.path.dirname(os.path.realpath(__file__))

    try:
        full_history = merge_all_histories()
        filename = save_history(full_history, base_dir=this_dir)
    except IOError as e:
        print('history not saved: {}'.format(str(e)))
        sys.exit(1)
    else:
        print('saved: {}'.format(filename))
