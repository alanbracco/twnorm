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
        self.VARIANT_CLASS  = 0
        self.SPANISH_CLASS  = 1
        self.FOREIGN_CLASS  = 2
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
            result = self.SPANISH_CLASS  # Correct word in spanish
        elif self.check_NoES(word):
            result = self.FOREIGN_CLASS  # Correct word in another language
        else:
            result = self.VARIANT_CLASS  # Variant word (to correct)
        return result

    def is_variant(self, class_number):
        return class_number == self.VARIANT_CLASS

    def is_correct(self, class_number):
        return class_number == self.SPANISH_CLASS

    def is_not_spanish(self, class_number):
        return class_number == self.FOREIGN_CLASS


class BaselineClassifier(object):
    def __init__(self):
        self.spanish_dict = enchant.Dict("es_AR")
        self.VARIANT_CLASS  = 0
        self.SPANISH_CLASS  = 1

    def classify(self, word):
        return int(self.spanish_dict.check(word))

    def is_variant(self, class_number):
        return class_number == self.VARIANT_CLASS

    def is_correct(self, class_number):
        return class_number == self.SPANISH_CLASS
