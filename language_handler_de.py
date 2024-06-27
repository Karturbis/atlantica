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
            "nominativ": {"maskulin": "", "feminin": "e", "neutral": "", "plural": "e"},
            "akkusativ": {
                "maskulin": "en",
                "feminin": "e",
                "neutral": "",
                "plural": "e",
            },
            "dativ": {
                "maskulin": "em",
                "feminin": "er",
                "neutral": "em",
                "plural": "en",
            },
            "genitiv": {
                "maskulin": "es",
                "feminin": "er",
                "neutral": "es",
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


if __name__ == "__main__":
    # for testing
    lh_de = LanguageHandlerDE()

    print(
        lh_de.create_possesiv_artikel(
            "dativ", "maskulin", "plural", "person_2", "neutral"
        )
    )
