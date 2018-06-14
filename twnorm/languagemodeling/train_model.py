"""
Train an n-gram model.

Usage:
  train.py -i <input_corpus> -n <n> [-m <model>] -o <file>
  train.py -h | --help

Options:
  -i <input_file> Input file (plain text corpus)
  -n <n>            Order of the model.
  -m <model>        Model to use [default: ngram]:
                      ngram: Unsmoothed n-grams.
                      addone: N-grams with add-one smoothing.
                      inter: N-grams with interpolation smoothing.
                      back: N-grams with backoff smoothing.
  -o <output_file>  Output model file.
  -h --help         Show this screen.
"""

import os
import pickle
from docopt import docopt
from nltk.data import load
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import PlaintextCorpusReader
from twnorm.languagemodeling.ngram import NGram, AddOneNGram
from twnorm.languagemodeling.ngram import InterpolatedNGram, BackOffNGram

if __name__ == '__main__':
    opts = docopt(__doc__)

    # set pattern for tokenize
    pattern = r'''(?ix)    # set flag to allow verbose regexps
        (?:Inc\.|sra\.|sr\.)
        | (?:[A-Z]\.)+        # abbreviations, e.g. U.S.A.
        | \w+(?:-\w+)*        # words with optional internal hyphens
        | \$?\d+(?:\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
        | \.\.\.            # ellipsis
        | [][.,;"'?():-_`]  # these are separate tokens; includes [ ],
    '''

    # set tokenizer
    sent_tokenizer = load('tokenizers/punkt/spanish.pickle')
    tokenizer = RegexpTokenizer(pattern)

    input_file = opts['-i']
    if not os.path.isfile(input_file):
        print('You must enter an existing input file.')
        sys.exit()

    # load data
    path, input_file = os.path.split(input_file)
    corpus = PlaintextCorpusReader(path, input_file,
                                   word_tokenizer=tokenizer,
                                   sent_tokenizer=sent_tokenizer)
    # store tokenized sents
    sents = corpus.sents()

    # train the (chosen) model
    n = int(opts['-n'])
    mode = str(opts['-m'])
    if mode == "addone":
        model = AddOneNGram(n, sents)
    elif mode == "inter":
        model = InterpolatedNGram(n, sents)
    elif mode == "back":
        model = BackOffNGram(n, sents)
    else:
        model = NGram(n, sents)

    # save it
    filename = opts['-o']
    f = open(filename, 'wb')
    pickle.dump(model, f)
    f.close()
