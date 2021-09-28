import re

from bs4 import BeautifulSoup
import os
import requests


def bool_price(article):
    url = 'https://630630.ru/magazin/search/result'
    data = {
        'setsearchdata': 1,
        'category_id': 0,
        'search_type': 'any',
        'search': article,
    }
    html = requests.post(url, data=data).text
    soup = BeautifulSoup(html, 'html.parser')
    in_stock = soup.find_all(class_=re.compile('stock$'))
    paragraphs = []
    for x in in_stock:
        paragraphs.append(str(x.string))
    print(paragraphs[0])
    if paragraphs[0] == 'В наличии':
        return True
    else:
        if paragraphs[0] == 'Нет в наличии':
            return False


if __name__ == '__main__':
    print(bool_price(111981))