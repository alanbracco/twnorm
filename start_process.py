"""Train a parser.

Usage:
  start_process.py -i <input_file> [-o <output_file>] -m <model_file>
  start_process.py -h | --help

Options:
  -m <model_file>    Model to use in candidates selection
  -i <input_file>    Input file with tweets
  -o <output_file>   Output file with tweets and list of corrections
                     [default: output.txt]
  -h --help     Show this screen.
"""
import os
import sys
from docopt import docopt
from main_process import MainProcess


if __name__ == '__main__':
    opts = docopt(__doc__)

    input_file = opts['-i']
    input_file_path = os.path.join(os.getcwd(), 'Input', input_file)
    if not os.path.isfile(input_file_path):
        print('You must enter an existing input file.')
        sys.exit()

    output_file = opts['-o']
    if output_file is None:
        output_file = 'output.txt'

    model_file = opts['-m']
    model_file = os.path.join(os.getcwd(), 'Models', model_file)
    if not os.path.isfile(model_file):
        print('You must enter an existing model file.')
        sys.exit()

    MainProcess(input_file, output_file, model_file)
