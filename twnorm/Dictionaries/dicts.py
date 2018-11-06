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
        lemario_tmp = defaultdict(set)
        for word in lines:
            lemario_tmp[word[0]].add(word)
        self.lemario = dict(lemario_tmp)

        # create set of argentine slang
        slangfile = open(os.path.join(resources_path, 'lunfardos.txt'), 'r')
        lines = slangfile.read().split('\n')
        slangfile.close()
        self.slang = {word for word in lines}

    def is_in_lemario(self, word):
        return word[0] in self.lemario.keys() and word in self.lemario[word[0]]

    def is_valid(self, word):
        result = (self.is_in_lemario(word) or
                  word in self.slang or
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
