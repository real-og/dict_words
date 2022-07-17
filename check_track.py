from db import *
from LyricParser import LyricsParser

url = input("Enter url to Genius lyrics you want to check: ")
words = LyricsParser(url).get_word_list()


print("Do you know this word? y/n")
unknown = list()
for word in words:
    if check_word(word):
        continue
    print(word)
    ans = input("y/n")
    if ans == 'y':
        add_word(word)
    else:
        unknown.append(word)

print('Words to learn:')
print(unknown)




