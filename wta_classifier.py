import enchant
from Dictionaries.dicts import dicts
from treetaggerwrapper import TreeTagger, make_tags
from nltk.stem.snowball import SpanishStemmer


class WTAclassifier(object):

    def __init__(self, stem=False, tag=False):
        dictionaries = dicts()
        self.english_dict = enchant.Dict("en_EN")
        self.spanish_dict = enchant.Dict("es_AR")
        self.ND = dictionaries.norm
        self.SD = dictionaries.lemario
        self.PND = dictionaries.names
        self.stem = stem
        self.tag = tag

        if stem:
            self.stemmer = SpanishStemmer()
        if tag:
            # path to TreeTagger installation directory
            path = 'here put path to TreeTagger'
            self.tagger = TreeTagger(TAGLANG='es', TAGDIR=path)

    def dictionary_lookup(self, word):
        result = (word in self.SD or
                  word in self.PND or
                  word in self.ND.values())
        return result

    def affix_check(self, word):
        result = False
        if word.islower() or word.istitle():
            if self.stem:
                stem = self.stemmer.stem(word)
                n = len(stem)
                # compare with first substring of length n of each word in SD
                for w in [x[:n] for x in self.SD if len(x) >= n]:
                    result = (stem == w)
                    if result:
                        break
            if self.tag:
                lemma = make_tags(self.tagger.tag_text(word))[0].lemma
                result = self.dictionary_lookup(lemma)
        return result

    def check(self, word):
        result = self.spanish_dict.check(word)
        if not result:
            result = self.dictionary_lookup(word) or self.affix_check(word)
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
