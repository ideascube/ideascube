import struct

from django.db import connection


def create_index_table():
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS idx")
    cursor.execute("CREATE VIRTUAL TABLE idx using "
                   "FTS4(id, model, model_id, public, text)")


def rank(match_info):
    # Handle match_info called w/default args 'pcx' - based on the example
    # rank function http://sqlite.org/fts3.html#appendix_a
    # From github.com/coleifer/peewee/master/playhouse/sqlite_ext.py
    score = 0.0
    if not match_info:
        return score
    bufsize = len(match_info)  # length in bytes
    match_info = [struct.unpack('@I', match_info[i:i+4])[0]
                  for i in range(0, bufsize, 4)]
    p, c = match_info[:2]
    for phrase_num in range(p):
        phrase_info_idx = 2 + (phrase_num * c * 3)
        for col_num in range(c):
            col_idx = phrase_info_idx + (col_num * 3)
            x1, x2 = match_info[col_idx:col_idx + 2]
            if x1 > 0:
                score += float(x1) / x2
    return score
