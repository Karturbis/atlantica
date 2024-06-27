"""Compiles the given sentence
to valid german language code."""

class LanguageHandlerDE:
    """Compiler for german
    language output."""

    def __init__(self):
        self.__artikel_definitif: dict = {
            "nominativ": {
                "maskulin": "der",
                "feminin": "die",
                "neutral": "das",
                "plural": "die"
            },
            "akkusativ": {
                "maskulin": "den",
                "feminin": "die",
                "neutral": "das",
                "plural": "die"
            },
            "dativ": {
                "maskulin": "dem",
                "feminin": "der",
                "neutral": "dem",
                "plural": "den"
            },
            "genitiv": {
                "maskulin": "des",
                "feminin": "der",
                "neutral": "des",
                "plural": "der"
            }
        }
        self.__artikel_indefinitiv: dict = {

        }
        self.__artikel_negativ: dict = {

        }


    def chunk_description(self, attributes: dict) -> str:
        """Compiles the chunk desciprion
        from the given attributes."""
        output: str = f"Du bist in {attributes["room"]}"
        return output
