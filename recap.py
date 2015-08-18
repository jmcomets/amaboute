from matching import matches_hashtag, matches_share

def recap(history):
    most_active = max(history.items(), key=lambda it: len(it[1]))[0]
    most_hashtags = max(history.items(), key=lambda it: len(list(filter(lambda tm: matches_hashtag(tm[1]), it[1]))))[0]
    most_shares = max(history.items(), key=lambda it: len(list(filter(lambda tm: matches_share(tm[1]), it[1]))))[0]
    return dict(most_active=most_active, most_hashtags=most_hashtags, most_shares=most_shares)
