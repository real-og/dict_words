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
    with Database() as curs:
        _SQL = """INSERT INTO words (word) VALUES"""
        for word in words:
            word = word.replace("'", "''").replace("`", "''")
            _SQL = _SQL + " ('" + word + "'), "
        _SQL = _SQL[:-2] + ' ON CONFLICT (word) DO NOTHING;'
        curs.execute(_SQL)

# Too slow
# def add_words(words):
#     for word in words:
#         add_word(word)


def check_word(word):
    word = word.replace("'", "''").replace("`", "''")
    with Database() as curs:
        _SQL = "SELECT word FROM words WHERE word = '" + word + "';"
        curs.execute(_SQL)
        if len(curs.fetchall()) == 0:
            return False
        return True


def add_word(word):
    with Database() as curs:
        word = word.replace("'", "''").replace("`", "''")
        _SQL = "INSERT INTO words (word) VALUES ('" + word + "') ON CONFLICT (word) DO NOTHING;"
        curs.execute(_SQL)
