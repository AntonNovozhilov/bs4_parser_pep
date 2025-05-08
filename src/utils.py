import logging

from requests import RequestException

from exceptions import ParserFindTagException


def get_response(session, url):
    '''Выполняет GET-запрос к указанному URL.'''
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception('Возникла ошибка при загрузке страницы %s', url)
        return None

def find_tag(soup, tag, attrs=None):
    '''Ищет один тег в объекте BeautifulSoup.'''
    searched_tag = soup.find(tag, attrs=(attrs or{}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag

def find_tags(soup, tag, attrs=None):
    '''Ищет все теги заданного типа и атрибутов в объекте BeautifulSoup.'''
    searched_tag = soup.find_all(tag, attrs=(attrs or{}))
    if searched_tag is None:
        error_msg = f'Не найдены теги {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
