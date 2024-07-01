"""Compiles the given sentence
to valid german language output."""


class LanguageHandlerDE:
    """Compiler for german
    language output."""

    def __init__(self):
        pass

    def nomen_deklination_n(
        self, grundform: str, fall: str, genus: str, numerus: str, ausnahme: int
    ) -> str:
        """dekliniert das übergebene Nomen nach den
        Regeln der n-deklination"""
        if ausnahme == 0:  # Regelfall:
            # Kein check für nominativ-singular, da in create_nomen gecheckt.
            endungen_e_gebraucht: list = ["f", "t", "d", "h", "r", "z", "m"]
            for i in endungen_e_gebraucht:
                if grundform.endswith(i):
                    return f"{grundform}en"
            # if not endung = "f" or "t" or "d"
            return f"{grundform}n"
        if ausnahme == 1:  # Ausnahmefall 1
            if fall == "genitv":
                return (
                    f"{self.nomen_deklination_n(grundform, fall, genus, numerus, 0)}s"
                )
            # Else:
            return self.nomen_deklination_n(grundform, fall, genus, numerus, 0)

        if ausnahme == 2:  # Ausnahmefall Herr
            if numerus == "plural":
                return self.nomen_deklination_n("herre", fall, genus, numerus, 0)
            # Else:
            return self.nomen_deklination_n("herr", fall, genus, numerus, 0)

        return ""

    def nomen_deklination_standard(
        self, grundform: str, fall: str, genus: str, numerus: str
    ) -> str:
        """Dekliniert das übergebene Nomen
        nach den standard deklinations Regeln."""
        return "NoName"

    def create_nomen(self, grundform: str, fall: str, genus: str, numerus: str) -> str:
        """Erzeugt ein Nomen, greift auf
        nomen_deklination_standard()"""
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
            return ausnahmen[grundform][fall][genus][numerus]
        if fall == "nominativ" and numerus == "singular":
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
            "nom"
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
                return self.nomen_deklination_n(grundform, fall, genus, numerus, 0)
        if grundform in n_deklinations_ausnahmen:
            return self.nomen_deklination_n(grundform, fall, genus, numerus, 0)
        if grundform in n_deklinations_ausnahmen_1:
            return self.nomen_deklination_n(grundform, fall, genus, numerus, 1)
        if grundform == "herr":
            return self.nomen_deklination_n(grundform, fall, genus, numerus, 2)
        # Else:
        return self.nomen_deklination_standard(grundform, fall, genus, numerus)

    def create_possesiv_artikel(
        self,
        fall: str,
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
            and not endungen[fall][genus_objekt] == ""
        ):
            person = "person_2_no_e"
        try:
            possesiv_artikel: str = grundformen[numerus][person][genus_subjekt]
        except TypeError:
            possesiv_artikel: str = grundformen[numerus][person]
        possesiv_artikel = f"{possesiv_artikel}{endungen[fall][genus_objekt]}"
        return possesiv_artikel

    def create_artikel(
        self,
        art: str,
        fall: str,
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
                fall, genus_objekt, numerus, person, genus_subjekt
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
        if genus_objekt != "maskulin" and fall == "akkusativ":
            fall = "nominativ"
        artikel = f"{artikel}{artikel_liste[art][fall][genus_objekt]}"
        return artikel


if __name__ == "__main__":
    lh_de = LanguageHandlerDE()
    var0 = input("Type the nomen you want: ").lower()
    var1 = input("Type the art of the article: ")
    var2 = input("Fall: ")
    var3 = input("Genus: ")
    var4 = input("numerus: ")
    print(
        f"{lh_de.create_artikel(var1, var2, var3, var4)} {lh_de.create_nomen(var0, var2, var3, var4)}"
    )
