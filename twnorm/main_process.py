import time
from twnorm.aux import print_progress
from collections import defaultdict
from twnorm.wta_classifier import WTAclassifier, BaselineClassifier
from twnorm.tweets_splitter import Splitter
from twnorm.output_builder import OutputBuilder
from twnorm.variants_generation import VariantsGenerator, BaselineGenerator
from twnorm.candidate_selection import Selector, BaselineSelector


def MainProcess(input_file, output_file, model_file, lemma, baseline):

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

    accumulated = 1
    tweets_time = {}
    total_tokens = 0
    for tweet_id, tweet in wtas.items():
        tweet_start = time.time()
        print_progress(accumulated, len(wtas))
        accumulated += 1
        for j, sent in tweet.items():  # j is number of the sent
            for_prev = tokenized[tweet_id][j]  # For previous tokens corrected
            correct[tweet_id][j] = []
            for word, pos in sent:
                total_tokens += 1
                class_number = classifier.classify(word)
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

        tweet_end = time.time()
        tweets_time[tweet_id] = tweet_end - tweet_start

    correct = dict(correct)
    output.build(splitter.get_texts(), splitter.get_ids_order(), correct)

    total_time = sum([t for t in tweets_time.values()])
    tweet_rate = len(wtas) / total_time

    token_rate = total_tokens / total_time

    print('\nProcess finished.')
    print('Took:', time.strftime("%H hs %M min %S sec",
                                 time.gmtime(total_time)))
    print('Tweet rate (only tweets to correct):',
          round(tweet_rate, 2), 'tweets/sec')
    print('Token rate (only tokens to correct):',
          round(token_rate, 2), 'tokens/sec')
