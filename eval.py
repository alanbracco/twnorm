import os
from copy import copy
from tweets_splitter import Tw_Splitter
from oov_picker import OOVpicker


def my_write(*args, stdout=False, filename='stats.txt'):
    with open(filename, 'a') as file:
        print(*args, file=file)
    if stdout:
        print(*args)


def get_measure(gold_dict, generated_dict, tokenized):

    my_write("\nSTATISTICS")
    my_write("==========")

    set_gold_ids = set(gold_dict.keys())
    set_generated_ids = set(generated_dict.keys())

    both = sorted(list(set_gold_ids & set_generated_ids))
    missing_tweets = sorted(list(set_gold_ids - set_generated_ids))

    hits_corr = 0
    hits_class = 0
    total = 0
    wrong_cl = 0
    wrong_co = 0
    misses = 0
    surpluses = 0
    unanalyzed = 0  # Quantity of words not analyzed
    total_missing_corr = 0  # Total number of corrections in 'gold' tweets

    oov_tp = 0  # Detected as OOV and it is OOV (True positives)
    oov_fp = 0  # Detected as OOV but it is not OOV (False positives)
    oov_tn = 0  # Not detected as OOV and it is not OOV (True Negatives)
    oov_fn = 0  # Not detected as OOV but it is OOV (False Negatives)
    total_words = 0  # Total number of words

    for tweet_id in missing_tweets:
        total_missing_corr += len(gold_dict[tweet_id])

    for tweet_id in both:
        gold_corrections = gold_dict[tweet_id]
        own_corrections = generated_dict[tweet_id]

        gold_words = [word for word, _, _ in gold_corrections]
        set_gold_words = set(gold_words)
        own_words = [word for word, _, _ in own_corrections]
        set_own_words = set(own_words)

        all_words = [word for j in tokenized[tweet_id].keys()
                     for word, _ in tokenized[tweet_id][j]]

        my_oov = copy(own_words)
        gold_oov = copy(gold_words)
        total_words += len(all_words)
        for word in all_words:
            if word in gold_oov and word in my_oov:
                oov_tp += 1
                my_oov.remove(word)
                gold_oov.remove(word)
            elif word in gold_oov and word not in my_oov:
                oov_fn += 1
                gold_oov.remove(word)
            elif word not in gold_oov and word in my_oov:
                oov_fp += 1
                my_oov.remove(word)
            elif word not in gold_oov and word not in my_oov:
                oov_tn += 1

        missing_words = set_gold_words - set_own_words
        surplus_words = set_own_words - set_gold_words
        both_words = set_gold_words & set_own_words
        conflict_words = missing_words | surplus_words

        if missing_words or surplus_words:
            my_write("\nTweetID:", tweet_id)
            my_write("-"*len("TweetID: " + tweet_id))
            if missing_words:
                sorted_missing_words = sorted(list(missing_words))
                misses += len(missing_words)
                my_write("Missing words:", sorted_missing_words)
                for word in sorted_missing_words:
                    correct_words = [c for w, _, c in gold_corrections
                                     if w == word]
                    if len(correct_words) > 1:
                        my_write("WARNING: There are more than one correction"
                                 "for '{}'. All corrections will be printed"
                                 "".format(word))
                    for correct_word in correct_words:
                        my_write(" - Word '{}' should be corrected as '{}'."
                                 "".format(word, correct_word))
            if surplus_words:
                surpluses += len(surplus_words)
                my_write("Surplus words:", sorted(list(surplus_words)))

        for word in sorted(list(both_words)):
            gold_tuples = [t for t in gold_corrections if t[0] == word]
            own_tuples = [t for t in own_corrections if t[0] == word]
            n_gold = len(gold_tuples)
            n_own = len(own_tuples)
            if n_gold != n_own:
                unanalyzed += 1
                my_write("WARNING: word", word, "not analized.")
                my_write("You corrected", n_own, "time(s),",
                         "but you have to correct it", n_gold, "time(s).")
                my_write("DETAILS")
                my_write("Actual corrections:", gold_tuples)
                my_write("Current corrections:", own_tuples)
            else:
                total += n_gold
                for i in range(n_gold):
                    wg, clg, cog = gold_tuples[i]
                    wo, clo, coo = own_tuples[i]
                    assert wg == wo
                    if clg != clo:
                        wrong_cl += 1
                        my_write("You classified", word, "as", clo,
                                 "but it is", clg)
                    else:
                        hits_class += 1
                        if cog != coo:
                            wrong_co += 1
                            my_write("You corrected", word, "as", coo,
                                     "but it is", cog)
                        else:
                            hits_corr += 1

    assert wrong_cl + wrong_co == total - hits_corr

    total += total_missing_corr

    assert total_words == oov_fn + oov_fp + oov_tn + oov_tp

    oov_accuracy = (oov_tp + oov_tn) / total_words
    oov_precision = oov_tp / (oov_tp + oov_fp)
    oov_recall = oov_tp / (oov_tp + oov_fn)

    cl_accuracy = hits_class / total

    co_accuracy = hits_corr / total

    my_write("\nSUMMARY", stdout=True)
    my_write("=======", stdout=True)
    if len(gold_dict) > 1:
        tweets = 'tweets'
    else:
        tweets = 'tweet'
    my_write("There are", len(gold_dict), tweets, "to correct.", stdout=True)
    my_write("You corrected", len(generated_dict), stdout=True)
    my_write("#TweetsCorrected vs. #TweetsToBeCorrected:",
             len(both), stdout=True)
    my_write("#TweetsCorrected vs. #TweetsNotToBeCorrected:",
             len(set_generated_ids - set_gold_ids), stdout=True)
    my_write("#TweetsNotCorrected vs. #TweetsToBeCorrected:",
             len(missing_tweets), stdout=True)
    my_write("You hit", hits_corr, "out of", total, "corrections (" +
             str(total_missing_corr), "corrections are missing).", stdout=True)
    my_write("You hit", hits_class, "out of", total, "classifications (" +
             str(total_missing_corr), "corrections are missing).", stdout=True)
    my_write("The system MISCLASSIFIED", wrong_cl, "words.", stdout=True)
    my_write("The system MISCORRECTED", wrong_co, "words.", stdout=True)
    my_write("Missing corrections:", misses, stdout=True)
    my_write("Surplus corrections:", surpluses, stdout=True)
    my_write("Words unanalyzed (corrected not equal times):",
             unanalyzed, stdout=True)

    my_write("\nOOV detection", stdout=True)
    my_write("-------------", stdout=True)
    my_write("Accuracy:", round(oov_accuracy, 2), stdout=True)
    my_write("Precision:", round(oov_precision, 2), stdout=True)
    my_write("Recall:", round(oov_recall, 2), stdout=True)

    my_write("\nClassification", stdout=True)
    my_write("--------------", stdout=True)
    my_write("Accuracy:", round(cl_accuracy, 2), stdout=True)

    my_write("\nCorrections", stdout=True)
    my_write("-----------", stdout=True)
    my_write("Accuracy:", round(co_accuracy, 2), stdout=True)
    my_write("Note that if class is wrong it is counted as MISCORRECTED too.",
             stdout=True)


    print("\nA detailed information can be found in 'stats.txt'")


if __name__ == '__main__':
    input_splitter = Tw_Splitter('Input/corpus_v1.txt')
    output_splitter = Tw_Splitter('Output/corpus_v1.txt')

    gold_dict = input_splitter.corrections
    generated_dict = output_splitter.corrections

    tokenized = OOVpicker(input_splitter.texts).tokenized

    if os.path.exists('stats.txt'):
        os.remove('stats.txt')

    get_measure(gold_dict, generated_dict, tokenized)
