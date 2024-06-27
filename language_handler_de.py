"""Compiles the given sentence
to valid german language code."""


class LanguageHandlerDE:
    """Compiler for german
    language output."""

    def __init__(self):
        pass

    def create_possesiv_artikel(
        self,
        fall: str,
        geschlecht_objekt: str,
        anzahl: str = None,
        person: str = None,
        geschlecht_subjekt: str = None,
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
            anzahl == "plural"
            and person == "person_2"
            and not endungen[fall][geschlecht_objekt] == ""
        ):
            person = "person_2_no_e"
        try:
            possesiv_artikel: str = grundformen[anzahl][person][geschlecht_subjekt]
        except TypeError:
            possesiv_artikel: str = grundformen[anzahl][person]
        possesiv_artikel = f"{possesiv_artikel}{endungen[fall][geschlecht_objekt]}"
        return possesiv_artikel

    def create_artikel(
        self,
        art: str,
        fall: str,
        geschlecht_objekt: str,
        anzahl: str,
        person: str = None,
        geschlecht_subjekt: str = None
    ) -> str:
        artikel_liste: dict = {
            "definitiv": {
                "nominativ": {
                    "maskulin": "der",
                    "feminin": "die",
                    "neutrum": "das",
                    "plural": "die"
                },
                "akkusativ": {
                    "maskulin": "den",
                },
                "dativ": {
                    "maskulin": "dem",
                    "feminin": "der",
                    "neutrum": "dem",
                    "plural": "den"
                },
                "genitiv": {
                    "maskulin": "des",
                    "feminin": "der",
                    "neutrum": "des",
                    "plural": "der"
                }
            },
            "indefinitiv":{
                "nominativ": {
                    "maskulin": "ein",
                    "feminin": "eine",
                    "neutrum": "ein",
                    "plural": ""
                },
                "akkusativ": {
                    "maskulin": "einen",
                },
                "dativ": {
                    "maskulin": "einem",
                    "feminin": "einer",
                    "neutrum": "einem",
                    "plural": ""
                },
                "genitiv": {
                    "maskulin": "eines",
                    "feminin": "einer",
                    "neutrum": "eines",
                    "plural": "einer"
                }
            }
        }
        if art == "possesiv":
            return self.create_possesiv_artikel(fall, geschlecht_objekt, anzahl, person, geschlecht_subjekt)
        if anzahl == "plural":
            geschlecht_objekt = "plural"
            if art == "indefinitiv":
                return ""
        if art == "negativ":
            artikel: str = "k"
            art = "indefinitiv"
        else:
            artikel: str = ""
        if geschlecht_objekt != "maskulin" and fall == "akkusativ":
            fall = "nominativ"
        artikel = f"{artikel}{artikel_liste[art][fall][geschlecht_objekt]}"
        return artikel


if __name__ == "__main__":
    lh_de = LanguageHandlerDE()
    var1 = input("Type the art of the article: ")
    var2 = input("Fall: ")
    var3 = input("Genus: ")
    var4 = input("Anzahl: ")
    print(lh_de.create_artikel(var1, var2, var3, var4))