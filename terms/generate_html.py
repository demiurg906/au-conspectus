import json
import lxml.html
import os
import regex
import requests
import sys

from lxml.cssselect import CSSSelector
from textile import textile

WIKI_SEARCH_URL_TEMPLATE = 'https://ru.wikipedia.org/w/index.php?search={}&title=Служебная:Поиск&profile=default&fulltext=1'
NEERC_SEARCH_URL_TEMPLATE = 'https://neerc.ifmo.ru/wiki/index.php?title=%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F%3ASearch&profile=advanced&search={}&fulltext=Search&ns0=1&redirs=1&profile=advanced'


def convert_encoding(s):
    return s.encode('ISO-8859-1', 'ignore').decode('utf-8')


def search_wiki(term: str):
    """
    находит ссылку на страницу в вики
    :param term: термин
    :return: title, url
    """
    url = WIKI_SEARCH_URL_TEMPLATE.format(term)
    try:
        resp = requests.get(url)
    except requests.ConnectionError:
        # TODO: написать в лог
        return None
    if resp.status_code != 200:
        return None
    tree = lxml.html.fromstring(resp.content)
    finded_sel = CSSSelector('.mw-search-results')
    finded = finded_sel(tree)
    if finded:
        # поиск что-то нашел, выбираем первую ссылку
        el = finded[0]
        # TODO: проверить, что нашли то, что нужно
        page = CSSSelector('div.mw-search-result-heading a')(el)[0]
        ref = 'https://ru.wikipedia.org' + page.attrib['href']
        title = page.attrib['title']
        return title, ref
    else:
        return None


def get_wiki_info(term: str):
    """
    находит информацию по термину в вики
    :return: словарь с инфо о странице:
             заголовок, адрес, текст и html для превью
    """
    info = search_wiki(term)
    if info is None:
        return None
    title, base_url = info

    url = f'https://ru.wikipedia.org/api/rest_v1/page/summary/{title}'
    try:
        resp = requests.get(url)
    except requests.ConnectionError:
        # TODO: написать в лог
        return None
    if resp.status_code != 200:
        return None
    data = json.loads(resp.text)

    def delete_key(data, key: str):
        try:
            del data[key]
        except KeyError:
            pass

    delete_key(data, 'displaytitle')
    delete_key(data, 'pageid')
    delete_key(data, 'dir')
    delete_key(data, 'lang')
    delete_key(data, 'timestamp')
    delete_key(data, 'originalimage')

    if 'thumbnail' in data:
        delete_key(data['thumbnail'], 'original')

    data['wiki_url'] = base_url
    return data


def search_neerc(term: str):
    """
    находит ссылку на страницу на neerc.ifmo
    :param term: термин
    :return: title, url
    """
    url = NEERC_SEARCH_URL_TEMPLATE.format(term)
    try:
        resp = requests.get(url)
    except requests.ConnectionError:
        # TODO: написать в лог
        return None
    if resp.status_code != 200:
        return None
    tree = lxml.html.fromstring(resp.content)
    finded_sel = CSSSelector('.mw-search-results')
    finded = finded_sel(tree)
    if finded:
        # поиск что-то нашел, выбираем первую ссылку
        el = finded[0]
        # TODO: проверить, что нашли то, что нужно
        page = CSSSelector('div.mw-search-result-heading a')(el)[0]
        ref = 'https://neerc.ifmo.ru' + page.attrib['href']
        title = convert_encoding(page.attrib['title'])
        return title, ref
    else:
        return None


