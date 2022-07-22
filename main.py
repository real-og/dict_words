from db import *
from LyricsParser import LyricsParser
import time

while True:
    url = input("Enter url to Genius lyrics you want to fully insert: ")
    start = time.time()
    count_before = get_words_count()
    words = LyricsParser(url).get_word_list()
    add_words(words)
    print('The text contains', len(words), 'words')
    print('It took', '%.3f' % (time.time() - start), 'seconds to add', get_words_count() - count_before, 'words')


