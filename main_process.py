import time
from os import path
from aux import progress
from collections import defaultdict
from wta_picker import WTApicker
from wta_classifier import WTAclassifier
from tweets_splitter import Tw_Splitter
from output_builder import OutputBuilder
from variants_generation import VariantsGenerator
from candidate_selection import Selector


def MainProcess(input_file, output_file, model_file):

    print('Initializing resources...')
    splitter = Tw_Splitter(path.join('Input', input_file), verbose=True)
    picker = WTApicker(splitter.texts, verbose=True)
    classifier = WTAclassifier()
    variants_generator = VariantsGenerator()
    selector = Selector(model_file)
    output = OutputBuilder(output_file, verbose=True)
    wtas = picker.WTA
    tokenized = picker.tokenized
    correct = defaultdict(dict)
    print('Initialization finished')

    n = 1
    tweets_time = {}
    for tweet_id, tweet in wtas.items():
        tweet_start = time.time()
        x = int((float(n)/picker.n)*20)
        perc = round((float(n)/picker.n)*100, 1)
        msg = ('Processing tweets...{}% ({}/{})'.format(perc, n, picker.n) +
               ' '*(len(str(picker.n)) + 6 - (len(str(perc))+len(str(n)))) +
               '[' + '#'*x + ' '*(20-x) + ']')

        progress(msg)
        n += 1
        for j, sent in tweet.items():  # j is number of the sent
            for_prev = tokenized[tweet_id][j]  # For previous tokens corrected
            correct[tweet_id][j] = []
            for word, pos in sent:
                class_number = classifier.classify(word)
                # if class is variant
                if class_number == 0:
                    IVcandidates = variants_generator.generate(word)
                    # if no candidates generated
                    if len(IVcandidates) == 0:
                        correct_word = '-'
                    else:
                        prev_tokens = selector.prev_tokens((word, pos),
                                                           for_prev)
                        correct_word = selector.choose(prev_tokens,
                                                       IVcandidates)
                        for_prev[for_prev.index((word, pos))] = (
                                                        correct_word, pos)
                # if class is correct or NoES
                else:
                    correct_word = '-'

                correct[tweet_id][j].append((word, class_number, correct_word))

        tweet_end = time.time()
        tweets_time[tweet_id] = tweet_end - tweet_start

    correct = dict(correct)
    output.build(splitter.texts, splitter.order, correct)

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
