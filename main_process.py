import time
from os import path
from aux import progress
from collections import defaultdict
from oov_picker import OOVpicker
from oov_classifier import OOVclassifier
from tweets_splitter import Tw_Splitter
from output_builder import OutputBuilder
from variants_generation import PrimaryCandidates, SecondaryCandidates
from candidate_selection import Selector
from candidates_memory import CandidatesMemory


def MainProcess(input_file, output_file, model_file):

    print('Initializing resources...')
    splitter = Tw_Splitter(path.join('Input', input_file))
    picker = OOVpicker(splitter.texts)
    classifier = OOVclassifier()
    primary = PrimaryCandidates(2)
    secondary = SecondaryCandidates()
    selector = Selector(model_file)
    output = OutputBuilder(output_file)
    oovs = picker.OOV
    tokenized = picker.tokenized
    correct = defaultdict(dict)
    memory = CandidatesMemory()
    print('Initialization finished')

    n = 1
    start_time = time.time()
    for tweet_id, tweet in oovs.items():
        x = int((float(n)/picker.n)*20)
        perc = round((float(n)/picker.n)*100, 1)
        msg = ('Processing tweets...{}% ({}/{})'.format(perc, n, picker.n) +
               ' '*(len(str(picker.n)) + 6 - (len(str(perc))+len(str(n)))) +
               '[' + '#'*x + ' '*(20-x) + ']')

        progress(msg)
        n += 1
        for j, sent in tweet.items():  # j is number of the sent
            for_prev = tokenized[tweet_id][j]
            correct[tweet_id][j] = []
            for word, pos in sent:
                class_number = classifier.classify(word)
                # if class is variant
                if class_number == 0:
                    if memory.already_processed(word):
                        IVcandidates = memory.get_candidates(word)
                    else:
                        IVcandidates = primary.generate(word)
                        # if no primary candidates generated
                        if len(IVcandidates) == 0:
                            IVcandidates = secondary.generate(word)
                            memory.add_candidates(word, IVcandidates,
                                                  primary=False)
                        else:
                            memory.add_candidates(word, IVcandidates)
                    # if no candidates generated
                    if len(IVcandidates) == 0:
                        class_number = 1
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
    correct = dict(correct)
    output.build(splitter.texts, splitter.order, correct)
    print('\nProcess finished.')
    total_time = time.time() - start_time
    print('Took:', time.strftime("%H hs %M min %S sec",
                                 time.gmtime(total_time)))
