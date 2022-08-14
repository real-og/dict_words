from db import add_word_to_user

# Adds words to a user from file like a1.txt, or a2.txt
# Returns the number of added words
def init_user(id_tg, filename):
    with open(filename, 'r') as f:
        words = f.read().split()
        for word in words:
            add_word_to_user(id_tg, word)
    return len(words)