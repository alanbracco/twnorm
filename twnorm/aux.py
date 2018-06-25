import sys


def progress(msg, width=None):
    """Ouput the progress of something on the same line."""
    if not width:
        width = len(msg)
    print('\b' * width + msg, end='')
    sys.stdout.flush()


def to_str_perc(number):
    return "{0:.2f}%".format(round(number*100, 2))


def print_progress(accumulated, total):
    progress_symbol = '#'
    no_progress_symbol = '.'
    progress_bar_length = 20
    perc_decimals = 1

    x = int((float(accumulated)/total)*progress_bar_length)
    perc = round((float(accumulated)/total)*100, perc_decimals)
    msg = ('Processing tweets...{}% ({}/{})'.format(perc, accumulated, total) +
           ' '*(len(str(total)) + 6 - (len(str(perc))+len(str(accumulated)))) +
           '[' + progress_symbol*x +
           no_progress_symbol*(progress_bar_length-x) + ']')
    progress(msg)
