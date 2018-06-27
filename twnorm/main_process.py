import time
from twnorm.aux import print_progress
from collections import defaultdict
from twnorm.wta_classifier import WTAclassifier, BaselineClassifier
from twnorm.tweets_splitter import Splitter
from twnorm.output_builder import OutputBuilder
from twnorm.variants_generation import VariantsGenerator, BaselineGenerator
from twnorm.candidate_selection import Selector, BaselineSelector


def MainProcess(input_file, output_file, model_file,
                lemma=False, times=0, baseline=False):

    print('Initializing resources...')
    init_start = time.time()
    splitter = Splitter(input_file, verbose=True, lemma=lemma)

    if baseline:
        classifier = BaselineClassifier()
        variants_generator = BaselineGenerator()
        selector = BaselineSelector()
    else:
        classifier = WTAclassifier(lemma=lemma)
        variants_generator = VariantsGenerator()
        selector = Selector(model_file)

    tokenized = splitter.get_analyzable_tokens()
    wtas = splitter.get_wtas(baseNorm=baseline)
    output = OutputBuilder(output_file, verbose=True)
    correct = defaultdict(dict)
    init_end = time.time()
    init_time = time.strftime("%M min %S sec",
                              time.gmtime(init_end - init_start))
    print('Initialization finished ({}).'.format(init_time))

    accumulated = 0
    tweets_time = {}
    total_tokens = 0
    print_progress(accumulated, len(wtas))
    for tweet_id, tweet in wtas.items():
        tweet_start = time.time()
        for j, sent in tweet.items():  # j is number of the sent
            for_prev = tokenized[tweet_id][j]  # For previous tokens corrected
            correct[tweet_id][j] = []
            for word, class_number, pos in sent:
                total_tokens += 1
                # if class is variant
                if classifier.is_variant(class_number):
                    IVcandidates = variants_generator.generate(word)
                    correct_word = selector.select_candidate(word, pos,
                                                             for_prev,
                                                             IVcandidates)
                    # If a correction was made
                    if correct_word != selector.UNKNOWN_CORRECTION:
                        # To pick corrected previous tokens
                        # in following iterations
                        for_prev[for_prev.index((word, pos))] = (correct_word,
                                                                 pos)
                # if class is correct or NoES
                else:
                    correct_word = selector.DEFAULT_CORRECTION

                correct[tweet_id][j].append((word, class_number, correct_word))
        accumulated += 1
        print_progress(accumulated, len(wtas))

        tweet_end = time.time()
        tweets_time[tweet_id] = tweet_end - tweet_start

    correct = dict(correct)
    output.build(splitter.get_texts(), splitter.get_ids_order(), correct)

    total_time = sum([t for t in tweets_time.values()])
    tweet_rate = len(wtas) / total_time

    token_rate = total_tokens / total_time

    process_time = time.strftime("%H hs %M min %S sec",
                                 time.gmtime(total_time))
    print('\nProcess finished ({}).\n'.format(process_time))
    print('Tweet rate (only tweets to correct):',
          round(tweet_rate, 2), 'tweets/sec')
    print('Token rate (only tokens to correct):',
          round(token_rate, 2), 'tokens/sec')

    if times > 0:
        print("\nTweets processing time")
        if times > len(wtas):
            times = len(wtas)
        tweets_times = [(tweet, time) for tweet, time in tweets_time.items()]
        tweets_times = sorted(tweets_times, key=lambda x: x[1], reverse=True)
        for i in range(times):
            print("Tweet ID: {} | Processing time: {} seg"
                  "".format(tweets_times[i][0], round(tweets_times[i][1], 3)))
