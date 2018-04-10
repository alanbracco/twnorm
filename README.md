# Text Normalization on tweets

This is a project to work on text normalization of tweets in spanish.

## Installation

## Usage

### Settings before execution
Once, you have installed all the requirements, in *line 21* of
*wta_classifier.py* file, you have to enter the path to TreeTagger installation
directory.
Also, you need to activate *twnorm_venv* virtual environment.
In order to do this, type **workon twnorm_venv** in the console and press Enter.
*(twnorm_venv)* will appear in prompt.

### Execution
Execute start_proccess.py and specify (using flags) the input file, model
language file and output file (not required).
Example: *python start_proccess.py -i input_file.txt -m 3gram -o out.txt*
(run *python start_proccess.py -h* for more info).
