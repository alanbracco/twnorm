"""
Train an n-gram model.

Usage:
  train_model.py -n <n> -o <file>
  train_model.py -h | --help

Options:
  -n <n>        Order of the model.
  -o <file>     Output model file.
  -h --help     Show this screen.
"""

import pickle
from docopt import docopt
from corpus.ancora import AncoraCorpusReader
from languagemodeling.ngram import BackOffNGram

if __name__ == '__main__':
    opts = docopt(__doc__)
    n = int(opts['-n'])
    path = 'path to /ancora-3.0.1es/'
    corpus = AncoraCorpusReader(path)
    sents = list(corpus.sents())
    # split words with "_" (underscore)
    checked_sents = []
    for i, sent in enumerate(sents):
        checked_sents.append([])
        for word in sent:
            if '_' in word:
                new_words = word.split('_')
                for new_word in new_words:
                    checked_sents[i].append(new_word)
            else:
                checked_sents[i].append(word)
    # build model
    model = BackOffNGram(n, checked_sents)
    # # save it
    filename = opts['-o']
    f = open(filename, 'wb')
    pickle.dump(model, f)
    f.close()
