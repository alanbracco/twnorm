class OutputBuilder(object):
    def __init__(self, filepath):
        self.filepath = filepath

    def build(self, texts, order, correct):
        file = open(self.filepath, 'w')
        for tweet_id in order:
            file.write(tweet_id + '\t' + texts[tweet_id] + '\n')
            for j in correct[tweet_id].keys():
                for org_word, class_n, correct_w in correct[tweet_id][j]:
                    line = org_word + ' ' + str(class_n) + ' ' + correct_w
                    file.write('\t' + line + '\n')
        file.close()
