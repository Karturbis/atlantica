"""Compiles the given sentence
to valid german language output."""
import sqlite3


class LanguageHandlerDE:
    """Compiler for german
    language output."""

    def __init__(self):
        self.__schwa_silben: list = ["el", "er", "en", "e"]

    def nomen_pluralisierung(self, grundform_plural: str, genus: str) -> str:
        """Bildet den Plural eines Nomens."""
        ausnahmen = {
            "besipiel": "plural des beispiels"
        }
        if grundform_plural in ausnahmen:
            return ausnahmen[grundform_plural]
        if genus == "feminin":
            return f"{grundform_plural}en"
        if grundform_plural.endswith("e") and genus == "maskulin":
            return f"{grundform_plural}en"
        for i in self.__schwa_silben:
            if grundform_plural.endswith(i):
                return grundform_plural
        # Else:
        return f"{grundform_plural}e"

    def nomen_deklination_n(
        self, grundform: str, kasus: str, genus: str, numerus: str, ausnahme: int
    ) -> str:
        """dekliniert das übergebene Nomen nach den
        Regeln der n-deklination"""
        if ausnahme == 0:  # Regelfall:
            # Kein check für nominativ-singular, da in create_nomen gecheckt.
            for i in self.__schwa_silben:
                if grundform.endswith(i):
                    return f"{grundform}n"
            # if not endung = ein schwa laut:
            return f"{grundform}en"
        if ausnahme == 1:  # Ausnahmefall 1
            if kasus == "genitv":
                return (
                    f"{self.nomen_deklination_n(grundform, kasus, genus, numerus, 0)}s"
                )
            # Else:
            return self.nomen_deklination_n(grundform, kasus, genus, numerus, 0)

        if ausnahme == 2:  # Ausnahmefall Herr
            if numerus == "plural":
                return self.nomen_deklination_n("herre", kasus, genus, numerus, 0)
            # Else:
            return self.nomen_deklination_n("herr", kasus, genus, numerus, 0)

        return ""

    def nomen_deklination_standard(
        self, grundform: str, grundform_plural: str, kasus: str, genus: str, numerus: str
    ) -> str:
        """Dekliniert das übergebene Nomen
        nach den standard deklinations Regeln."""
        if numerus == "plural":
            grundform = self.nomen_pluralisierung(grundform_plural, genus)
        if genus == "maskulin" or genus == "neutrum":
            endungen: dict = {
                "nominativ": "",
                "genitiv": "s",
                "dativ": "",
                "akkusativ": ""
            }
            grundform = f"{grundform}{endungen[kasus]}"

        return f"{grundform}"

    def create_nomen(
        self,
        grundform: str,
        grundform_plural: str,
        kasus: str,
        genus: str,
        numerus: str
    ) -> str:
        """Erzeugt ein Nomen, greift auf
        nomen_deklination_standard() zu"""
        ausnahmen: dict = {
            "platzhalter": {
                "nominativ": {
                    "maskulin": {"singular": "", "plural": ""},
                    "feminin": {"singular": "", "plural": ""},
                    "neutrum": {"singular": "", "plural": ""},
                },
                "akkusativ": {
                    "maskulin": {"singular": "", "plural": ""},
                    "feminin": {"singular": "", "plural": ""},
                    "neutrum": {"singular": "", "plural": ""},
                },
                "dativ": {
                    "maskulin": {"singular": "", "plural": ""},
                    "feminin": {"singular": "", "plural": ""},
                    "neutrum": {"singular": "", "plural": ""},
                },
                "genitiv": {
                    "maskulin": {"singular": "", "plural": ""},
                    "feminin": {"singular": "", "plural": ""},
                    "neutrum": {"singular": "", "plural": ""},
                },
            }
        }
        if grundform in ausnahmen:
            return ausnahmen[grundform][kasus][genus][numerus]
        if kasus == "nominativ" and numerus == "singular":
            return grundform
        n_deklinations_endungen: list = [
            "oge",
            "ent",
            "ant",
            "at",
            "ist",
            "e",
            "et",
            "it",
            "graf",
            "ot",
            "soph",
            "at",
            "nom",
        ]
        n_deklinations_ausnahmen: list = [
            "bauer",
            "bär",
            "held",
            "mensch",
            "nachbar",
            "prinz",
        ]
        n_deklinations_ausnahmen_1: list = ["herz", "buchstabe", "gedanke", "name"]
        for i in n_deklinations_endungen:
            if grundform.endswith(i):
                return self.nomen_deklination_n(grundform, kasus, genus, numerus, 0)
        if grundform in n_deklinations_ausnahmen:
            return self.nomen_deklination_n(grundform, kasus, genus, numerus, 0)
        if grundform in n_deklinations_ausnahmen_1:
            return self.nomen_deklination_n(grundform, kasus, genus, numerus, 1)
        if grundform == "herr":
            return self.nomen_deklination_n(grundform, kasus, genus, numerus, 2)
        # Else:
        return self.nomen_deklination_standard(grundform, grundform_plural, kasus, genus, numerus)

    def create_possesiv_artikel(
        self,
        kasus: str,
        genus_objekt: str,
        numerus: str = None,
        person: str = None,
        genus_subjekt: str = None,
    ) -> str:
        """Returns the 'possesiv artikel',
        with the given properties."""
        grundformen: dict = {
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
        endungen: dict = {
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
        if (
            numerus == "plural"
            and person == "person_2"
            and not endungen[kasus][genus_objekt] == ""
        ):
            person = "person_2_no_e"
        try:
            possesiv_artikel: str = grundformen[numerus][person][genus_subjekt]
        except TypeError:
            possesiv_artikel: str = grundformen[numerus][person]
        possesiv_artikel = f"{possesiv_artikel}{endungen[kasus][genus_objekt]}"
        return possesiv_artikel

    def create_artikel(
        self,
        art: str,
        kasus: str,
        genus_objekt: str,
        numerus: str,
        person: str = None,
        genus_subjekt: str = None,
    ) -> str:
        """Erzeugt einen Artikel
        mit den übergebenen Parametern."""
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
        if art == "possesiv":
            return self.create_possesiv_artikel(
                kasus, genus_objekt, numerus, person, genus_subjekt
            )
        if numerus == "plural":
            genus_objekt = "plural"
            if art == "indefinitiv":
                return ""
        if art == "negativ":
            artikel: str = "k"
            art = "indefinitiv"
        else:
            artikel: str = ""
        if genus_objekt != "maskulin" and kasus == "akkusativ":
            kasus = "nominativ"
        artikel = f"{artikel}{artikel_liste[art][kasus][genus_objekt]}"
        return artikel

    def create_verb(self, grundform: str, kasus: str, genus: str, numerus: str) -> str:
        """Erstellt ein Verb mit den gegebenen Parametern"""

# Tests:
if __name__ == "__main__":
    lh_de = LanguageHandlerDE()
    var0 = input("Type the nomen you want: ").lower()
    var1 = input("Grundform_plural: ")
    var3 = input("Genus: ")
    print(
        f"{lh_de.create_artikel("negativ", "nominativ", var3, "singular").capitalize()} {lh_de.create_nomen(var0, var1, "nominativ", var3, "singular").capitalize()} würde das tun."
    )
    print(
        f"{lh_de.create_nomen(var0, var1, "dativ", var3, "plural").capitalize()} würden so etwas nicht tun."
    )
    print(
        f"{lh_de.create_artikel("indefinitiv", "nominativ", var3, "singular").capitalize()} {lh_de.create_nomen(var0, var1, "nominativ", var3, "singular").capitalize()} tut so etwas nicht!"
    )
    print(
        f"Du hast {lh_de.create_artikel("indefinitiv", "akkusativ", var3, "singular")} {lh_de.create_nomen(var0, var1, "akkusativ", var3, "singular").capitalize()} gegessen."
    )
    print(
        f"Das gehört {lh_de.create_artikel("definitiv", "dativ", var3, "singular")} {lh_de.create_nomen(var0, var1, "dativ", var3, "singular").capitalize()}."
    )
