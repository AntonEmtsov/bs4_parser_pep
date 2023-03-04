import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR,
    EXPECTED_STATUS,
    MAIN_DOC_URL,
    PATTERN,
    PEPS_URL,
    WHATS_NEW_URL,
)
from outputs import control_output
from utils import find_tag, get_response, get_soup

COMMAND_LINE_ARGUMENTS = 'Аргументы командной строки: {args}'
CONNECTION_ERROR = 'Не удалось установить соединение: {link}'
LIST_VERSIONS_ERROR = 'Не найден список c версиями Python'
LOG_ARCHIVE = 'Архив был загружен и сохранён: {archive_path}'
LOG_PARSER_RUNNING = 'Парсер запущен!'
LOG_PARSER_FINISHED_WORKING = 'Парсер завершил работу.'
MISMATCHED_STATUSES = (
    'Несовпадающие статусы: {link}\n'
    'Статус в карточке: {status}\n'
    'Ожидаемый статус: {preview_status}.'
)
PROGRAM_ERROR = 'Ошибка программы {error}'


def whats_new(session):
    li_tags = get_soup(session, WHATS_NEW_URL).select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    logs = []
    for section in tqdm(li_tags):
        version_link = urljoin(WHATS_NEW_URL, section.find('a')['href'])
        try:
            soup = get_soup(session, version_link)
            results.append(
                (
                    version_link,
                    find_tag(soup, 'h1').text,
                    soup.find('dl').text.replace('\n', ' ')
                )
            )
        except ConnectionError:
            logs.append(CONNECTION_ERROR.format(link=version_link))
    list(map(logging.info, logs))
    return results


def latest_versions(session):
    verions_python = get_soup(session, MAIN_DOC_URL).select(
        'div.sphinxsidebarwrapper ul'
    )
    for ul in verions_python:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise RuntimeError(LIST_VERSIONS_ERROR)
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    for a_tag in a_tags:
        text_match = re.search(PATTERN, a_tag.text,)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (a_tag['href'], version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    archive_url = urljoin(
        downloads_url,
        get_soup(session, downloads_url).select_one(
            'table.docutils td > a[href$="pdf-a4.zip"]'
        )['href']
    )
    downloads_dir = BASE_DIR / 'downloads'  # для тестов
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / archive_url.split('/')[-1]
    with open(archive_path, 'wb') as file:
        file.write(get_response(session, archive_url).content)
    logging.info(LOG_ARCHIVE.format(archive_path=archive_path))


def pep(session):
    peps_reference_internal = get_soup(session, PEPS_URL).select(
        '#numerical-index tbody tr'
    )
    results = defaultdict(int)
    logs = []
    for tr_tag in tqdm(peps_reference_internal):
        link = urljoin(PEPS_URL, find_tag(tr_tag, 'a')['href'])
        try:
            status = get_soup(session, link).select_one(
                'dl.rfc2822.field-list.simple'
                '> :-soup-contains("Status")'
                '+ dd'
            ).text
            preview_status = EXPECTED_STATUS.get(
                find_tag(tr_tag, 'td').text[1:]
            )
            if status not in preview_status:
                logs.append(MISMATCHED_STATUSES.format(
                        link=link,
                        status=status,
                        preview_status=preview_status[0]
                    )
                )
            results[status] += 1
        except ConnectionError:
            logs.append(CONNECTION_ERROR.format(link=link))
    list(map(logging.info, logs))
    return (
        [('Статус', 'Количество')]
        + sorted(results.items())
        + [('Всего', sum(results.values()))]
    )


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info(LOG_PARSER_RUNNING)
    args = configure_argument_parser(MODE_TO_FUNCTION.keys()).parse_args()
    logging.info(COMMAND_LINE_ARGUMENTS.format(args=args))
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
    except Exception as error:
        logging.exception(PROGRAM_ERROR.format(error=error))
    logging.info(LOG_PARSER_FINISHED_WORKING)


if __name__ == '__main__':
    main()
