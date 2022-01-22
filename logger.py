import logging
logging.basicConfig(filename='actions.log', level=logging.INFO, filemode='w', format='%(message)s')
logging.info('Trading bot has been started')
from typing import List
from datetime import datetime, timedelta

def write_starting_log():
    logging.info('program started')

def write_log(time, action: str, indicator_names: List[str], indicator_values: List[any]) -> str:
    indicator_message = time + ' : ' + action + ' | '
    for index, val in enumerate(indicator_names):
        if str == type(indicator_values[index]):
            indicator_message += indicator_names[index] + ': ' + indicator_values[index]  +'; '
        else:
            indicator_message += indicator_names[index] + ': ' + "{:.4f}".format(indicator_values[index])  +'; '
    logging.info(indicator_message)