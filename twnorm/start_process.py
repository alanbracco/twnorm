"""TEXT NORMALIZATOR

Usage:
  twnorm -i <input_file> [-o <output_file>] [-m <model_file>] [-l] [-b]
         [-t <number>]
  twnorm -h | --help

Options:
  -i <input_file>    Input file with tweets
  -o <output_file>   Output file with tweets and list of corrections
                     [default: output.txt]
  -m <model_file>    Model to use in candidates selection
  -l                 Enables lemmatizer
  -b                 Enables baseline normalization
  -t <number>        Show the <number> most costly tweets (processing time)
  -h --help          Show this screen.
"""
import os
import sys
from docopt import docopt
from twnorm.main_process import MainProcess


def start_process():
    abs_current_path = os.path.dirname(os.path.abspath(__file__))
    project_root_path = os.path.join(abs_current_path, '..')

    opts = docopt(__doc__)

    input_file = opts['-i']
    input_file_path = os.path.join(project_root_path, 'Input', input_file)
    input_file_path = os.path.abspath(input_file_path)
    if not os.path.isfile(input_file_path):
        print('You must enter an existing input file.')
        sys.exit()

    output_file = opts['-o']
    if not output_file:
        output_file = 'output.txt'
    output_file_path = os.path.join(project_root_path, 'Output', output_file)
    output_file_path = os.path.abspath(output_file_path)

    baseline = bool(opts['-b'])
    if not baseline:
        model_file = opts['-m']
        if model_file:
            model_file_path = os.path.join(project_root_path, 'Models',
                                           model_file)
        if not (model_file and os.path.isfile(model_file_path)):
            print('You must enter an existing model file.')
            sys.exit()
        lemmatize = bool(opts['-l'])
    else:
        model_file_path = ''
        lemmatize = False

    times = opts['-t']
    if times:
        try:
            times = int(times)
        except Exception:
            print("Tweets quantity must be an integer.")
            sys.exit()
    else:
        times = 0

    MainProcess(input_file_path, output_file_path, model_file_path,
                lemma=lemmatize, times=times, baseline=baseline)


if __name__ == '__main__':
    start_process()
