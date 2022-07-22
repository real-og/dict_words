import requests
from bs4 import BeautifulSoup
import re


class LyricsParser:

    def __init__(self, url):
        self.url = url
        self.page = requests.get(url)
        self.soup = BeautifulSoup(self.page.text, "html.parser")
        self.lyrics_blocks = self.soup.findAll(class_="Lyrics__Container-sc-1ynbvzw-6 YYrds")

    def get_word_list(self):
        words = list()
        # problem with connected - like "dec--"
        # words = [word.strip(string.punctuation).lower() for word in lyrics.split()]
        for block in self.lyrics_blocks:
            words = words + re.findall('[’a-zа-яё\'-]+', block.get_text('\n').lower())
        return words

    def get_word_set(self):
        uniq_words = set()
        for block in self.lyrics_blocks:
            uniq_words |= set(re.findall('[’a-zа-яё\']+', block.get_text('\n').lower()))

# url = 'https://genius.com/Kendrick-lamar-dna-lyrics'
# url = 'https://genius.com/Slowthai-adhd-lyrics'

