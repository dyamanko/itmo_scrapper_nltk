from urllib.request import urlopen
from bs4 import BeautifulSoup
from collections import Counter
from wordcloud import WordCloud

import matplotlib.pyplot as plt
import nltk

# поисковый запрос на сайте habr.com. параметры: number - номер страницы, search - текст поискового запроса
list_url = "https://habr.com/ru/search/page{number}/?q={search}&target_type=posts&order=relevance"

# текст поискового запроса
search_text = "NFT"

# кол-во страниц
max_page_number = 1

# номер стартовой страницы
page_number = 1

# общий текст собранных статей
article_text = ''
article_tags = []

while page_number <= max_page_number:
    # поисковый запрос. search - текст запроса, number - номер страницы
    url = list_url.format(number=page_number, search=search_text)
    search_bs = BeautifulSoup(urlopen(url).read(), 'html.parser')
    # search_bs.findAll('article') список статей из результата поиска
    for article in search_bs.findAll('article'):
        # ссылка на статью из заголовка
        article_link = 'https://habr.com' + article.h2.a['href']
        article_soap = BeautifulSoup(urlopen(article_link).read(), 'html.parser')
        # текст статьи
        article_text += article_soap.find('div', {'id': 'post-content-body'}).getText()
        # теги статьи
        article_tags_text = article_soap.find('div', {'class': 'tm-separated-list tm-article-presenter__meta-list'})
        article_tags.extend([tag.getText().lower() for tag in article_tags_text.find_all("li")])
    page_number += 1

# Выделение ключевых терминов.
print(Counter(article_tags))

# Облако тегов
wordcloud = WordCloud().generate(' '.join(article_tags))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()

# Выделение ключевых персонажей (тренд-сеттеров, "игроков"), публикующих материалы и выступающих на конференциях.

from natasha import (
    Segmenter,
    MorphVocab,

    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,

    PER,
    NamesExtractor,

    Doc
)

segmenter = Segmenter()
morph_vocab = MorphVocab()

emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)

names_extractor = NamesExtractor(morph_vocab)

# создаем документ из текстов статей
doc = Doc(article_text)
doc.segment(segmenter)
doc.tag_morph(morph_tagger)
doc.parse_syntax(syntax_parser)

# тэгируем текст
doc.tag_ner(ner_tagger)

# нормализуем текст
for span in doc.spans:
    span.normalize(morph_vocab)

# вывод списка ключевых лиц
for span in doc.spans:
    if span.type == PER:
        span.extract_fact(names_extractor)

# список ключевых лиц
persons = {_.normal: _.fact.as_dict for _ in doc.spans if _.fact}

# рейтинг ключевых лиц
print(Counter(persons.keys()))
