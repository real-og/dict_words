import psycopg2
import os


class Database(object):
    def __init__(self):
        self.conn = psycopg2.connect(
            database=str(os.environ.get('database')),
            user=str(os.environ.get('user')),
            password=str(os.environ.get('password')),
            host=str(os.environ.get('host')),
            port=str(os.environ.get('port'))
        )
        self.curs = self.conn.cursor()

    def __enter__(self):
        return self.curs

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()

# WORDS IN GENERAL
def get_all_words():
    with Database() as curs:
        _SQL = """SELECT word FROM words ORDER BY word;"""
        curs.execute(_SQL)
        return curs.fetchall()

def get_words_count():
    with Database() as curs:
        _SQL = """SELECT count(*) FROM words;"""
        curs.execute(_SQL)
        return curs.fetchall()[0][0]

def add_words(words):
# Too slow
#   for word in words:
#       add_word(word)
    with Database() as curs:
        _SQL = """INSERT INTO words (word) VALUES"""
        for word in words:
            word = word.replace("`", "'").replace("’", "'")
            _SQL = _SQL + " ($$" + word + "$$), "
        _SQL = _SQL[:-2] + ' ON CONFLICT (word) DO NOTHING;'
        curs.execute(_SQL)


# A WORD IN GENERAL
def check_word(word):
    word = word.replace("`", "'").replace("’", "'")
    with Database() as curs:
        _SQL = "SELECT word FROM words WHERE word = $$" + word + "$$;"
        curs.execute(_SQL)
        if len(curs.fetchall()) == 0:
            return False
        return True

def add_word(word):
    with Database() as curs:
        word = word.replace("`", "'").replace("’", "'")
        _SQL = "INSERT INTO words (word) VALUES ($$" + word + "$$) ON CONFLICT (word) DO NOTHING;"
        curs.execute(_SQL)


# WORDS CONNECTED TO THE USER
def get_words_by_user(id_tg, table='user_word'):
    with Database() as curs:
        _SQL = """select word
                    from """ + table + """ inner join words
                    on """ + table + """.user_id = (select id from users where id_tg = """ + str(id_tg) + """)
                    and """ + table + """.word_id = words.id order by word;"""
        curs.execute(_SQL)
        return [tupl[0] for tupl in curs.fetchall()]
        #return curs.fetchall()

def get_words_count_by_user(id_tg, table='user_word'):
    with Database() as curs:
        _SQL = """select count(*)
                    from """ + table + """ where
                    user_id = (select id from users where id_tg = """+str(id_tg)+""");"""
        curs.execute(_SQL)
        return curs.fetchall()[0][0]

def add_words_to_user(id_tg, words, table='user_word'):
    with Database() as curs:
        dbid = str(get_user_dbid(id_tg))
        add_words(words)
        _SQL = """INSERT INTO """ + table + """ (user_id, word_id) values """
        for word in words:
            word = word.replace("`", "'").replace("’", "'")
            _SQL = _SQL + "(" + dbid + ", (select id from words where word =$$" + word + "$$)), "
        _SQL = _SQL[:-2] + ' ON CONFLICT DO NOTHING;'
        curs.execute(_SQL)


# A WORD CONNECTED TO THE USER
def delete_word_by_user(id_tg, word, table='user_word'):
    with Database() as curs:
        word = word.replace("`", "'").replace("’", "'")
        _SQL = """delete from """ + table + """ where
                    user_id = (select id from users where id_tg = """ + str(id_tg) + """)
                    and word_id = (select id from words where word = $$""" + word + """$$);"""
        curs.execute(_SQL)

def check_word_by_user(id_tg, word, table='user_word'):
    with Database() as curs:
        word = word.replace("`", "'").replace("’", "'")
        _SQL = """select * from """ + table + """ where 
                    user_id = (select id from users where id_tg = """ + str(id_tg) + """)
                    and word_id = (select id from words where word = $$""" + word + """$$);"""
        curs.execute(_SQL)
        if len(curs.fetchall()) == 0:
            return False
        return True

def add_word_to_user(id_tg, word, table='user_word'):
    with Database() as curs:
        word = word.replace("`", "'").replace("’", "'")
        if not check_word(word=word):
            add_word(word)
        _SQL = """insert into """ + table + """ (user_id, word_id)
                    select users.id, words.id
                    from users inner join words on
                    words.word = $$""" + word + """$$ and users.id_tg = """ + str(id_tg) + """ on conflict do nothing;"""
        curs.execute(_SQL)


# USERS
def get_user_dbid(id_tg):
    with Database() as curs:
        _SQL = "SELECT id FROM users WHERE id_tg = " + str(id_tg) + ";"
        curs.execute(_SQL)
        res = curs.fetchall()
        if len(res) == 0:
            return None
        return res[0][0]

def add_user(id_tg, username=None):
    with Database() as curs:
        if not check_user(id_tg):
            if username:
                _SQL = "INSERT INTO users (id_tg, username) VALUES (" + str(id_tg) + ", $$" + username + "$$ );"
            else:
                _SQL = "INSERT INTO users (id_tg) VALUES (" + str(id_tg) + ");"
            curs.execute(_SQL)

def check_user(id_tg):
    with Database() as curs:
        _SQL = "SELECT id FROM users WHERE id_tg = " + str(id_tg) + ";"
        curs.execute(_SQL)
        if len(curs.fetchall()) == 0:
            return False
        return True