def get_neerc_info(term: str):
    """
    находит информацию по термину в вики
    :return: словарь с инфо о странице:
             заголовок, адрес, текст и html для превью
    """
    info = search_neerc(term)
    if info is None:
        return None
    title, base_url = info

    # TODO: проверить, что работает на страницах без определений
    def get_text():
        url = f'{base_url}&action=edit'
        try:
            resp = requests.get(url)
        except requests.ConnectionError:
            # TODO: написать в лог
            return None
        if resp.status_code != 200:
            return None
        tree = lxml.html.fromstring(resp.content)
        el = CSSSelector('#wpTextbox1')(tree)[0]
        text = convert_encoding(el.text)

        def process_text(text: str):
            res = []
            buf = ''
            step = 0
            for c in text:
                if step == 0:
                    if c != '|':
                        res.append(c)
                    else:
                        step = 1
                elif step == 1:
                    buf += c
                    if 'definition =' in buf:
                        step = 2
                else:
                    res.append(c)
            res = ''.join(res)
            res = regex.sub(r'<tex.*?>|</tex>', '$', res)
            res = regex.sub(r'\[.*?\||\]', '', res)
            res = regex.sub(r'|.?|definition\s*=', '', res)
            res = res.replace('{{---}}', '—')
            res = res.replace('*', '* ')
            res = regex.sub(r"'''\s*(.*?)\s*'''", ' *\g<1>* ', res)
            return res

        preview_text = process_text(regex.findall(r'{{((?>[^{}]+|(?R))*)}}', text)[0].strip())
        preview_text = f"{regex.findall(r'==.+?==', text)[0].strip()}\n{preview_text}"

        preview_html = textile(preview_text).replace('<strong', '<b').replace('</strong', '</b')
        return preview_text, preview_html

    def get_thumbnail():
        try:
            resp = requests.get(base_url)
        except requests.ConnectionError:
            # TODO: написать в лог
            return None
        if resp.status_code != 200:
            return None
        tree = lxml.html.fromstring(resp.content)
        thumbnails = CSSSelector('img.thumbimage')(tree)
        if thumbnails is None:
            return None
        thumbnail = thumbnails[0]
        args = thumbnail.attrib
        data = {
            'source': 'https://neerc.ifmo.ru' + args['src'],
            'width': args['width'],
            'height': args['height']
        }
        return data

    text, html = get_text()
    data = {
        'title': title,
        'wiki_url': base_url,
        'extract': text,
        'extract_html': html
    }

    thumbnail = get_thumbnail()
    if thumbnail is not None:
        data['thumbnail'] = thumbnail
    return data


def get_info(term: str):
    wiki_info = get_wiki_info(term)
    neerc_info = get_neerc_info(term)
    res = {}
    if wiki_info is not None:
        res['wiki'] = wiki_info
    if neerc_info is not None:
        res['neerc'] = neerc_info
    return res


# def get_terms(input_folder):
def get_terms(filename):
    with open(filename) as f:
        return json.load(f)
    # res = set()
    # for file in os.listdir(input_folder):
    #     if file.endswith('.json'):
    #         res.update(json.load(open(file)))
    # return res


# def generate_terms_info(input_folder='./'):
def generate_terms_info(filename):
    """
    дописывает информацию он новых терминах из
    `get_terms` в индекс
    """
    data = {}
    # for term in get_terms(input_folder):
    for term in get_terms(filename):
        if term in data:
            continue
        info = get_info(term)
        if info:
            data[term] = info
            print(f'info about "{term}" added')
    return json.dumps(data)


def generate_htmls(input_folder='./', template_name='template.html'):
    files = [file for file in os.listdir(input_folder) if file.endswith('.html')]
    with open(template_name) as f:
        template = ''.join(f.readlines())
    template.replace('{{ content }}', '{}\n<script>\nvar terms = {};\n</script>')
    for file in files:
        with open(file) as f:
            content = ''.join(f.readlines())

        terms_file = file.replace('.html', '.json')
        terms_json = generate_terms_info(terms_file)
        res_file = file.replace('.html', '.valid.html')
        with open(res_file, 'w') as f:
            res_content = template.format(content, terms_json)
            f.write(res_content)
        print(f'{res_file} generated')


def main():
    generate_htmls()



if __name__ == '__main__':
    main()
