import time
import enchant
from os import path
from aux import print_progress
from collections import defaultdict
from tweets_splitter import Splitter
from output_builder import OutputBuilder


def BaselineNormalization(input_file, output_file):

    print('Initializing resources...')
    splitter = Splitter(input_file, verbose=True)
    output = OutputBuilder(output_file, verbose=True)
    wtas = splitter.get_wtas(baseNorm=True)
    correct = defaultdict(dict)
    iv_dict = enchant.Dict("es_AR")
    print('Initialization finished')

    accumulated = 1
    tweets_time = {}
    start_time = time.time()
    for tweet_id, tweet in wtas.items():
        tweet_start = time.time()
        print_progress(accumulated, len(wtas))
        accumulated += 1
        for j, sent in tweet.items():  # j is number of the sent
            correct[tweet_id][j] = []
            for word, pos in sent:
                if not iv_dict.check(word):
                    IVcandidates = iv_dict.suggest(word)
                    # if no candidates generated
                    if len(IVcandidates) == 0:
                        correct_word = '-'
                    else:
                        # a candidate can contain whitespaces
                        correct_word = IVcandidates[0].replace(' ', '_')
                else:
                    correct_word = '-'

                correct[tweet_id][j].append((word, 0, correct_word))

        tweet_end = time.time()
        tweets_time[tweet_id] = tweet_end - tweet_start

    correct = dict(correct)
    output.build(splitter.get_texts(), splitter.get_ids_order(), correct)

    total_time = sum([t for t in tweets_time.values()])
    tweet_rate = len(wtas) / total_time

    total_tokens = sum([len(correct[x][y]) for x in correct
                        for y in correct[x]])
    token_rate = total_tokens / total_time

    print('\nProcess finished.')
    print('Took:', time.strftime("%H hs %M min %S sec",
                                 time.gmtime(total_time)))
    print('Tweet rate (only tweets to correct):',
          round(tweet_rate, 2), 'tweets/sec')
    print('Token rate (only tokens to correct):',
          round(token_rate, 2), 'tokens/sec')
