"""Language handler, which is based on data (word lists) rather
than on trying to implement the structure of the language, because
natural Languages are too complex and have too many exceptions
from their rules to be easily implemented, the systematic approach
is something, wich can be tried with Esperanto."""

import sqlite3
from colorama import Fore, Style


class Satz:

    @classmethod
    def create_satz(cls, kasus, zeitform, args: list[dict]):
        satz = ""
        # use string and not list, to be able to add
        # punctuations without spaces.
        subjekt = None
        objekt = None
        for word in args:
            wortart = word["wortart"]
            if wortart == "eigenname" or wortart == "substantiv":
                word["form"] = Nomen.create_nomen(
                    wortart, word["lemma"], kasus, word["numerus"]
                )
                word["genus"] = Wort.get_genus("nomen", word["form"])
                satz = f"{satz} {word["form"]}"
                if word["funktion"] == "subjekt":
                    subjekt = word
                elif word["funktion"] == "objekt":
                    objekt = word
                    subjekt = word

            elif wortart == "adjektiv":
                pass
                # satz = satz + " " + Adjektiv()
            elif wortart == "verb":
                satz = (
                    satz
                    + " "
                    + Verb.create_verb(
                        wortart,
                        word["lemma"],
                        word["typ"],
                        word["form"],
                        word["person"],
                    )
                )
            elif wortart == "artikel" or wortart == "possesiv_artikel":
                satz = (
                    satz
                    + " "
                    + Artikel.create_artikel(
                        word["art"],
                        wortart,
                        kasus,
                        objekt["genus"],
                        objekt["numerus"],
                        word["person"],
                        subjekt["genus"],
                    )
                )
            elif wortart == "konst":
                satz = satz + " " + word["wort"]
            else:
                satz = satz + word["satzzeichen"]
        satz = satz.split(" ")
        satz[0] = satz[0].capitalize()
        satz = " ".join(satz)[1:]
        return satz


class Wort:
    """Parent class, for all classes, who need
    to create a word."""

    # Setup the sqlite3 database connection:
    word_data_path: str = "data/test_language_handler_de_data.sqlite"
    connection = sqlite3.connect(word_data_path)
    cursor = connection.cursor()

    @classmethod
    def get_form(cls, table: str, tags: list, lemma: str) -> str:
        """Creates and executes a sqlite command, to get
        the needed word from the sqlite database."""
        command = f"SELECT form FROM {table} WHERE lemma LIKE '{lemma}'"
        for tag in tags:
            command = f"{command} AND tags LIKE '%{tag}%'"
        return cls.cursor.execute(command).fetchall()

    @classmethod
    def get_tags(cls, table: str, form: str) -> str:
        """Creates and executes a sqlite command, to get
        the tags of the given word from the sqlite database."""
        command = f"SELECT tags FROM {table} WHERE form LIKE '{form}'"
        return cls.cursor.execute(command).fetchall()

    @classmethod
    def get_genus(cls, table: str, form: str) -> str:
        tags = str(cls.get_tags(table, form)).upper()
        if "FEM" in tags:
            return "feminin"
        if "MAS" in tags:
            return "maskulin"
        if "NEU" in tags:
            return "neutrum"


class Nomen(Wort):
    """Class with all the tags and methods
    needed to create a Nomen."""

    # possible tags for Nomen in the database:
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
    ):
        """Creates the Nomen, using the get_form()
        method from the Word class."""
        tags = [
            cls.tags_nomen["wortart"][wortart],
            cls.tags_nomen["kasus"][kasus],
            cls.tags_nomen["numerus"][numerus],
        ]
        form = super().get_form("nomen", tags, lemma)[0][0]
        return form


class Verb(Wort):
    """Contains all the Tag-data and the
    method to create a verb."""

    # possible tags for verbs in the database:
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
        "zeitform": {"präteritum": "PRÄ"
        }
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
        """Sets the tags for the database
        query, prints a Warning, if a tag is
        not found. Calls the Word.get_form()
        method to get the correct verb."""
        tags = []
        try:
            tags.append(cls.tags_verben["wortart"][wortart])
        except KeyError:
            print(
                f"{Fore.YELLOW}Warning:{Style.RESET_ALL} create verb: unknown wortart"
            )
        try:
            cls.tags_verben["typ"][typ],
        except KeyError:
            print(f"{Fore.YELLOW}Warning:{Style.RESET_ALL} create verb: unknown typ")
        try:
            tags.append(cls.tags_verben["form"][form])
        except KeyError:
            print(f"{Fore.YELLOW}Warning:{Style.RESET_ALL} create verb: unknown form")
        try:
            tags.append(cls.tags_verben["person"][person])
        except KeyError:
            print(
                f"{Fore.YELLOW}Warning:{Style.RESET_ALL} create verb: person not found"
            )
        form = super().get_form("verben", tags, lemma)[0][0]
        return form


class Adjektiv(Wort):
    """Contains all the tags needed
    to create an Adjektiv."""

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


class Artikel:
    """Contains all data and methods
    to create every german article."""

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
        """Creates an article with the
        given parameters."""

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


# For testing:
if __name__ == "__main__":
    """
    print(
        Artikel.create_artikel(
            "definitiv",
            genus_objekt="maskulin",
            wortart="artikel",
            genus_subjekt="maskulin",
            kasus="nominativ",
            numerus="singular",
        )
    )
    print(Nomen.create_nomen("substantiv", "Aal", "nominativ", "singular"))
    print(Verb.create_verb("verb", "schwimmen", person="3_person"))
    print("durch")
    print(
        Artikel.create_artikel(
            "definitiv",
            genus_objekt="neutrum",
            genus_subjekt="maskulin",
            wortart="artikel",
            kasus="nominativ",
            numerus="singular",
        )
    )
    print(Nomen.create_nomen("substantiv", "wasser", "nominativ", "singular"))
    """


    satz = Satz.create_satz(
        "nominativ",
        "perfekt",
        [
            {"wortart": "konst", "wort": "du"},
            {"wortart": "verb", },
            {"wortart": "konst"}
        ]
    )

    print(satz)