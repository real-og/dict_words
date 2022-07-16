import psycopg2


class Database(object):
    def __init__(self):
        self.conn = psycopg2.connect(
            database="words",
            user="words",
            password="words",
            host="127.0.0.1",
            port="5432"
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


# problem with word contain ' symbol
# def add_words(words):
#     with Database() as curs:
#         _SQL = """INSERT INTO words (word) VALUES"""
#         for word in words:
#             if "'" in word:
#
#             _SQL = _SQL + " ('" + word + "'), "
#         _SQL = _SQL[:-2] + ' ON CONFLICT (word) DO NOTHING;'
#         curs.execute(_SQL)


def add_words(words):
    with Database() as curs:
        _SQL = """INSERT INTO words (word) VALUES"""
        for word in words:
            if "'" not in word:
                _SQL = "INSERT INTO words (word) VALUES ('" + word + "') ON CONFLICT (word) DO NOTHING;"
                curs.execute(_SQL)



