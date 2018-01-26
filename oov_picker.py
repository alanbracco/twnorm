import enchant
from collections import defaultdict
from nltk.tokenize import sent_tokenize
from tokenizer import MyTokenizer


def is_valid(word):

    if '@' in word and not word[0] == '@':
        word = word.replace('@', 'a')
    if '-' in word:
        for w in word.split('-'):
            if not w.isalnum() or word.isdigit():
                return False
        return True
    else:
        return (word.isalnum() and not word.isdigit())


class OOVpicker(object):

    def __init__(self, tweets):
        twt = MyTokenizer()
        known_word = enchant.Dict("es_AR")
        OOV = defaultdict(lambda: defaultdict(list))
        tokenized = defaultdict(dict)
        # split tweets by tweet separator
        for tweet_id, tweet_text in tweets.items():
            # separate tweet sentences
            sents = sent_tokenize(tweet_text, language='spanish')
            # tokenize each sentence
            tokenized_sents = [twt.tokenize(sent) for sent in sents]
            for j, sent in enumerate(tokenized_sents):
                # enumerate sent to know word's position
                e = enumerate(sent)
                # list of (word, pos) where word is alphanumeric and not digit
                wp_list = [(word, pos) for pos, word in e if is_valid(word)]
                tokenized[tweet_id][j] = wp_list
                for word, pos in wp_list:
                    # check if word is In Vocabulary
                    if not known_word.check(word):
                        # add (word, pos) to j-th sent
                        # of tweet with id = tweet_id
                        OOV[tweet_id][j].append((word, pos))
        n = len(OOV)
        print('Tweets to correct:', n)
        self.n = n
        self.tokenized = dict(tokenized)
        self.OOV = dict(OOV)
