import requests
from bs4 import BeautifulSoup
import string
import re

# url = 'https://genius.com/Kendrick-lamar-dna-lyrics'
url = 'https://genius.com/Slowthai-adhd-lyrics'
page = requests.get(url)
soup = BeautifulSoup(page.text, "html.parser")

words = list()
uniq_words = set()
lyrics_blocks = soup.findAll(class_="Lyrics__Container-sc-1ynbvzw-6 YYrds")

for block in lyrics_blocks:
    uniq_words |= set(re.findall('[’a-zа-яё\']+', block.get_text('\n').lower()))

for block in lyrics_blocks:
    words = words + re.findall('[’a-zа-яё\']+', block.get_text('\n').lower())

# problem with connected - like "dec--"
# words = [word.strip(string.punctuation).lower() for word in lyrics.split()]



