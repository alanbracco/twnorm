import pickle
from nltk.data import load
from os import path


class Selector(object):

    def __init__(self):
        """
        model -- n-gram model.
        """
        modelpath = 'here put path to language model'
        # open model file
        file = open(modelpath, 'rb')
        # load model file
        model = pickle.load(file)

        self.model = model
        self.n = model.n

    def choose(self, prev_tokens, candidates):
        """
            return the most probable next token for prev_tokens
        """
        model = self.model
        cands = list(candidates)
        probs = [model.cond_prob(c, prev_tokens) for c in cands]
        max_prob = max(probs)
        index = probs.index(max_prob)
        winner = cands[index]

        return winner

    def prev_tokens(self, pair, tokenized):
        n = self.n
        index = tokenized.index(pair)
        prev_tokens = tuple()
        for i in range(index - n + 1, index):
            if i < 0:
                prev_tokens += ('<s>',)
            else:
                prev_tokens += (tokenized[i][0],)
        return prev_tokens
