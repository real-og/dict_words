import requests
from bs4 import BeautifulSoup
import re


class LyricsParser:

    def __init__(self, url):
        self.url = url
        try:
            self.page = requests.get(url)
            self.soup = BeautifulSoup(self.page.text, "html.parser")
        except Exception as e:
            print(e)
            self.page = 'bam'
            self.soup = BeautifulSoup('bang', "html.parser")
        self.lyrics_blocks = self.soup.findAll(class_="Lyrics__Container-sc-1ynbvzw-6 YYrds")

    def get_word_list(self):
        words = list()
        for block in self.lyrics_blocks:
            words = words + re.findall('[’a-z$\'-]+', block.get_text('\n').lower())
        return words

    # def get_word_set(self):
    #     uniq_words = set()
    #     for block in self.lyrics_blocks:
    #         uniq_words |= set(re.findall('[’a-z$\']+', block.get_text('\n').lower()))

# url = 'https://genius.com/Kendrick-lamar-dna-lyrics'
# url = 'https://genius.com/Slowthai-adhd-lyrics'

