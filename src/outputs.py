import datetime as dt
import csv
import logging

from prettytable import PrettyTable
from constants import NAMEDATE, BASE_DIR




def control_output(results, cli_args):
    """Docstring"""
    output = cli_args.output
    if output == 'pretty':
        pretty_output(results)
    if output == 'file':
        file_output(results, cli_args)
    else:
        default_output(results)
 
def default_output(results):
    """Docstring"""

    for row in results:
        print(*row)

def pretty_output(results):
    """Docstring"""

    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)

def file_output(results, cli_args):
    """Docstring"""

    results_dir = BASE_DIR / 'fils'

    results_dir.mkdir(exist_ok=True)

    parse_mode = cli_args.mode

    now = dt.datetime.now()
    now_formated = now.strftime(NAMEDATE)
    file_name = f'{parse_mode}-{now_formated}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}') 