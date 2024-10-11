"""Language handler, which is based on data (word lists) rather
than on trying to implement the structure of the language, because
natural Languages are too complex and have too many exceptions
from their rules to be easily implemented, the systematic approach
is something, wich can be tried with Esperanto."""

import json


class Wort:
    word_data_path: str = "language_handler_de_data_chunked/"

    @classmethod
    def create_word(
        cls, wortart: str, lemma: str, genus: str, numerus: str, kasus: str
    ):
        word = ""
        return word


class Nomen(Wort):
    tags_nomen: dict = {
        "wortart": {"EIG": "eigenname", "SUB": "substantiv"},
        "kasus": {
            "NOM": "nominativ",
            "GEN": "genitiv",
            "DAT": "dativ",
            "AKK": "akkusativ",
        },
        "numerus": {"SIN": "singular", "PLU": "plural"},
        "genus": {
            "MAS": "maskulin",
            "FEM": "feminin",
            "NEU": "neutrum",
            "NOG": "no_genus",
        },
    }
    word_data_file: str = f"{super.word_data_path}nomen.json"


class Verb(Wort):
    tags_verben: dict = {
        "wortart": {"VER": "verb", "SKZ": "wortform_zu", "ZUS": "zusatz"},
        "typ": {"AUX": "hilfsverb", "MOD": "modal"},
        "form": {
            "INF": "infinitiv",
            "PA1": "partizip_1",
            "PA2": "partizip_2",
            "EIZ": "erweiterter_infinitiv_mit_zu",
            "IMP": "imperativ",
        },
        "person": {"1": "1_person", "2": "2_person", "3": "3_person"},
    }
    word_data_files: dict = {
        "a": f"{super.word_data_path}verben_a.json",
        "b-e": f"{super.word_data_path}verben_b-e.json",
        "f-i": f"{super.word_data_path}verben_f-i.json",
        "j-t": f"{super.word_data_path}verben_j-t.json",
        "u-z": f"{super.word_data_path}verben_u-z.json",
    }


class Adjektiv(Wort):
    tags_adjektive: dict = {
        "wortart": {"ADJ": "adjektiv", "PA1": "partizip_1", "PA2": "partizip_2"},
        "art": {"SOL": "alleinstehend", "DEF": "definitiv", "IND": "indefinitiv"},
        "kasus": {
            "NOM": "nominativ",
            "GEN": "genitiv",
            "DAT": "dativ",
            "AKK": "akkusativ",
        },
        "numerus": {"SIN": "singular", "PLU": "plural"},
        "genus": {"MAS": "maskulin", "FEM": "feminin", "NEU": "neutrum"},
        "gebrauch": {"ADV": "adverb"},
    }
    word_data_files: dict = {
        "a-j": f"{super.word_data_path}adjektive_a-j.json",
        "k-s": f"{super.word_data_path}adjektive_k-s.json",
        "t-z": f"{super.word_data_path}adjektive_t-z.json",
    }
