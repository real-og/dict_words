from db import add_words_to_user

# Adds words to a user from file like a1.txt, or a2.txt
# Returns the number of added words
def init_user_dict(id_tg, filename):
    with open('words_to_init/' + filename, 'r') as f:
        words = f.read().split()
        add_words_to_user(id_tg=id_tg, words=words)
    return len(words)
