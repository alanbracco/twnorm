# https://docs.python.org/3/library/collections.html
from collections import defaultdict
from math import log
from random import random


def ngram_delim(n, sent):
    """Add delimiters at the beginning and at the end of the sentence.
    n -- order of the model.
    sent -- one sentence (a list of tokens).
    """
    sent = ['<s>']*(n-1) + sent + ['</s>']
    return sent


def log2(x):
    """Calculate log (base 2) of x.
    """
    if x <= 0:
        result = float('-inf')
    else:
        result = log(x, 2)

    return result


class NGram(object):

    def __init__(self, n, sents):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        """
        assert n > 0
        self.n = n
        self.counts = counts = defaultdict(int)
        # add delimiters to each sentence and build n-grams
        for sent in sents:
            sent = ngram_delim(n, sent)
            for i in range(len(sent) - n + 1):
                ngram = tuple(sent[i: i + n])
                counts[ngram] += 1
                counts[ngram[:-1]] += 1

    def count(self, tokens):
        """Count for an n-gram or (n-1)-gram.
        tokens -- the n-gram or (n-1)-gram tuple.
        """
        return self.counts[tokens]

    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.
        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        n = self.n
        if not prev_tokens:
            prev_tokens = []
        assert len(prev_tokens) == n - 1    # check n-gram size

        tokens = prev_tokens + [token]

        p1 = self.counts[tuple(tokens)]    # appearances of (prev_tokens,token)
        p2 = self.counts[tuple(prev_tokens)]    # appearances of prev_tokens

        prob = 0

        if p2 != 0:
            # calculate probability P(token | prev_tokens) using counts.
            prob = float(p1)/p2

        return prob

    def sent_prob(self, sent):
        """Probability of a sentence. Warning: subject to underflow problems.
        sent -- the sentence as a list of tokens.
        """
        n = self.n
        prob = 1
        sent = ngram_delim(n, sent)
        # for each n-gram of the sentece,
        # calculate the conditional probability using Markov Assumption.
        for i in range(n-1, len(sent)):
            prev_tokens = sent[i-n+1:i]
            token = sent[i]
            prob *= self.cond_prob(token, prev_tokens)

        return prob

    def sent_log_prob(self, sent):
        """Log-probability of a sentence.
        sent -- the sentence as a list of tokens.
        """
        n = self.n
        prob = 0
        sent = ngram_delim(n, sent)
        # calculate log(base 2) of conditional probability
        # of each n-gram related to the sentence.
        for i in range(n-1, len(sent)):
            prev_tokens = sent[i-n+1:i]
            token = sent[i]
            prob_temp = self.cond_prob(token, prev_tokens)
            if prob_temp == 0:
                prob = float('-inf')
            else:
                # calculate log base 2.
                # Domain error is not a problem (because 'if statement').
                prob += log2(prob_temp)

        return prob

    def log_probability(self, sents):
        """Log-probability of sentences.
        sents -- list of sentences, each one being a list of tokens.
        """
        log_prob = sum(self.sent_log_prob(sent) for sent in sents)

        return log_prob

    def cross_entropy(self, sents):
        """Cross-entropy of sentences.
        sents -- list of sentences, each one being a list of tokens.
        """
        M = sum([len(sent) for sent in sents])
        log_probability = self.log_probability(sents)

        cross_entropy = log_probability / float(M)

        return cross_entropy

    def perplexity(self, sents):
        """Perplexity of sentences.
        sents -- list of sentences, each one being a list of tokens.
        """
        l = self.cross_entropy(sents)

        perplexity = 2**(-l)

        return perplexity


class NGramGenerator:

    def __init__(self, model):
        """
        model -- n-gram model.
        """

        # create structures
        self.probs = probs = defaultdict(dict)
        self.sorted_probs = sorted_probs = defaultdict(dict)
        self.n = n = model.n
        counts = model.counts
        # initialize structures
        for words in counts.keys():
            if len(words) == n:
                token = words[n-1]
                prev_tokens = words[:n-1]
                if prev_tokens not in probs:
                    probs.update({prev_tokens: defaultdict(dict)})
                    sorted_probs.update({prev_tokens: []})
                current_prob = model.cond_prob(token, list(prev_tokens))
                probs[prev_tokens].update({token: current_prob})
                sorted_probs[prev_tokens].append((token, current_prob))
                sorted_probs[prev_tokens] = sorted(sorted_probs[prev_tokens],
                                                   key=lambda x: (-x[1], x[0]))

    def generate_sent(self):
        """Randomly generate a sentence."""
        n = self.n

        sent = prev_tokens = ['<s>'] * (n-1)    # add initial delimiters
        end_delim = '</s>'
        new_token = ''

        # while not end of sentence, generate a new token
        while new_token != end_delim:
            new_token = self.generate_token(tuple(prev_tokens))
            sent.append(new_token)
            prev_tokens = tuple(sent[len(sent)-n+1:])

        return sent[n-1:len(sent)-1]

    def generate_token(self, prev_tokens=None):
        """Randomly generate a token, given prev_tokens.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        if not prev_tokens:
            prev_tokens = ()

        tokens = self.sorted_probs[prev_tokens]
        prob = 0
        X = random()
        gen_token = ''
        i = 0

        # choose token using inverse transform sampling
        while prob < X:
            gen_token, prob_token = tokens[i]
            prob += prob_token
            i += 1

        return gen_token


