import logging
import re
from collections import deque
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import (LOG_FORMAT_STATUS, configure_argument_parser,
                     configure_logging)
from constants import BASE_DIR, MAIN_DOC_URL, PEP_URL
from outputs import control_output
from utils import find_tag, find_tags, get_response

def whats_new(session):
    '''Парсинг версий, названия и автора.'''
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
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        versilon_link = urljoin(whats_new_url, href)
        response = get_response(session, versilon_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((versilon_link, h1.text, dl_text))
    return results

def latest_versions(session):
    '''Парсинг версий и ссылки на них.'''
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
    '''Загружает архив с документацией Python в формате PDF A4.'''
    downloads_dir = BASE_DIR / 'downloads'
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    soup = BeautifulSoup(response.text, features='lxml')
    table_tag = find_tag(soup, tag='table', attrs={"class": "docutils"})
    pdf_a4_tag = find_tag(table_tag, tag='a', attrs={'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_link = pdf_a4_tag['href']
    urlpdf = urljoin(downloads_url, pdf_link)
    filename=urlpdf.split('/')[-1]
    downloads_dir.mkdir(exist_ok=True)
    pdf_path=downloads_dir / filename
    response = session.get(urlpdf)
    with open(pdf_path, 'wb') as f:
        f.write(response.content)
    logging.info('Архив был загружен и сохранён: %s', pdf_path)

def pars_tr(session):
    '''Парсинг тегов tr для статусов PEP.'''
    response = get_response(session, PEP_URL)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    tables = soup.find_all('table')
    all_rows = []
    for table in tables[:-1]:
        rows = table.find_all('tr')
        all_rows.extend(rows)
    return all_rows

def abbr(session):
    '''Получаем все теги abbr.'''
    rows = pep(session)
    abbr_list = []
    for row in rows:
        abbr_tag = row.find('abbr')
        if abbr_tag and abbr_tag.has_attr('title'):
            abbr_list.append(abbr_tag['title'])
    return abbr_list

def link(session):
    '''Получаем ссылки.'''
    row = pep(session)
    list_links = []
    for links in row:
        urllink = links.find('a', class_='pep reference internal')
        if urllink and urllink.text.isdigit():
            href = urllink['href']
            fullurl = urljoin(PEP_URL, href)
            list_links.append(fullurl)
    return list_links

def pep(session):
    '''Получаем все статусы переходя по ссылкам и сравниваем с ожидаемыми.'''
    status_list = deque(abbr(session))
    peplink = link(session)
    actlink = acclink = drlink = dlink = flink = plink = rlink = slink = wlink = 0
    results = [('Статус', 'Количество')]
    status_pep = ['Active',
                  'Accepted',
                  'Deferred',
                  'Draft',
                  'Final',
                  'Provisional',
                  'Rejected',
                  'Superseded',
                  'Withdrawn',
                  'Total']
    count = []
    for links in tqdm(peplink, desc='Проверка'):
        response = session.get(links)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        real_status = None
        for dt in soup.find_all('dt'):
            if dt.get_text(strip=True).startswith('Status'):
                dd = dt.find_next_sibling('dd')
                if dd:
                    real_status = dd.text.strip()
                break
        if status_list and real_status:
            expected_raw = status_list.popleft()
            expected_list = [s.strip() for s in expected_raw.split(',')]
            if real_status not in expected_list:
                logging.info(LOG_FORMAT_STATUS,
                             links, real_status,
                             status_list[0] if status_list else 'отсутствует'
                )
            if real_status == status_pep[0]:
                actlink += 1
            elif real_status == status_pep[1]:
                acclink += 1
            elif real_status == status_pep[2]:
                dlink += 1
            elif real_status == status_pep[3]:
                drlink += 1
            elif real_status == status_pep[4]:
                flink += 1
            elif real_status == status_pep[5]:
                plink += 1
            elif real_status == status_pep[6]:
                rlink += 1
            elif real_status == status_pep[7]:
                slink += 1
            elif real_status == status_pep[8]:
                wlink += 1
        else:
            logging.info(LOG_FORMAT_STATUS,
                         links, real_status,
                         status_list[0] if status_list else 'отсутствует'
                )
            if real_status == status_pep[0]:
                actlink += 1
            elif real_status == status_pep[1]:
                acclink += 1
            elif real_status == status_pep[2]:
                dlink += 1
            elif real_status == status_pep[3]:
                drlink += 1
            elif real_status == status_pep[4]:
                flink += 1
            elif real_status == status_pep[5]:
                plink += 1
            elif real_status == status_pep[6]:
                rlink += 1
            elif real_status == status_pep[7]:
                slink += 1
            elif real_status == status_pep[8]:
                wlink += 1
            count.extend([actlink, acclink, drlink, dlink, flink, plink, rlink, slink, wlink])
    for status, value in zip(status_pep, count):
        results.append((status, value))
    results.append(('total', sum(count)))
    return results

MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}

def main():
    '''Основная функция.'''
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
