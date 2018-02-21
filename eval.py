from tweets_splitter import Tw_Splitter


def get_measure(gold_dict, generated_dict):

    print("\nSTATISTICS")
    print("==========")
    print("There are ", len(gold_dict), "to correct.")
    print("You corrected ", len(generated_dict))

    set_gold = set(gold_dict.keys())
    set_generated = set(generated_dict.keys())

    both = sorted(list(set_gold & set_generated))

    print("#Corrected vs. #ToBeCorrected:", len(both))
    print("#NotCorrected vs. #ToBeCorrected:", len(set_gold - set_generated))

    hits = 0
    total = 0
    wrong_cl = 0
    wrong_co = 0
    for tweet_id in both:
        gold_corrections = gold_dict[tweet_id]
        own_corrections = generated_dict[tweet_id]
        set_gold = set(gold_corrections)
        set_own = set(own_corrections)

        gold_words = {word for word, _, _ in gold_corrections}
        own_words = {word for word, _, _ in own_corrections}

        missing_words = gold_words - own_words
        surplus_words = own_words - gold_words
        both_words = gold_words & own_words
        conflict_words = missing_words | surplus_words

        if missing_words or surplus_words:
            print("\nTweetID:", tweet_id)
            if missing_words:
                print("Missing corrections:", missing_words)
            if surplus_words:
                print("Surplus corrections:", surplus_words)

        for word in both_words:
            gold_tuples = [t for t in gold_corrections if t[0] == word]
            own_tuples = [t for t in own_corrections if t[0] == word]
            n_gold = len(gold_tuples)
            n_own = len(own_tuples)
            if n_gold != n_own:
                print("WARNING: word", word, "not analized.")
                print("You corrected", n_own, "times,",
                      "but you have to correct it", n_gold, "times.")
            else:
                total += n_gold
                for i in range(n_gold):
                    wg, clg, cog = gold_tuples[i]
                    wo, clo, coo = own_tuples[i]
                    assert wg == wo
                    if clg != clo:
                        wrong_cl += 1
                        print("You classified", word, "as", clo,
                              "but it is", clg)
                    else:
                        if cog != coo:
                            wrong_co += 1
                            print("You corrected", word, "as", coo,
                                  "but it is", cog)
                        else:
                            hits += 1
    assert wrong_cl + wrong_co == total - hits
    print("\nYou hit", hits, "out of", total, "corrections.")
    print("The system classified", wrong_cl, "words differently,",
          "and missed", wrong_co, "corrections.")


if __name__ == '__main__':
    gold_dict = Tw_Splitter('Input/corpus_v1.txt').corrections
    generated_dict = Tw_Splitter('Output/corpus_v1.txt').corrections

    get_measure(gold_dict, generated_dict)