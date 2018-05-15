import enchant
from Dictionaries.dicts import Dicts
from lemmatizer import Lemmatizer


class WTAclassifier(object):

    def __init__(self, lemma=False):
        self.extra_dicts = Dicts()
        self.english_dict = enchant.Dict("en_EN")
        self.spanish_dict = enchant.Dict("es_AR")
        self.lemma = lemma
        if lemma:
            self.lemmatizer = Lemmatizer()

    def check(self, word):
        result = self.spanish_dict.check(word)
        if not result:
            result = self.extra_dicts.is_valid(word)
        if self.lemma and not result:
            lemma = self.lemmatizer.lemmatize(word)
            result = self.extra_dicts.is_valid(lemma)
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
