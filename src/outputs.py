import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


# Контроль вывода результатов парсинга.
def control_output(results, cli_args):
    output = cli_args.output
    if output == 'pretty':
        pretty_output(results)
    elif output == 'file':
        file_output(results, cli_args)
    else:
        default_output(results)


# Вывод данных в терминал построчно.
def default_output(results):
    for row in results:
        print(*row)


# Вывод данных в формате PrettyTable.
def pretty_output(results):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


# Создание директории с результатами парсинга.
def file_output(results, cli_args):
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    file_path = (
        results_dir /
        f'{cli_args.mode}_{dt.datetime.now().strftime(DATETIME_FORMAT)}.csv'
    )
    with open(file_path, 'w', encoding='utf-8') as f:
        csv.writer(f, dialect='unix').writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')
