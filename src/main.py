import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEPS_URL
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    session = requests_cache.CachedSession()
    response = get_response(session, whats_new_url)
    if not response:
        return
    sections_by_python = find_tag(
        find_tag(
            BeautifulSoup(response.text, features='lxml'),
            'section',
            attrs={'id': 'what-s-new-in-python'},
        ),
        'div',
        attrs={'class': 'toctree-wrapper'},
    ).find_all('li', attrs={'class': 'toctree-l1'})
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_link = urljoin(whats_new_url, section.find('a')['href'])
        response = get_response(session, version_link)
        if not response:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        results.append(
            (
                version_link,
                find_tag(soup, 'h1').text,
                soup.find('dl').text.replace('\n', ' ')
            )
        )
    return results


def latest_versions(session):
    session = requests_cache.CachedSession()
    response = get_response(session, MAIN_DOC_URL)
    if not response:
        return
    for ul in BeautifulSoup(response.text, 'lxml').find(
        'div',
        {'class': 'sphinxsidebarwrapper'}
    ).find_all('ul'):
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Не найден список c версиями Python')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    for a_tag in a_tags:
        text_match = re.search(
            r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)',
            a_tag.text,
        )
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
    response = get_response(session, downloads_url)
    if not response:
        return
    archive_url = urljoin(
        downloads_url,
        find_tag(
            find_tag(BeautifulSoup(response.text, 'lxml'), 'table'),
            'a',
            attrs={'href': re.compile(r'.+pdf-a4\.zip$')},
        )['href']
    )
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / archive_url.split('/')[-1]
    with open(archive_path, 'wb') as file:
        file.write(session.get(archive_url).content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, PEPS_URL)
    if not response:
        return
    tr_tags = find_tag(
        find_tag(
            BeautifulSoup(response.text, 'lxml'),
            'section',
            {'id': 'numerical-index'},
        ),
        'tbody',
    ).find_all('tr')
    results = {}
    total = 0
    for tr_tag in tqdm(tr_tags):
        link = urljoin(
            PEPS_URL,
            find_tag(tr_tag, 'a')['href']
        )
        response = get_response(session, link)
        if not response:
            continue
        status = find_tag(
            BeautifulSoup(response.text, 'lxml'),
            'dl',
            {'class': 'rfc2822 field-list simple'},
        ).select_one(':-soup-contains("Status") + dd').string
        preview_status = EXPECTED_STATUS.get(find_tag(tr_tag, 'td').text[1:])
        if status not in preview_status:
            logging.warning(
                f'Несовпадающие статусы: {link}\n'
                f'Статус в карточке: {status}\n'
                f'Ожидаемый статус: {preview_status[0]}.'
            )
        results[status] = results.get(status, 0) + 1
        total += 1
    return (
        [('Статус', 'Количество')]
        + sorted(results.items())
        + [('Total', total)]
    )


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    args = configure_argument_parser(MODE_TO_FUNCTION.keys()).parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
