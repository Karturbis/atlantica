"""Language handler, which is based on data (word lists) rather
than on trying to implement the structure of the language, because
natural Languages are too complex and have too many exceptions
from their rules to be easily implemented, the systematic approach
is something, wich can be tried with Esperanto."""
import json

class Wort:
    word_data_path: str = "language_handler_de_data_chunked/"

class Nomen(Wort):
    def __init__(self):
        self.word_data_file = f"{super.word_data_path}nomen.json"


class Verb(Wort):
    def __init__(self):
        self.word_data_files = f"{super.word_data_path}.json"

class Adjektiv(Wort):
    pass