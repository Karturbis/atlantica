"""Language handler, which is based on data (word lists) rather
than on trying to implement the structure of the language, because
natural Languages are too complex and have too many exceptions
from their rules to be easily implemented, the systematic approach
is something, wich can be tried with Esperanto."""

import sqlite3


class Wort:
    word_data_path: str = "data/test_language_handler_de_data.sqlite"
    cursor = connection.cursor()

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
        if wortart in {"eigenname", "substantiv"}:
            return Nomen.create_nomen(wortart, lemma, kasus, numerus, genus)
        if wortart in {"verb", "wortform_zu", "zusatz"}:
            return Verb.create_verb(
                wortart=wortart, lemma=lemma, form=form, person=person
            )
        return "ERROR IN create word"

    @classmethod
    def get_form(cls, table: str, tags: list, lemma: str):
        command = f"SELECT form FROM {table} WHERE lemma LIKE '{lemma}' AND tags LIKE '%{tags[0]}%'"
        for i in range(len(tags) - 1):
            command = f"{command} AND tags LIKE '%{tags[i + 1]}%'"
        return cls.cursor.execute(command).fetchall()


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
        wortart: str,
        lemma: str,
        kasus: str = "",
        numerus: str = "",
        genus: str = "",
    ):
        tags = [
            cls.tags_nomen["wortart"][wortart],
            cls.tags_nomen["kasus"][kasus],
            cls.tags_nomen["numerus"][numerus],
            cls.tags_nomen["genus"][genus],
        ]
        form = super().get_form("nomen", tags, lemma)[0][0]
        return form


class Verb(Wort):
    tags_verben: dict = {
        "wortart": {"verb": "VER", "wortform_zu": "SKZ", "zusatz": "ZUS"},
        "typ": {"hilfsverb": "AUX", "modal": "MOD"},
        "form": {
            "infinitiv": "INF",
            "partizip_1": "PA1",
            "partizip_2": "PA2",
            "erweiterter_infinitiv_mit_zu": "EIZ",
            "imperativ": "IMP",
        },
        "person": {"1_person": "1", "2_person": "2", "3_person": "3"},
    }

    @classmethod
    def create_verb(
        cls,
        wortart: str,
        lemma: str,
        typ: str = None,
        form: str = None,
        person: str = None,
    ):
        tags = []
        try:
            tags.append(cls.tags_verben["wortart"][wortart])
        except KeyError:
            pass
        try:
            cls.tags_verben["typ"][typ],
        except KeyError:
        cls.tags_verben["form"][form],
        cls.tags_verben["person"][person],
        form = super().get_form("verben", tags, lemma)
        return form


class Adjektiv(Wort):
    tags_adjektive: dict = {
        "wortart": {"adjektiv": "ADJ", "partizip_1": "PA1", "partizip_2": "PA2"},
        "art": {"alleinstehend": "SOL", "definitiv": "DEF", "indefinitiv": "IND"},
        "kasus": {
            "nominativ": "NOM",
            "genitiv": "GEN",
            "dativ": "DAT",
            "akkusativ": "AKK",
        },
        "numerus": {"singular": "SIN", "plural": "PLU"},
        "genus": {"maskulin": "MAS", "feminin": "FEM", "neutrum": "NEU"},
        "gebrauch": {"adverb": "ADV"},
    }


if __name__ == "__main__":
    print(Wort.create_word("substantiv", "Aal", "dativ", "singular", "maskulin"))
    print(Wort.create_word("verb", "rückenschwimmen", form="partizip_1"))
