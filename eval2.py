"""Evaluate normalization.

Usage:
  eval.py -r <gold_file> -g <generated_file> [-o <output_file>]
  eval.py -h | --help

Options:
  -r <gold_file>      Original corpus to compare results
  -g <generated_file> File generated by the normalizator
  -o <output_file>     Output file with normalization performance info
                       [default: stats.txt]
  -h --help            Show this screen.
"""
import os
import sys
from copy import copy
from docopt import docopt
from collections import Counter
from wta_picker import WTApicker
from tweets_splitter import Tw_Splitter


class Evaluator(object):
    def __init__(self, output_file):
        self.output_file = output_file

    def my_write(self, *args, stdout=False):
        with open(self.output_file, 'a') as file:
            print(*args, file=file)
        if stdout:
            print(*args)

    def print_symdiff_tweets(self, tweets_ids, tweets_dict, missing=True):
        if missing:
            header = "MISSING TWEETS"
            dashes = '-' * len(header)
            msg = "  - '{}' was not detected as WTA."
        else:
            header = "SURPLUS TWEETS"
            dashes = '-' * len(header)
            msg = "  - '{}' should not be detected as WTA."

        self.my_write(header)
        self.my_write(dashes)
        for tweet_id in tweets_ids:
            self.my_write(tweet_id)
            for wta, _, _ in tweets_dict[tweet_id]:
                self.my_write(msg.format(wta))

    def get_true_positives(self, gold_dict, gen_dict, for_correction=False):

        hits = 0
        tweet_ids = sorted(list(set(gold_dict.keys()) & set(gen_dict.keys())))

        for tweet_id in tweet_ids:
            current_hits = 0

            gold = gold_dict[tweet_id]
            generated = gen_dict[tweet_id]
            if not for_correction:
                gold = [w for w, _, _ in gold]
                generated = [w for w, _, _ in generated]

            current_hits += len(set(gold) & set(generated))

            gold_counter = Counter(gold)
            gen_counter = Counter(generated)
            for key, times in gold_counter.items():
                if key in generated and times > 1:
                    # Minus 1 because the first count appears in
                    # conjunction of gold and generated sets
                    current_hits += times - 1
            hits += current_hits

        return hits

    def get_accuracy(self, gold_dict, gen_dict, all_tokens,
                     for_correction=False):

        hits = 0
        for tweet_id in all_tokens:
            current_hits = 0
            tokens = all_tokens[tweet_id]

            if tweet_id in gold_dict and tweet_id in gen_dict:

                gold = [w for w, _, _ in gold_dict[tweet_id]]
                gen = [w for w, _, _ in gen_dict[tweet_id]]

                if for_correction:
                    gold_corr = {wd: corr for wd, _, corr
                                 in gold_dict[tweet_id]}
                    gen_corr = {wd: corr for wd, _, corr in gen_dict[tweet_id]}

                for token in tokens:
                    if (token in gold and token in gen):
                        if ((not for_correction) or
                                gold_corr[token] == gen_corr[token]):
                            current_hits += 1
                            gold.remove(token)
                            gen.remove(token)
                    elif (token not in gold and token not in gen):
                        current_hits += 1

            elif tweet_id not in gold_dict and tweet_id not in gen_dict:
                current_hits += len(tokens)

            elif tweet_id in gold_dict and tweet_id not in gen_dict:
                current_hits += len(tokens) - len(gold_dict[tweet_id])

            else:
                current_hits += len(tokens) - len(gen_dict[tweet_id])

            hits += current_hits

        total_tokens = sum(len(all_tokens[twt_id]) for twt_id in all_tokens)
        accuracy = hits / total_tokens

        return accuracy

    def get_precision_and_recall(self, gold_dict, gen_dict,
                                 for_correction=False):

        total_gold_wta = sum([len(gold_dict[x]) for x in gold_dict])
        total_gen_wta = sum([len(gen_dict[x]) for x in gen_dict])

        hits = self.get_true_positives(gold_dict, gen_dict, for_correction)

        precision = hits / total_gen_wta
        recall = hits / total_gold_wta

        return precision, recall

    def get_measures(self, gold_dict, gen_dict, all_tokens):

        self.my_write("STATISTICS")
        self.my_write("==========\n")

        set_gold_ids = set(gold_dict.keys())
        set_generated_ids = set(generated_dict.keys())

        # Tweets that appear in gold and generated
        both = sorted(list(set_gold_ids & set_generated_ids))
        # Tweets that only appear in gold
        missing_tweets = sorted(list(set_gold_ids - set_generated_ids))
        # Tweets that only appear in generated
        surplus_tweets = sorted(list(set_generated_ids - set_gold_ids))

        if missing_tweets:
            self.print_symdiff_tweets(missing_tweets, gold_dict, missing=True)

        if surplus_tweets:
            if missing_tweets:
                self.my_write('\n')
            self.print_symdiff_tweets(surplus_tweets, gen_dict, missing=False)

        # WTA detection metrics
        wta_precision, wta_recall = self.get_precision_and_recall(gold_dict,
                                                                  gen_dict)
        wta_accuracy = self.get_accuracy(gold_dict, gen_dict, all_tokens)

        # WTA correction metrics
        corr_precision, corr_recall = self.get_precision_and_recall(
                                        gold_dict, gen_dict,
                                        for_correction=True)
        corr_accuracy = self.get_accuracy(gold_dict, gen_dict, all_tokens,
                                          for_correction=True)


if __name__ == '__main__':

    opts = docopt(__doc__)

    gold_file = opts['-r']
    gold_file_path = os.path.join(os.getcwd(), 'Input', gold_file)
    if not os.path.isfile(gold_file_path):
        print('You must enter an existing input file.')
        sys.exit()

    generated_file = opts['-g']
    generated_file_path = os.path.join(os.getcwd(), 'Output', generated_file)
    if not os.path.isfile(generated_file_path):
        print('You must enter an existing input file.')
        sys.exit()

    output_file = opts['-o']
    if output_file is None:
        output_file = 'stats.txt'
    output_file = 'Stats/' + output_file
    if os.path.exists(output_file):
        os.remove(output_file)

    gold_splitter = Tw_Splitter(gold_file_path)
    gold_dict = gold_splitter.corrections

    generated_splitter = Tw_Splitter(generated_file_path)
    generated_dict = generated_splitter.corrections

    all_tokens = WTApicker(gold_splitter.texts).all_tokens

    evaluator = Evaluator(output_file)
    evaluator.get_measures(gold_dict, generated_dict, all_tokens)
