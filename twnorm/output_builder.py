import os


class OutputBuilder(object):
    def __init__(self, filepath, verbose=False):
        self.filepath = filepath
        self.line_start = '\t'
        self.end_correction = '\n'
        if verbose:
            print('Output file:', self.filepath)

    def build(self, texts, order, correct):
        with open(self.filepath, 'w') as file:
            for tweet_id in order:
                file.write(tweet_id + '\t' + texts[tweet_id] + '\n')
                if tweet_id in correct.keys():
                    corrections = []
                    for j in correct[tweet_id].keys():
                        # o:original word, t:class, c:corrected word
                        for o, t, c in correct[tweet_id][j]:
                            correction = ' '.join([o, str(t), c])
                            corrections.append(correction)
                    for corr in corrections:
                        file.write(self.line_start)
                        file.write(corr)
                        file.write(self.end_correction)
