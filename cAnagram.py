from ctypes import (
    CDLL,
    c_char_p,
    c_void_p,
    cast,
)
import os
import os.path
import tempfile
import sys

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

STEAL_SERVER_PATH = os.path.join(BASE_DIR, 'c/steal_server.c')

TEMP_FILE_O = tempfile.NamedTemporaryFile(suffix='.o')
TEMP_FILE_SO = tempfile.NamedTemporaryFile(suffix='.so')

os.system("""gcc -c -fPIC -O3 -o %s %s""" % (TEMP_FILE_O.name, STEAL_SERVER_PATH))
os.system("""gcc -shared -lc -o %s %s""" % (TEMP_FILE_SO.name, TEMP_FILE_O.name))

WORD_LIST = os.path.join(BASE_DIR, 'data/twl06.txt')

DLL = CDLL(TEMP_FILE_SO.name)
DLL.so_initialize(c_char_p(WORD_LIST))
DLL.so_find_steals.restype = c_void_p


def _find_steals(word, pool):
    buff = DLL.so_find_steals(c_char_p(word), c_char_p(pool))
    steals = cast(buff, c_char_p).value.split()
    DLL.del_steals(buff)
    return steals


def anagram(letters):
    return _find_steals(letters, '')


def steals_for(word, pool):
    return [(x, subtract(x, word)) for x in _find_steals(word, pool)]


def subtract(big, small):
    difference = list(big)
    for i in small:
        if i in difference:
            difference.remove(i)
        else:
            return None
    return difference


if __name__ == '__main__':
    print anagram('TEACHER')

    import timeit
    print timeit.timeit(
        """anagram('TEACHER')""",
        setup="""from __main__ import anagram""",
        number=1000000,
    )
