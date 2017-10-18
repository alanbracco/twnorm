import enchant
from collections import defaultdict
from nltk.tokenize import TweetTokenizer, sent_tokenize


class OOVpicker(object):

    def __init__(self, tweets):
        twt = TweetTokenizer()
        known_word = enchant.Dict("es_ES")
        OOV = defaultdict(lambda: defaultdict(list))
        tokenized = defaultdict(dict)
        # split tweets by tweet separator
        for tweet_id, tweet_text in tweets.items():
            # '318706266279145473'
            # separate tweet sentences
            sents = sent_tokenize(tweet_text)
            # tokenize each sentence
            tokenized_sents = [twt.tokenize(sent) for sent in sents]
            for j, sent in enumerate(tokenized_sents):
                # enumerate sent to know word's position
                e = enumerate(sent)
                # list of (word, pos) where word is alphanumeric and not digit
                wp_list = [(word, pos) for pos, word in e
                            if (word.isalnum() and not word.isdigit())]
                tokenized[tweet_id][j] = wp_list
                for word, pos in wp_list:
                    # check if word is In Vocabulary
                    if not known_word.check(word):
                        # add (word, pos) to j-th sent
                        # of tweet with id = tweet_id
                        OOV[tweet_id][j].append((word, pos))
        self.tokenized = dict(tokenized)
        self.OOV = dict(OOV)
