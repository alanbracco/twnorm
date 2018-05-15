from treetaggerwrapper import TreeTagger, make_tags


class Lemmatizer(object):

    def __init__(self):
        # path to TreeTagger installation directory
        path = 'here put path to TreeTagger'
        self.lemmatizer = TreeTagger(TAGLANG='es', TAGDIR=path)

    def lemmatize(self, word):
        tagged_word = self.lemmatizer.tag_text(word)
        tag_obj = make_tags(tagged_word)[0]
        lemma = tag_obj.lemma
        return lemma
