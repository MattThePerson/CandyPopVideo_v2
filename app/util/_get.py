""" Functions for getting specific things from collection, eg. performers, studios, ... """



def getPerformers(videos_dict):
    d = {}
    for vid in videos_dict.values():
        for p in vid.get('performers', []):
            d[p] = d.get(p, 0) + 1
    if '' in d:
        del d['']
    return d


def getStudios(videos_dict):
    d = {}
    for vid in videos_dict.values():
        k = vid.get('studio')
        if k:
            d[k] = d.get(k, 0) + 1
    return d

