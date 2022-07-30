from db import *
from LyricsParser import LyricsParser
import time

def add_track(url):
    words = LyricsParser(url).get_word_list()
    add_words(words)
    return len(words)
    

if __name__ == '__main__':    
    while True:
        url = input("Введите адрес на джиниус: ")
        count_before = get_words_count()
        print("В песне " + str(add_track(url)) + " слов")
        print("Добавлено " + str(get_words_count() - count_before))
