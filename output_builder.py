import os


class OutputBuilder(object):
    def __init__(self, filename):
        self.filepath = os.path.join(os.getcwd(), 'Output', filename)
        self.line_start = '\t'
        self.correction_separator = '\n\t'
        self.end_corrections = '\n'
        print('Output file:', self.filepath)

    def build(self, texts, order, correct):
        file = open(self.filepath, 'w')
        for tweet_id in order:
            file.write(tweet_id + '\t' + texts[tweet_id] + '\n')
            for j in correct[tweet_id].keys():
                for i, (org_word, class_n, correct_w) in \
                        enumerate(correct[tweet_id][j]):
                    if i > 0 and i < len(correct[tweet_id][j]):
                        file.write(self.correction_separator)
                    elif i == 0:
                        file.write(self.line_start)
                    line = org_word + ' ' + str(class_n) + ' ' + correct_w
                    file.write(line)
                    if i == len(correct[tweet_id][j]) - 1:
                        file.write(self.end_corrections)
        file.close()
