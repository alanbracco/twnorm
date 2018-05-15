import os
from collections import defaultdict


class Dicts(object):

    def __init__(self):

        filepath = os.path.join(os.getcwd(), 'Dictionaries', 'Resources')

        # create normalization dict
        d = defaultdict(str)
        normfile = open(os.path.join(filepath, 'sms.txt'), 'r')
        lines = normfile.read().split('\n')
        for use, correct in [line.split(':') for line in lines]:
            d[use] = correct
        normfile.close()
        self.norm = dict(d)

        # create set of spanish names
        namesfile = open(os.path.join(filepath, 'proper_nouns.txt'), 'r')
        lines = namesfile.read().split('\n')
        namesfile.close()
        self.names = {word for word in lines}

        # create set of spanish lemario
        lemfile = open(os.path.join(filepath, 'lemario.txt'), 'r')
        lines = lemfile.read().split('\n')
        lemfile.close()
        self.lemario = {word for word in lines}

        # create set of argentine slang
        slangfile = open(os.path.join(filepath, 'lunfardos.txt'), 'r')
        lines = slangfile.read().split('\n')
        slangfile.close()
        self.slang = {word for word in lines}

        # add a set of all verbs (infinitive + conjugated) to lemario
        verbsfile = open(os.path.join(filepath, 'verbs.txt'), 'r')
        lines = verbsfile.read().split('\n')
        verbsfile.close()
        self.lemario = self.lemario.union({word for word in lines})

    def is_valid(self, word):
        result = (word in self.lemario or
                  word in self.names or
                  word in self.norm.values())
        return result

    def is_social_term(self, word):
        return word in self.norm.keys()

    def fix_social_term(self, word):
        result = word
        if self.is_social_term(word):
            result = self.norm[word]
        return result
