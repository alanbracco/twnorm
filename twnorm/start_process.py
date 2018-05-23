"""Train a parser.

Usage:
  twnorm -i <input_file> [-o <output_file>] [-m <model_file>] [-b] [-l]
  twnorm -h | --help

Options:
  -m <model_file>    Model to use in candidates selection
  -i <input_file>    Input file with tweets
  -o <output_file>   Output file with tweets and list of corrections
                     [default: output.txt]
  -l                 Use lemmatizer
  -b                 Use baseline normalization
  -h --help     Show this screen.
"""
import os
import sys
from docopt import docopt
from twnorm.main_process import MainProcess
from twnorm.basenorm import BaselineNormalization


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

    if opts['-b']:
        BaselineNormalization(input_file_path, output_file_path)
    else:
        model_file = opts['-m']
        model_file_path = os.path.join(project_root_path, 'Models', model_file)
        if not os.path.isfile(model_file_path):
            print('You must enter an existing model file.')
            sys.exit()
        lemmatize = bool(opts['-l'])
        MainProcess(input_file_path, output_file_path, model_file_path,
                    lemmatize)


if __name__ == '__main__':
    start_process()