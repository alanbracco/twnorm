import time
import enchant
from os import path
from aux import progress
from collections import defaultdict
from wta_picker import WTApicker
from tweets_splitter import Tw_Splitter
from output_builder import OutputBuilder


def BaselineNormalization(input_file, output_file):

    print('Initializing resources...')
    splitter = Tw_Splitter(path.join('Input', input_file), verbose=True)
    picker = WTApicker(splitter.texts, verbose=True)
    output = OutputBuilder(output_file, verbose=True)
    wtas = picker.WTA
    correct = defaultdict(dict)
    iv_dict = enchant.Dict("es_AR")
    print('Initialization finished')

    n = 1
    start_time = time.time()
    for tweet_id, tweet in wtas.items():
        x = int((float(n)/picker.n)*20)
        perc = round((float(n)/picker.n)*100, 1)
        msg = ('Processing tweets...{}% ({}/{})'.format(perc, n, picker.n) +
               ' '*(len(str(picker.n)) + 6 - (len(str(perc))+len(str(n)))) +
               '[' + '#'*x + ' '*(20-x) + ']')

        progress(msg)
        n += 1
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

    correct = dict(correct)
    output.build(splitter.texts, splitter.order, correct)
    print('\nProcess finished.')
    total_time = time.time() - start_time
    print('Took:', time.strftime("%H hs %M min %S sec",
                                 time.gmtime(total_time)))
