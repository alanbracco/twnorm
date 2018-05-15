import enchant
from Dictionaries.dicts import dicts
from lemmatizer import Lemmatizer


class WTAclassifier(object):

    def __init__(self, lemma=False):
        dictionaries = dicts()
        self.english_dict = enchant.Dict("en_EN")
        self.spanish_dict = enchant.Dict("es_AR")
        self.ND = dictionaries.norm
        self.SD = dictionaries.lemario
        self.PND = dictionaries.names
        self.lemma = lemma
        if lemma:
            self.lemmatizer = Lemmatizer()

    def dictionary_lookup(self, word):
        result = (word in self.SD or
                  word in self.PND or
                  word in self.ND.values())
        return result

    def check(self, word):
        result = self.spanish_dict.check(word)
        if not result:
            result = self.dictionary_lookup(word)
        if not result and self.lemma:
            lemma = self.lemmatizer.lemmatize(word)
            result = self.dictionary_lookup(lemma)
        return result

    def check_NoES(self, word):
        result = False
        if len(word) > 1:
            result = self.english_dict.check(word)
        return result

    def classify(self, word):
        if self.check(word):
            result = 1
        elif self.check_NoES(word):
            result = 2
        else:
            result = 0
        return result
