import requests
from collections import OrderedDict


def query_google_ac(product):
    if product:
        base_query = "http://suggestqueries.google.com/" \
                     "complete/search?client=firefox&q={} vs "
        r = requests.request(
            'GET', base_query.format(product))

        return [r.json() and (product + " vs ") in x and
                (x.split(product + " vs ")[1]) for x in r.json()[1]]
    # bug where API performs autocorrection


def rank_rivals(product):
    ranking = {}
    if product:
        top_hits = query_google_ac(product)
        for i in range(0, len(top_hits)):
            ranking[top_hits[i]] = len(top_hits) - i
    return ranking


def aggregate_rivalries(product):  # Several ways to do this, need to try them
    rivals = set(query_google_ac(product))
    for rival in rivals.copy():
        if rival:
            immediate_rivals = set(query_google_ac(rival))
            if False not in immediate_rivals:
                rivals.update(immediate_rivals)

    ranking = {}
    for rival in rivals:
        immediate_rivals = rank_rivals(rival)
        for immediate_rival in immediate_rivals:
            if immediate_rival and immediate_rival in ranking:
                ranking[immediate_rival] += immediate_rivals[immediate_rival]
            else:
                ranking[immediate_rival] = immediate_rivals[immediate_rival]
    ordered_ranking = OrderedDict(
        sorted(ranking.items(), key=lambda t: t[1], reverse=True))
    return list(ordered_ranking)[0:10]

while(True):
    product = str(input("Enter the name of a product, brand, item, "
                        "or otherwise distinct entity: "))
    for a, b in enumerate(aggregate_rivalries(product), 1):
        print('{}. {}'.format(a, b))


# Author: William Truong
# Student at The University of Texas at Austin
