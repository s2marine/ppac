import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging


def prompt(msg, results):
    [print(result.group ,result.arg) for result in results]
    return input('%s (y/n)' % msg) == 'y'
