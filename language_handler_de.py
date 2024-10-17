"""Language handler, which is based on data (word lists) rather
than on trying to implement the structure of the language, because
natural Languages are too complex and have too many exceptions
from their rules to be easily implemented, the systematic approach
is something, wich can be tried with Esperanto."""

import sqlite3


class Wort:
    word_data_path: str = "data/test_language_handler_de_data.sqlite"

    @classmethod
    def create_word(
        cls,
        wortart: str,
        lemma: str,
        kasus: str = None,
        numerus: str = None,
        genus: str = None,
        typ: str = None,
        form: str = None,
        person: str = None,
        gebrauch: str = None,
    ):
        connection = sqlite3.connect(cls.word_data_path)
        cursor = connection.cursor()
        if wortart in {"eigenname", "substantiv"}:
            return Nomen.create_nomen(
                connection, cursor, wortart, lemma, kasus, numerus, genus
            )
        return "ERROR IN create word"


class Nomen(Wort):
    tags_nomen: dict = {
        "wortart": {"eigenname": "EIG", "substantiv": "SUB"},
        "kasus": {
            "nominativ": "NOM",
            "genitiv": "GEN",
            "dativ": "DAT",
            "akkusativ": "AKK",
        },
        "numerus": {"singular": "SIN", "plural": "PLU"},
        "genus": {
            "maskulin": "MAS",
            "feminin": "FEM",
            "neutrum": "NEU",
            "no_genus": "NOG",
        },
    }

    @classmethod
    def create_nomen(
        cls,
        connection,
        cursor,
        wortart: str,
        lemma: str,
        kasus: str = "",
        numerus: str = "",
        genus: str = "",
    ):
        tags = f"{cls.tags_nomen["wortart"][wortart]}:{cls.tags_nomen["kasus"][kasus]}:{cls.tags_nomen["numerus"][numerus]}:{cls.tags_nomen["genus"][genus]}"
        database_return = connection.execute(
            f"SELECT form FROM nomen WHERE lemma='{lemma}' AND tags='{tags}'"
        )
        form = database_return.fetchall()[0][0]
        return form


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


if __name__ == "__main__":
    print(Wort.create_word("substantiv", "Aal", "dativ", "singular", "maskulin"))
