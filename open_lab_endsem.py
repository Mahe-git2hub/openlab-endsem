# -*- coding: utf-8 -*-
"""open-lab-endsem.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PouihWWeJX7V-g7OHHf3N-rw5NU7lrr2
"""

# Commented out IPython magic to ensure Python compatibility.
# %%bash
# mkdir openlab
# cp /content/drive/'My Drive'/'end sem_openlab' -r /content/openlab/
# ls

# !pip install flask-ngrok

from flask_ngrok import run_with_ngrok

import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm

nlp = en_core_web_sm.load()
from pprint import pprint

from pathlib import Path
import os
from bs4 import BeautifulSoup
import requests
import re
from flask import Flask, render_template, request, flash, redirect, url_for
from wordcloud import WordCloud
from werkzeug.wrappers import Request, Response
import matplotlib.pyplot as plt
import socket

import nltk
import threading
from nltk.corpus import stopwords

nltk.download('stopwords')

link1 = 'https://www.thehindu.com/news/national/centre-may-raise-loan-to-pay-shortfall-of-gst-compensation-amount' \
        '/article31329841.ece?homepage=true '
link2 = 'https://www.thehindu.com/news/national/several-union-ministers-officials-return-to-work-at-ministries' \
        '/article31329079.ece?homepage=true '
link3 = 'https://www.thehindu.com/news/national/plea-to-bring-back-to-punjab-stranded-sikh-pilgrims/article31329103' \
        '.ece?homepage=true '

app = Flask(__name__)
run_with_ngrok(app)  # Start ngrok when app is run

print('Socket : \t', socket.gethostbyname(socket.getfqdn(socket.gethostname())))

stop_words = set(stopwords.words("english"))
new_stopwords = ['Hindu', 'Subscribe Now', 'free trial', 'Subscription', 'Subscribe']
stop_words = stop_words.union(new_stopwords)


@app.route('/url_to_string/<url_to_scrape>', methods=['GET'])
def url_to_string(url_to_scrape):
    res = requests.get(url_to_scrape)
    html = res.text
    soup = BeautifulSoup(html, 'html5lib')
    for script in soup(["script", "style", 'aside']):
        script.extract()
    return " ".join(re.split(r'[\n\t]+', soup.get_text()))


def string_to_nlp(s: str):
    return nlp(s)


art = url_to_string(link2)
article = nlp(art)
print(article.ents)

print(len(string_to_nlp(url_to_string(link3))))

labels = [x.label_ for x in article.ents]
print(Counter(labels))

items = [x.text for x in article.ents]
print(Counter(items).most_common(15))

sentences = [x for x in article.sents]
# any sentence can be selected randomly
sent_num = 10
print(sentences[sent_num])

displacy.render(nlp(str(sentences[sent_num])), jupyter=True, style='ent')


# displacy.render(nlp(str(sentences[sent_num])), jupyter=True, style='ent')
#
# displacy.render(nlp(str(sentences[sent_num])), style='dep', jupyter = True, options = {'distance': 70})
# sentence and its dependencies
@app.route('/pos', defaults={'pos_article': link3, 'sent_nums': 10})
@app.route('/pos/<string:pos_article>/<int:sent_nums>', methods=['GET'])
def PartsofSpeech(pos_article, sent_nums=10):
    sentences_pos = [x for x in pos_article.sents]
    # any sentence can be selected randomly default is 10
    svg = displacy.render(nlp(str(sentences_pos[sent_nums])), style='dep', jupyter=False, options={'distance': 70})
    output_path = Path(os.path.join("./", "sentence.svg"))
    output_path.open('w', encoding="utf-8").write(svg)
    # sentence and its dependencies
    return None


@app.route('/NER/<ner_article>', methods=['GET'])
def NER(ner_article):
    return displacy.render(ner_article, style='ent', jupyter=False)


#
# doc1 = nlp("This is a sentence.")
# doc2 = nlp("This is another sentence.")
# html = displacy.render([doc1, doc2], style="dep", page=True)
#
# # pprint(html)


# displacy.render(ner_article, jupyter=True, style='ent')
#
# doc1 = nlp("This is a sentence.")
# doc2 = nlp("This is another sentence.")
# html = displacy.render([doc1, doc2], style="dep", page=True)

# wordcloud = WordCloud(width=8000, height=8000, background_color='white', min_font_size=10,
#                       stopwords=stop_words).generate(url_to_string(link1))
# plt.figure(figsize=(20, 28), facecolor=None)
# plt.imshow(wordcloud)
# plt.axis("off")
# plt.tight_layout(pad=0)
#
# plt.show()


@app.route('/wcloud/<wc_article>')
def wc(wc_article):
    wordcloud = WordCloud(width=8000, height=8000, background_color='white', min_font_size=10,
                          stopwords=stop_words).generate(wc_article)
    plt.figure(figsize=(20, 28), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig('wordcloud.png', dpi='figure')
    plt.show()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        url = request.form.get('News article URL')
        print(url)
        string_content_url = url_to_string(str(url))
        nlp_content = string_to_nlp(string_content_url)
        print('nlp content: ', nlp_content)
        return redirect(url_for('PartsofSpeech'))


if __name__ == '__main__':
    print("Use the following links if don't have any :\n", link1, '\n', link2, '\n', link3)
    # print(eval_js("google.colab.kernel.proxyPort(5000)"))
    app.run()
