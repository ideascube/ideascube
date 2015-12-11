import struct

from django.db import connection


def create_index_table(force=True):
    cursor = connection.cursor()
    cursor.execute("SELECT count(*) FROM sqlite_master "
                   "WHERE type='table' AND name='idx';")
    count = cursor.fetchone()[0]
    if not count or force:
        cursor.execute("DROP TABLE IF EXISTS idx")
        cursor.execute("CREATE VIRTUAL TABLE idx using "
                       "FTS4(id, model, model_id, public, text)")


def rank(match_info):
    # Handle match_info called w/default args 'pcx' - based on the example
    # rank function http://sqlite.org/fts3.html#appendix_a
    # From github.com/coleifer/peewee/master/playhouse/sqlite_ext.py
    # Structure of match_info
    # It's a bytes array that looks like
    #  3 2  1 3 2  0 1 1  1 2 2...
    #  p c  x y z [x y z, x y z]
    # p is the number of tokens of the query
    # c is the number of searchable columns in the FTS table
    # every [xyz] group represents a match of one word against one columns,
    # so for example first group is for first word against first column, then
    # first word against second column, and so on, then second column on first
    # column, then second column, etc.
    # On each group:
    # - x is for the number of hits of the current word in the current column
    # - y is for the number of occurrences of the given word in all columns of
    #   all rows
    # - z is for the number of rows where the given word has been found
    score = 0.0
    if not match_info:
        return score
    bufsize = len(match_info)  # length in bytes
    match_info = [struct.unpack('@I', match_info[i:i+4])[0]
                  for i in range(0, bufsize, 4)]
    p, c = match_info[:2]
    for phrase_num in range(p):  # For earch word in the search query.
        phrase_info_idx = 2 + (phrase_num * c * 3)
        for col_num in range(c):  # For each searchable column.
            col_idx = phrase_info_idx + (col_num * 3)
            x1, x2 = match_info[col_idx:col_idx + 2]
            if x1 > 0:
                # The more hits in the column, the higher score (x1); the more
                # rows containing the word in the index, the lower score (x2).
                score += float(x1) / x2
    return score
