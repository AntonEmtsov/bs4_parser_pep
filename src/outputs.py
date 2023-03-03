import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (
    BASE_DIR,
    DATETIME_FORMAT,
    PARSER_OPTION_FILE,
    PARSER_OPTION_PRETTY,
    RESULTS,
)

FILE_RESULTS_SAVED = 'Файл с результатами был сохранён: {file_path}'
NAME_CSV_FILE = '{cli_args}_{data}.csv'


# Вывод данных в терминал построчно.
def default_output(results, *args):
    for row in results:
        print(*row)


# Вывод данных в формате PrettyTable.
def pretty_output(results, *args):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


# Создание директории с результатами парсинга.
def file_output(results, cli_args):
    # Тесты ругаются без "results_dir = BASE_DIR / 'results'"
    results_dir = BASE_DIR / RESULTS
    results_dir.mkdir(exist_ok=True)
    file_path = (
        results_dir / NAME_CSV_FILE.format(
            cli_args=cli_args.mode,
            data=dt.datetime.now().strftime(DATETIME_FORMAT),
        )
    )
    with open(file_path, 'w', encoding='utf-8') as f:
        csv.writer(
            f, dialect=csv.unix_dialect
        ).writerows(
            results
        )
    logging.info(FILE_RESULTS_SAVED.format(file_path=file_path))


OUTPUTS = {
    PARSER_OPTION_FILE: file_output,
    PARSER_OPTION_PRETTY: pretty_output,
    None: default_output,
}


# Контроль вывода результатов парсинга.
def control_output(results, cli_args, outputs=OUTPUTS):
    outputs[cli_args.output](results, cli_args)
