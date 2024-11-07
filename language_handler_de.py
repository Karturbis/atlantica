"""Language handler, which is based on data (word lists) rather
than on trying to implement the structure of the language, because
natural Languages are too complex and have too many exceptions
from their rules to be easily implemented, the systematic approach
is something, wich can be tried with Esperanto."""

import sqlite3


class Wort:
    word_data_path: str = "data/test_language_handler_de_data.sqlite"
    connection = sqlite3.connect(word_data_path)
    cursor = connection.cursor()

    @classmethod
    def get_form(cls, table: str, tags: list, lemma: str):
        command = f"SELECT form FROM {table} WHERE lemma LIKE '{lemma}'"
        for tag in tags:
            command = f"{command} AND tags LIKE '%{tag}%'"
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
            print("create verb: unknown wortart")
        try:
            cls.tags_verben["typ"][typ],
        except KeyError:
            print("create verb: unknown typ")
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


class Artikel(Wort):

    artikel_liste: dict = {
        "definitiv": {
            "nominativ": {
                "maskulin": "der",
                "feminin": "die",
                "neutrum": "das",
                "plural": "die",
            },
            "akkusativ": {
                "maskulin": "den",
            },
            "dativ": {
                "maskulin": "dem",
                "feminin": "der",
                "neutrum": "dem",
                "plural": "den",
            },
            "genitiv": {
                "maskulin": "des",
                "feminin": "der",
                "neutrum": "des",
                "plural": "der",
            },
        },
        "indefinitiv": {
            "nominativ": {
                "maskulin": "ein",
                "feminin": "eine",
                "neutrum": "ein",
                "plural": "",
            },
            "akkusativ": {
                "maskulin": "einen",
            },
            "dativ": {
                "maskulin": "einem",
                "feminin": "einer",
                "neutrum": "einem",
                "plural": "",
            },
            "genitiv": {
                "maskulin": "eines",
                "feminin": "einer",
                "neutrum": "eines",
                "plural": "einer",
            },
        },
    }

    grundformen_possessiv_artikel: dict = {
        "singular": {
            "person_1": "mein",
            "person_2": "dein",
            "person_3": {"maskulin_subjekt": "sein", "feminin_subjekt": "ihr"},
        },
        "plural": {
            "person_1": "unser",
            "person_2": "euer",
            "person_2_no_e": "eur",
            "person_3": {"maskulin_subjektiv": "ihr", "feminin_subjektiv": "Ihr"},
        },
    }

    endungen_possessiv_artikel: dict = {
        "nominativ": {"maskulin": "", "feminin": "e", "neutrum": "", "plural": "e"},
        "akkusativ": {
            "maskulin": "en",
            "feminin": "e",
            "neutrum": "",
            "plural": "e",
        },
        "dativ": {
            "maskulin": "em",
            "feminin": "er",
            "neutrum": "em",
            "plural": "en",
        },
        "genitiv": {
            "maskulin": "es",
            "feminin": "er",
            "neutrum": "es",
            "plural": "er",
        },
    }

    @classmethod
    def _create_possessiv_artikel(
        cls,
        kasus: str,
        genus_objekt: str,
        numerus: str = None,
        person: str = None,
        genus_subjekt: str = None,
    ) -> str:
        """Returns the 'possessiv artikel',
        with the given properties."""

        if (
            numerus == "plural"
            and person == "person_2"
            and not cls.endungen_possessiv_artikel[kasus][genus_objekt] == ""
        ):
            person = "person_2_no_e"
        try:
            possessiv_artikel: str = cls.grundformen_possessiv_artikel[numerus][person][
                genus_subjekt
            ]
        except TypeError:
            possessiv_artikel: str = cls.grundformen_possessiv_artikel[numerus][person]
        possessiv_artikel = (
            f"{possessiv_artikel}{cls.endungen_possessiv_artikel[kasus][genus_objekt]}"
        )
        return possessiv_artikel

    @classmethod
    def create_artikel(
        cls,
        art: str,
        wortart: str,
        kasus: str,
        genus_objekt: str,
        numerus: str,
        person: str = None,
        genus_subjekt: str = None,
    ) -> str:
        """Erzeugt einen Artikel
        mit den übergebenen Parametern."""

        if wortart == "possessiv_artikel":
            return cls._create_possessiv_artikel(
                kasus, genus_objekt, numerus, person, genus_subjekt
            )
        if numerus == "plural":
            genus_objekt = "plural"
            if art == "indefinitiv":
                return ""
        if art == "negativ":
            artikel: str = "k"
            wortart = "indefinitiv"
        else:
            artikel: str = ""
        if genus_objekt != "maskulin" and kasus == "akkusativ":
            kasus = "nominativ"
        artikel = f"{artikel}{cls.artikel_liste[art][kasus][genus_objekt]}"
        return artikel


if __name__ == "__main__":
    print(Nomen.create_nomen("substantiv", "Aal", "dativ", "singular", "maskulin"))
    print(Artikel.create_artikel("definitiv", genus_objekt="neutrum", wortart="artikel", genus_subjekt="maskulin", kasus="dativ", numerus="plural"))
    # print(Wort.create_word("verb", "rückenschwimmen", form="partizip_1"))
