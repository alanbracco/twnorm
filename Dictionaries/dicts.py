import os
from collections import defaultdict


class Dicts(object):

    def __init__(self):

        abs_current_path = os.path.dirname(os.path.abspath(__file__))
        resources_path = os.path.join(abs_current_path, 'Resources')

        # create normalization dict
        d = defaultdict(str)
        normfile = open(os.path.join(resources_path, 'sms.txt'), 'r')
        lines = normfile.read().split('\n')
        for use, correct in [line.split(':') for line in lines]:
            d[use] = correct
        normfile.close()
        self.norm = dict(d)

        # create set of spanish names
        namesfile = open(os.path.join(resources_path, 'proper_nouns.txt'), 'r')
        lines = namesfile.read().split('\n')
        namesfile.close()
        self.names = {word for word in lines}

        # create set of spanish lemario
        lemfile = open(os.path.join(resources_path, 'lemario.txt'), 'r')
        lines = lemfile.read().split('\n')
        lemfile.close()
        self.lemario = {word for word in lines}

        # create set of argentine slang
        slangfile = open(os.path.join(resources_path, 'lunfardos.txt'), 'r')
        lines = slangfile.read().split('\n')
        slangfile.close()
        self.slang = {word for word in lines}

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
