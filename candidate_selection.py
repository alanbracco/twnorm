import os
import pickle


class Selector(object):

    def __init__(self, modelfile):
        """
        model -- n-gram model.
        """
        # path to model file
        filepath = os.path.join(os.getcwd(), 'Models', modelfile)
        # open model file
        file = open(filepath, 'rb')
        # load model file
        model = pickle.load(file)

        self.model = model
        self.n = model.n
        self.UNKNOWN_CORRECTION = '-'
        self.DEFAULT_CORRECTION = '-'

    def choose(self, prev_tokens, candidates):
        """
            return the most probable next token for prev_tokens
        """
        model = self.model
        cands = sorted(list(candidates))
        probs = [model.cond_prob(c, prev_tokens) for c in cands]
        max_prob = max(probs)
        index = probs.index(max_prob)
        winner = cands[index]

        return winner

    def prev_tokens(self, word, position, tokenized):
        n = self.n
        pair = (word, position)
        index = tokenized.index(pair)
        prev_tokens = tuple()
        for i in range(index - n + 1, index):
            if i < 0:
                prev_tokens += ('<s>',)
            else:
                prev_tokens += (tokenized[i][0],)
        return prev_tokens

    def select_candidate(self, word, position, tokens, candidates):
        if not candidates:
            return self.UNKNOWN_CORRECTION

        prev_tokens = self.prev_tokens(word, position, tokens)
        selected_candidate = self.choose(prev_tokens, candidates)
        return selected_candidate
