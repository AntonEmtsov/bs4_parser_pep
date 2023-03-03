import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import (
    DT_FORMAT,
    LOG_DIR,
    LOG_FORMAT,
    PARSER_OPTION_FILE,
    PARSER_OPTION_PRETTY,
)


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера',
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша',
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(
            PARSER_OPTION_PRETTY,
            PARSER_OPTION_FILE,
        ),
        help='Дополнительные способы вывода данных',
    )
    return parser


def configure_logging(encoding='utf-8'):
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(
            RotatingFileHandler(
                LOG_DIR / 'parser.log',
                maxBytes=10 ** 6,
                backupCount=5,
                encoding=encoding,
            ),
            logging.StreamHandler(),
        ),
    )
