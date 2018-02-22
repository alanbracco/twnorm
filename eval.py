import os
from tweets_splitter import Tw_Splitter


def my_write(*args, stdout=False, filename='stats.txt'):
    with open(filename, 'a') as file:
        print(*args, file=file)
    if stdout:
        print(*args)


def get_measure(gold_dict, generated_dict):

    my_write("\nSTATISTICS")
    my_write("==========")

    set_gold_ids = set(gold_dict.keys())
    set_generated_ids = set(generated_dict.keys())

    both = sorted(list(set_gold_ids & set_generated_ids))
    missing_tweets = sorted(list(set_gold_ids - set_generated_ids))

    hits = 0
    total = 0
    wrong_cl = 0
    wrong_co = 0
    misses = 0
    surpluses = 0
    unanalyzed = 0  # Quantity of words not analyzed
    total_gold = 0  # Total number of corrections in 'gold' tweets
    total_own = 0  # Total number of corrections in 'own' tweets

    for tweet_id in missing_tweets:
        total_gold += len(gold_dict[tweet_id])

    for tweet_id in both:
        gold_corrections = gold_dict[tweet_id]
        own_corrections = generated_dict[tweet_id]
        total_gold += len(gold_corrections)
        total_own += len(own_corrections)

        gold_words = {word for word, _, _ in gold_corrections}
        own_words = {word for word, _, _ in own_corrections}

        missing_words = gold_words - own_words
        surplus_words = own_words - gold_words
        both_words = gold_words & own_words
        conflict_words = missing_words | surplus_words

        if missing_words or surplus_words:
            my_write("\nTweetID:", tweet_id)
            my_write("-"*len("TweetID: " + tweet_id))
            if missing_words:
                misses += len(missing_words)
                my_write("Missing corrections:", missing_words)
            if surplus_words:
                surpluses += len(surplus_words)
                my_write("Surplus corrections:", surplus_words)

        for word in both_words:
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
                        if cog != coo:
                            wrong_co += 1
                            my_write("You corrected", word, "as", coo,
                                     "but it is", cog)
                        else:
                            hits += 1
    assert wrong_cl + wrong_co == total - hits

    my_write("\nSUMMARY", stdout=True)
    my_write("=======", stdout=True)
    my_write("There are ", len(gold_dict), "to correct.", stdout=True)
    my_write("You corrected ", len(generated_dict), stdout=True)
    my_write("#TweetsCorrected vs. #TweetsToBeCorrected:",
             len(both), stdout=True)
    my_write("#TweetsCorrected vs. #TweetsNotToBeCorrected:",
             len(set_generated_ids - set_gold_ids), stdout=True)
    my_write("#TweetsNotCorrected vs. #TweetsToBeCorrected:",
             len(missing_tweets), stdout=True)
    my_write("You hit", hits, "out of", total, "corrections.", stdout=True)
    my_write("The system classified", wrong_cl, "words differently,",
             "and", wrong_co, "are miscorrected.", stdout=True)
    my_write("Missing corrections:", misses, stdout=True)
    my_write("Surplus corrections:", surpluses, stdout=True)
    my_write("Words unanalyzed (corrected not equal times):",
             unanalyzed, stdout=True)

    print("\nA detailed information can be found in 'stats.txt'")


if __name__ == '__main__':
    gold_dict = Tw_Splitter('Input/corpus_v1.txt').corrections
    generated_dict = Tw_Splitter('Output/corpus_v1.txt').corrections

    if os.path.exists('stats.txt'):
        os.remove('stats.txt')

    get_measure(gold_dict, generated_dict)
