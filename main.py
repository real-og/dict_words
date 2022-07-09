import requests
from bs4 import BeautifulSoup

#url = 'https://genius.com/Kendrick-lamar-dna-lyrics'
url = 'https://genius.com/Slowthai-adhd-lyrics'
page = requests.get(url)
soup = BeautifulSoup(page.text, "html.parser")

lines = soup.findAll(class_="Lyrics__Container-sc-1ynbvzw-6 YYrds")

for i in lines:
    s = i.get_text('\n')
    print(s, len(s))
