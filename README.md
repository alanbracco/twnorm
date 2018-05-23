# Text Normalization on tweets

This is a project to work on text normalization of tweets in spanish.

## Requirements
1. Python 3
2. pip
3. "es_AR" language on your system

## Installation
Open a terminal, go to **twnorm** *root folder* and execute:  
`pip install -r requirements.txt`

>If you want to use the lemmatizer you have to install the spacy spanish model:  
>Run `spacy download es` (This has to be downloaded only once).

## Usage
### Normalizer
Run by command `twnorm` and specify (using flags) the input file, model
language file and output file (not required).  
Example: `twnorm -i input_file.txt -m 3gram -o out.txt`
(run `twnorm -h` for more info).
>For baseline normalizer add flag -l (model file will not be considered)

### Evaluator
Run by command `evalnorm` and specify (using flags) the gold corpus file, the
generated corpus file and output file (not required).  
Example: `evalnorm -r real.txt -g generated.txt`
(run `evalnorm -h` for more info).
