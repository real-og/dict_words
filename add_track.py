from db import *
from LyricsParser import LyricsParser
import time

def add_track(url):
    words = LyricsParser(url).get_word_list()
    add_words(words)
    return len(words)
    