class AddOneNGram(NGram):

    def __init__(self, n, sents):

        super().__init__(n, sents)

        word_types = set(word for sent in sents for word in sent)
        # add 1 because of "end of sentece"('</s>') delimiter.
        self.vocabulary_size = len(word_types) + 1

    def V(self):
        """Size of the vocabulary.
        """
        return self.vocabulary_size

    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.
        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        n = self.n
        if not prev_tokens:
            prev_tokens = []
        assert len(prev_tokens) == n - 1    # check n-gram size

        tokens = prev_tokens + [token]
        # appearances of (prev_tokens,tokens), plus one (addOne).
        p1 = float(self.counts[tuple(tokens)]) + 1
        # appearances of prev_tokens plus vocabulary size.
        p2 = self.counts[tuple(prev_tokens)] + self.V()

        prob = 0

        if p2 != 0:
            # calculate probability
            # (c(prev_token,token) + 1) / (c(prev_token) + V)
            prob = float(p1)/p2

        return prob


class InterpolatedNGram(NGram):

    def __init__(self, n, sents, gamma=None, addone=True):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        gamma -- interpolation hyper-parameter (if not given, estimate using
            held-out data).
        addone -- whether to use addone smoothing (default: True).
        """
        self.n = n
        self.gamma = gamma
        self.models = models = []

        if gamma:
            train_sents = sents
        else:
            train_sents = sents[:int(0.9*len(sents))]

        if addone:
            models.append(AddOneNGram(1, train_sents))
        else:
            models.append(NGram(1, train_sents))

        for i in range(2, n+1):
            models.append(NGram(i, train_sents))

        if not gamma:
            held_out = sents[int(0.9*len(sents)):]
            gamma = self.calculate_gamma(held_out)

    def count(self, tokens):
        n = len(tokens)
        if n == 0:
            n = 1
        return self.models[n-1].counts[tokens]

    def calculate_gamma(self, held_out):
        max_log_prob = float('-inf')
        for i in range(200, 600, 50):
            self.gamma = float(i)
            log_prob = self.log_probability(held_out)
            if max_log_prob < log_prob:
                max_log_prob = log_prob
                k = i

        self.gamma = k

    def lambdas(self, tokens, lambda_list):

        tokens = tuple(tokens)
        count = self.count(tokens)
        lambd = (1-sum(lambda_list))

        if tokens:
            lambd *= (count/(count+self.gamma))
        return lambd

    def cond_prob(self, token, prev_tokens=None):

        n = self.n
        models = self.models

        if not prev_tokens:
            prev_tokens = []
        assert len(prev_tokens) == n - 1    # check n-gram size

        lambda_list = []
        prob = 0.0
        qMLprob = 0.0

        for i in range(n):
            lambd = self.lambdas(prev_tokens, lambda_list)
            lambda_list.append(lambd)
            qMLprob = models[n-1-i].cond_prob(token, prev_tokens)
            prob += lambda_list[i] * qMLprob
            prev_tokens = prev_tokens[1:]

        return prob


class BackOffNGram(NGram):

    def __init__(self, n, sents, beta=None, addone=True):
        """
        Back-off NGram model with discounting as described by Michael Collins.

        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.

        beta -- discounting hyper-parameter (if not given, estimate using
            held-out data).
        addone -- whether to use addone smoothing (default: True).
        """
        self.n = n
        self.beta = beta
        self.models = models = []
        self._A = A = defaultdict(set)
        self.addone = addone
        self.V = float(len(set(word for sent in sents for word in sent)) + 1)

        if beta is None:
            train_sents = sents[:int(0.9*len(sents))]
        else:
            train_sents = sents
        for i in range(1, n+1):
            models.append(NGram(i, train_sents))
        for model in models[1:]:
            n_model = model.n
            for ngram, val in model.counts.items():
                if len(ngram) == n_model:
                    nm1gram = ngram[:-1]
                    A[nm1gram].add(ngram[-1])

        if beta is None:
            held_out = sents[int(0.9*len(sents)):]
            beta = self.calculate_beta(held_out)
        else:
            self._alpha = self.calculate_alpha()
            self._denom = self.calculate_denom()

    def count(self, tokens):
        n = len(tokens)

        if tokens == n*('<s>',):
            n += 1
        count = self.models[n-1].counts[tokens]

        return count

    def cond_prob(self, token, prev_tokens=None):

        prob = 0.0

        if not prev_tokens:
            c = self.count(tuple([token]))
            cc = float(self.count(()))

            if self.addone:
                prob = (c + 1) / (cc + self.V)
            else:
                prob = c / cc

        else:
            if token in self.A(tuple(prev_tokens)):
                tokens = tuple(prev_tokens) + tuple([token])
                c_disc = self.count(tokens) - self.beta
                c = self.count(tuple(prev_tokens))
                prob = c_disc/float(c)
            else:
                alpha = self.alpha(tuple(prev_tokens))
                prob_tmp = self.cond_prob(token, prev_tokens[1:])
                denom = self.denom(tuple(prev_tokens))
                if prob_tmp != 0 and denom != 0:
                    prob = alpha*(prob_tmp/denom)

        return prob

    def calculate_alpha(self):

        _alpha = defaultdict(float)

        for ngram, val in self._A.items():
            sumat = 0
            for x in val:
                c_disc = self.count(ngram + tuple([x])) - self.beta
                c = self.count(ngram)
                sumat += c_disc/c
            _alpha[ngram] = 1.0-sumat

        return _alpha

    def calculate_denom(self):

        _denom = defaultdict(float)

        for ngram, val in self._A.items():
            sumat = 0
            for x in val:
                sumat += self.cond_prob(x, ngram[1:])

            _denom[ngram] = 1.0-sumat

        return _denom

    def calculate_beta(self, held_out):
        max_log_prob = float('-inf')
        for j in [i*0.1 for i in range(10)]:
            self.beta = float(j)
            self._alpha = self.calculate_alpha()
            self._denom = self.calculate_denom()
            log_prob = self.log_probability(held_out)
            if max_log_prob < log_prob:
                max_log_prob = log_prob
                k = j

        self.beta = k
        self._alpha = self.calculate_alpha()
        self._denom = self.calculate_denom()

    def A(self, tokens):
        """Set of words with counts > 0 for a k-gram with 0 < k < n.

        tokens -- the k-gram tuple.
        """
        return self._A.get(tokens, set())

    def alpha(self, tokens):
        """Missing probability mass for a k-gram with 0 < k < n.

        tokens -- the k-gram tuple.
        """
        return self._alpha.get(tokens, 1.0)

    def denom(self, tokens):
        """Normalization factor for a k-gram with 0 < k < n.

        tokens -- the k-gram tuple.
        """
        return self._denom.get(tokens, 1.0)
