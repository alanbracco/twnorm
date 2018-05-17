import os
import enchant
from tokenizer import MyTokenizer
from collections import defaultdict
from nltk.tokenize import sent_tokenize
from wta_classifier import WTAclassifier


def is_valid(word):

    if '@' in word and not word[0] == '@':
        word = word.replace('@', 'a')
    if '-' in word:
        for w in word.split('-'):
            if not w.isalnum() or word.isdigit():
                return False
        return True
    if '.' in word:
        for w in word.split('.'):
            if not w.isalnum() or word.isdigit():
                return False
        return True

    else:
        return (word.isalnum() and not word.isdigit())


class Splitter(object):
    def __init__(self, tweets_file, verbose=False):
        filepath = os.path.join(os.getcwd(), tweets_file)
        self.verbose = verbose
        if verbose:
            print('Input tweets file:', filepath)
        file = open(filepath, 'r')
        lines = file.read().split('\n')
        # dict to store text of each tweet
        texts = dict()
        # dict to store corrections of each tweet
        corrections = defaultdict(list)
        # list of tweet id to maintain order
        order = []
        # number of tweets
        n = 0
        #  read and store data from each line of corpus
        for line in [line for line in lines if len(line) > 0]:
            splitted = line.split('\t')
            if line[0] != '\t':
                tweet_id, tweet_text = splitted
                order.append(tweet_id)
                texts[tweet_id] = tweet_text
                current_id = tweet_id
                n += 1
            else:
                # o:original word, t:class, c:corrected word
                o, t, c = splitted[1].split(' ')
                corrections[current_id].append((o, t, c))
        if verbose:
            print('Total tweets:', n)

        self.texts = texts
        self.order = order
        self.corrections = dict(corrections)

        twt = MyTokenizer()
        tokenized = defaultdict(dict)
        all_tokens = defaultdict(dict)
        # split tweets by tweet separator
        for tweet_id, tweet_text in texts.items():
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
                if tweet_id not in all_tokens:
                    all_tokens[tweet_id] = []
                all_tokens[tweet_id].extend([word for pos, word
                                             in enumerate(sent)])

        self.tokenized = dict(tokenized)
        self.all_tokens = dict(all_tokens)

    def get_texts(self):
        return self.texts

    def get_ids_order(self):
        return self.order

    def get_wtas(self, baseNorm=False):
        WTA = defaultdict(lambda: defaultdict(list))
        if baseNorm:
            classifier = enchant.Dict("es_AR")
        else:
            classifier = enchant.Dict("es_AR")

        for tweet_id in self.tokenized:
            for j in self.tokenized[tweet_id]:
                for word, pos in self.tokenized[tweet_id][j]:
                    # check if word is In Vocabulary
                    if not classifier.check(word):
                        # add (word, pos) to j-th sent
                        # of tweet with id = tweet_id
                        WTA[tweet_id][j].append((word, pos))
        if self.verbose:
            print('Tweets to correct:', len(WTA))
        return dict(WTA)

    def get_analyzable_tokens(self):
        return self.tokenized

    def get_all_tokens(self):
        return self.all_tokens
