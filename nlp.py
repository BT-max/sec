import re

import nltk
import seaborn

nltk.download('stopwords')
nltk.download('wordnet')


def analyse_text(text, year, ticker):
    tokens = re.findall(r'\w+', text)
    filtered_tokens = []
    for token in tokens:
        token = token.lower()
        stop_words = nltk.corpus.stopwords.words('english')
        if token not in stop_words:
            filtered_tokens.append(token)
    seaborn.set_style('whitegrid')
    text_frequencies = nltk.FreqDist(filtered_tokens)
    text_frequencies.plot(10, title=f'Word Frequencies of {ticker} for {year}')
