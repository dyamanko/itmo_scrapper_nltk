from urllib.request import urlopen
from bs4 import BeautifulSoup
from collections import Counter
import re
import nltk

# поисковый запрос на сайте habr.com. параметры: number - номер страницы, search - текст поискового запроса
list_url = "https://habr.com/ru/search/page{number}/?q={search}&target_type=posts&order=relevance"

# текст поискового запроса
search_text = "javascript"

# кол-во страниц
max_page_number = 2

# номер стартовой страницы
page_number = 1


class Article:
    def __init__(self, code):
        # текст статьи
        self.text = code.find('div', { 'id' : 'post-content-body' }).getText()
        # автор статьи(удаляем лишние пробелы/отступы)
        raw_author = code.find('a', {'class': 'tm-user-info__username'}).getText()
        self.author = re.sub(r"[\n\t\s]* +", " ", raw_author)


def get_text_tags(text):
    tokens = nltk.word_tokenize(text)
    return nltk.pos_tag(tokens)


# список полученных данных статей
article_list = []

while page_number <= max_page_number:
    url = list_url.format(number=page_number, search=search_text)
    html = urlopen(url)
    bs = BeautifulSoup(html.read(), 'html.parser')
    # bs.findAll('article') список статей из результата поиска
    for article in bs.findAll('article'):
        # ссылка на статью из заголовка
        article_link = 'https://habr.com' + article.h2.a['href']
        article_html = urlopen(article_link)
        article_soap = BeautifulSoup(article_html.read(), 'html.parser')
        article_list.append(Article(article_soap))
    page_number += 1

