from collections import defaultdict
from oov_picker import OOVpicker
from oov_classifier import OOVclassifier
from tweets_splitter import Tw_Splitter
from output_builder import OutputBuilder
from variants_generation import PrimaryCandidates, SecondaryCandidates
from candidate_selection import Selector


outputfile = 'result100.txt'
tweets_file = 'tweet-norm-dev100_annotated.txt'
modelfile = 'bo3'

splitter = Tw_Splitter(tweets_file)
picker = OOVpicker(splitter.texts)
classifier = OOVclassifier()
primary = PrimaryCandidates(2)
secondary = SecondaryCandidates()
selector = Selector(modelfile)
output = OutputBuilder(outputfile)
oovs = picker.OOV
tokenized = picker.tokenized
correct = defaultdict(dict)

for tweet_id, tweet in oovs.items():
    for j, sent in tweet.items():  # j is number of the sent
        for_prev = tokenized[tweet_id][j]
        correct[tweet_id][j] = []
        for word, pos in sent:
            class_number = classifier.classify(word)
            # if class is variant
            if class_number == 0:
                IVcandidates = primary.generate(word)
                # if no primary candidates generated
                if len(IVcandidates) == 0:
                    IVcandidates = secondary.generate(word)
                # if no secondary candidates generated
                if len(IVcandidates) == 0:
                    class_number = 1
                    correct_word = '-'
                    class_numb = 1
                else:
                    prev_tokens = selector.prev_tokens((word, pos), for_prev)
                    correct_word = selector.choose(prev_tokens, IVcandidates)
                    for_prev[for_prev.index((word, pos))] = (correct_word, pos)
            # if class is correct or NoES
            else:
                correct_word = '-'
            correct[tweet_id][j].append((word, class_number, correct_word))
output.build(splitter.texts, splitter.order, correct)
