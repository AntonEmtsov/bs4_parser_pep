from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException

ERROR_TAG = 'Не найден тег {tag} {attrs}'
RESPONSE_ERROR = 'Возникла ошибка при загрузке страницы {url}'


def get_soup(session, url, features='lxml'):
    return BeautifulSoup(get_response(session, url).text, features)


def get_response(session, url, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException:
        raise ConnectionError(RESPONSE_ERROR.format(url=url))


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs={} if attrs is None else attrs)
    if searched_tag is None:
        raise ParserFindTagException(ERROR_TAG.format(tag=tag, attrs=attrs))
    return searched_tag
