import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, NAMEDATE


def control_output(results, cli_args):
    '''Задаем атрибуты.'''
    output = cli_args.output
    if output == 'pretty':
        pretty_output(results)
    elif output == 'file':
        file_output(results, cli_args)
    else:
        default_output(results)

def default_output(results):
    '''Реагирование на отсутвие атрибута.'''
    for row in results:
        print(*row)

def pretty_output(results):
    '''Создаем таблицу.'''
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)

def file_output(results, cli_args):
    '''Создаем файл с данными в формате csv.'''
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parse_mode = cli_args.mode
    now = dt.datetime.now()
    now_formated = now.strftime(NAMEDATE)
    file_name = f'{parse_mode}_{now_formated}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerows(results)
    logging.info('Файл с результатами был сохранён: %s', file_path)
