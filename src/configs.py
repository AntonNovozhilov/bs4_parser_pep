import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import BASE_DIR

LOG_FORMAT = '%(asctime)s - [%(levelname)s] - %(message)s'
LOG_FORMAT_STATUS = (
    'Несовпадающие статусы:\n%s\nСтатус в карточке: %s\nОжидаемый статус: %s\n'
)
DT_FORMAT = '%d.%m.%Y %H:%M:%S'

def configure_argument_parser(available_modes):
    '''Описание функций парсера.'''
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=('pretty', 'file', ),
        help='Дополнительные способы вывода данных'
    )
    return parser

def configure_logging():
    '''Конфигурация логирования.'''
    log_dir = BASE_DIR / 'logging'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'parser.log'
    rotation_handler = RotatingFileHandler(
        log_file,
        maxBytes=10**6,
        backupCount=5,
        encoding='utf-8',
        )
    logging.basicConfig(
        format=LOG_FORMAT,
        datefmt=DT_FORMAT,
        level=logging.INFO,
        handlers=(rotation_handler, logging.StreamHandler())
    )
