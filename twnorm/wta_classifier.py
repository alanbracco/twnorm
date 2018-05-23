import spacy
import enchant
from twnorm.Dictionaries.dicts import Dicts


class Lemmatizer(object):

    def __init__(self):
        self.lemmatizer = spacy.load("es")

    def lemmatize(self, word):
        lemma = self.lemmatizer(word)[0].lemma_
        return lemma


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
            # Tokens like 'x' or 'q' appear in english dict and return True
            result = self.english_dict.check(word)
        return result

    def classify(self, word):
        if self.check(word):
            result = 1  # Correct word in spanish
        elif self.check_NoES(word):
            result = 2  # Correct word in another language
        else:
            result = 0  # Variant word (to correct)
        return result

    def is_variant(self, class_number):
        return class_number == 0

    def is_correct(self, class_number):
        return class_number == 1

    def is_not_spanish(self, class_number):
        return class_number == 2
