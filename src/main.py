import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import (LOG_FORMAT_STATUS, configure_argument_parser,
                     configure_logging)
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_URL
from outputs import control_output
from utils import find_tag, find_tags, get_response


def whats_new(session):
    """Парсинг версий, названия и автора."""
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    stap3 = find_tags(div_with_ul, 'li', attrs={'class': 'toctree-l1'})
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(stap3):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))
    return results


def latest_versions(session):
    """Парсинг версий и ссылки на них."""
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        math = re.search(pattern, a_tag.text)
        if math:
            version = math.group(1)
            status = math.group(2)
            links = a_tag['href']
            results.append((links, version, status))
        else:
            version = a_tag.text
    return results


def download(session):
    """Загружает архив с документацией Python в формате PDF A4."""
    downloads_dir = BASE_DIR / 'downloads'
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response:
        soup = BeautifulSoup(response.text, features='lxml')
        table_tag = find_tag(soup, tag='table', attrs={"class": "docutils"})
        pdf_a4_tag = find_tag(
            table_tag, tag='a',
            attrs={'href': re.compile(r'.+pdf-a4\.zip$')}
        )
        pdf_link = pdf_a4_tag['href']
        urlpdf = urljoin(downloads_url, pdf_link)
        filename = urlpdf.split('/')[-1]
        downloads_dir.mkdir(exist_ok=True)
        pdf_path = downloads_dir / filename
        response = get_response(session, urlpdf)
        if response:
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            logging.info('Архив был загружен и сохранён: %s', pdf_path)
        logging.exception('Ошибка при выполнении функции download.\n'
                          'Проверьте ссылу на документ.')
    return None


def pars_tr(session):
    """Парсинг тегов tr для статусов PEP."""
    response = get_response(session, PEP_URL)
    if response:
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        tables = soup.find_all('table')
        return tables


def abbr(session):
    """Получаем все теги abbr."""
    tables = pars_tr(session)
    abbr_list = []
    for table in tables[:-1]:
        try:
            abbr_tag = find_tags(table, 'abbr')
            for tag in abbr_tag:
                if tag and tag.text:
                    abbr_list.append(tag.text[1:])
        except Exception:
            continue
    abbr_list.append('""')
    return abbr_list


def link(session):
    """Получаем ссылки."""
    tables = pars_tr(session)
    list_links = []
    for table in tables:
        try:
            a_tag = find_tags(table, tag='a')
            for a in a_tag:
                if a and a.text.isdigit():
                    href = a['href']
                    fullurl = urljoin(PEP_URL, href)
                    list_links.append(fullurl)
        except Exception:
            continue
    return list_links


def get_real_status(session, url):
    """Получаем статус с страницы PEP."""
    response = get_response(session, url)
    if response:
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        for dt in soup.find_all('dt'):
            if dt.get_text(strip=True).startswith('Status'):
                dd = dt.find_next_sibling('dd')
                if dd:
                    return dd.text.strip()
        return None
    return None


def pep(session):
    """Получаем все статусы переходя по ссылкам и сравниваем с ожидаемыми."""
    status_list = abbr(session)
    peplink = link(session)
    results = [('Статус', 'Количество')]
    status_counter = {status: 0 for status in EXPECTED_STATUS}
    loggind_list = []
    for i, links in enumerate(tqdm(peplink, desc='Проверка')):
        real_status = get_real_status(session, links)
        current_status = status_list[i]
        valid_statuses = EXPECTED_STATUS.get(current_status, ())
        if real_status in valid_statuses:
            status_counter[current_status] += 1
        else:
            loggind_list.append(
                LOG_FORMAT_STATUS.format(
                    links,
                    real_status,
                    valid_statuses if status_list else 'отсутствует'
                )
            )
            found = False
            for key, valid_values in EXPECTED_STATUS.items():
                if real_status in valid_values:
                    status_counter[key] += 1
                    found = True
                    break
            if not found:
                status_counter.setdefault(real_status, 0)
                status_counter[real_status] += 1
    if loggind_list:
        logging.info('\n'.join(loggind_list))
    results.extend(status_counter.items())
    results.append(('Total', sum(status_counter.values())))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    """Основная функция."""
    configure_logging()
    logging.info('Парсер запущен')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info('Аргументы командной строки %s', args)
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results:
        control_output(results, args)
    logging.info('Парсер завершил свою работу')


if __name__ == '__main__':
    main()
