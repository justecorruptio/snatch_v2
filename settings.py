import os
import os.path

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

GAME_END_TIME = 60
PEEL_DELAY = 5.2;

MIN_WORD_LENGTH = 4;

SCRABBLE_LETTERS = ('AAAAAAAAABBCCDDDDEEEEEEEEEEEEFFGGGHHIIIIIIIIIJKLL'
                    'LLMMNNNNNNOOOOOOOOPPQRRRRRRSSSSTTTTTTUUUUVVWWXYYZ')

GAME_LETTERS = list(SCRABBLE_LETTERS)
NUM_LETTERS = 98


TORNADO_SETTINGS = {
    'static_path': os.path.join(BASE_DIR, 'static'),
    'template_path': os.path.join(BASE_DIR, 'templates'),
    'debug': True,
}
