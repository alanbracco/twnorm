import os
from collections import defaultdict


class Tw_Splitter(object):
    def __init__(self, tweets_file):
        filepath = os.path.join(os.getcwd(), 'Input', tweets_file)
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
        print('Total tweets:', n)
        self.n = n
        self.texts = texts
        self.order = order
        self.corrections = dict(corrections)
