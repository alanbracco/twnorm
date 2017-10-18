from os import path
from collections import defaultdict


class dicts(object):

    def __init__(self):

        filepath = path.split(path.abspath(__file__))[0] + '/txt/'

        # create normalization dict
        d = defaultdict(str)
        normfile = open(filepath + 'sms.txt', 'r')
        lines = normfile.read().split('\n')
        for use, correct in [line.split(':') for line in lines]:
            d[use] = correct
        normfile.close()
        self.norm = dict(d)

        # create set of spanish names
        namesfile = open(filepath + 'proper_nouns.txt', 'r')
        lines = namesfile.read().split('\n')
        self.names = {word for word in lines}

        # create set of spanish lemario
        lemfile = open(filepath + 'lemario.txt', 'r')
        lines = lemfile.read().split('\n')
        self.lemario = {word for word in lines}

        # add a set of all verbs (infinitive + conjugated) to lemario
        verbsfile = open(filepath + 'verbs.txt', 'r')
        lines = verbsfile.read().split('\n')
        self.lemario = self.lemario.union({word for word in lines})
