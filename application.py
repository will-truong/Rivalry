import requests
from collections import OrderedDict
from flask import Flask, jsonify


application = Flask(__name__)


def query_google_ac(product):
    """
    Determines a product's immediate rivals using
    Google Search Autocomplete API with "vs" syntax.
    """
    if product:
        base_query = "http://suggestqueries.google.com/" \
                     "complete/search?client=firefox&q={} vs "
        r = requests.request(
            'GET', base_query.format(product))

        return [r.json() and (product + " vs ") in x and
                (x.split(product + " vs ")[1]) for x in r.json()[1]]
    # bug where API performs autocorrection


def rank_rivals(product):
    """
    Ranks a product's immediate rivals by search frequency.
    """
    ranking = {}
    if product:
        top_hits = query_google_ac(product)
        for i in range(0, len(top_hits)):
            ranking[top_hits[i]] = len(top_hits) - i
    return ranking


def aggregate_rivalries(product):
    """
    Aggregates rivalries within a product's industry to
    generate an industry-wide ranking.
    """
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


@application.route('/')
def welcome():
    return 'Welcome to Rivalry.'


@application.route('/<product>')
def get_rivals(product):
    return jsonify(aggregate_rivalries(product))


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


if __name__ == "__main__":
    application.run()


"""
Copyright 2015-2016
Author: Will Truong
Student at The University of Texas at Austin
"""
