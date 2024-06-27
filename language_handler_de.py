"""Compiles the given sentence
to valid german language code."""

class LanguageHandlerDE:
    """Compiler for german
    language output."""

    def __init__(self):
        """To acess the artikel dict:
        [Art][fall][geschlecht_objekt]
            (Bei possesiv zusätzlich am Ende):
            [singular/plural][person]
                (bei dritter Person zusätzlich am Ende):
                [geschlecht_subjekt]"""

        self.__artikel: dict = {
            "definitiv": {
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
            },
            "indefinitiv": {  # Indefinitiv für plural ist immer leer
                "nominativ": {
                    "maskulin": "ein",
                    "feminin": "eine",
                    "neutral": "ein",
                },
                "akkusativ": {
                    "maskulin": "einen",
                    "feminin": "eine",
                    "neutral": "ein",
                },
                "dativ": {
                    "maskulin": "einem",
                    "feminin": "einer",
                    "neutral": "einem",
                },
                "genitiv": {
                    "maskulin": "eines",
                    "feminin": "einer",
                    "neutral": "eines",
                }
            },
            "negativ": {
                "nominativ": {
                    "maskulin": "kein",
                    "feminin": "keine",
                    "neutral": "kein",
                    "plural": "keine"
                },
                "akkusativ": {
                    "maskulin": "keinen",
                    "feminin": "keine",
                    "neutral": "kein",
                    "plural": "keine"
                },
                "dativ": {
                    "maskulin": "keinem",
                    "feminin": "keiner",
                    "neutral": "keinem",
                    "plural": "keinen"
                },
                "genitiv": {
                    "maskulin": "keines",
                    "feminin": "keiner",
                    "neutral": "keines"
                    # Es gibt keinen negativen Plural des Genitivs
                }
            },
            "possesiv": {  # Besitzanzeigend
                "nominativ": {
                    "maskulin": {
                        "singular": {
                            "person_1": "mein",
                            "person_2": "dein",
                            "person_3": {
                                "maskulin": "sein",
                                "feminin": "ihr",
                                "neutral": "sein"
                            }
                        },
                        "plural": {
                            "person_1": "unser",
                            "person_2": "euer",
                            "person_3": {
                                "maskulin": "ihr",
                                "feminin": "Ihr",
                            }
                        }
                    },
                    "feminin": {
                        "singular": {
                            "person_1": "meine",
                            "person_2": "deine",
                            "person_3": {
                                "maskulin": "seine",
                                "feminin": "ihre",
                                "neutral": "seine"
                            }
                        },
                        "plural": {
                            "person_1": "unsere",
                            "person_2": "eure",
                            "person_3": {
                                "maskulin": "ihre",
                                "feminin": "Ihre",
                            }
                        }
                    },
                    "neutral": {
                        "singular": {
                            "person_1": "mein",
                            "person_2": "dein",
                            "person_3": {
                                "maskulin": "sein",
                                "feminin": "ihr",
                                "neutral": "sein"
                            }
                        },
                        "plural": {
                            "person_1": "unser",
                            "person_2": "euer",
                            "person_3": {
                                "maskulin": "ihr",
                                "feminin": "Ihr",
                            }
                        }
                    },
                    "plural": {
                        "singular": {
                            "person_1": "meine",
                            "person_2": "deine",
                            "person_3": {
                                "maskulin": "seine",
                                "feminin": "ihre",
                                "neutral": "seine"
                            }
                        },
                        "plural": {
                            "person_1": "unsere",
                            "person_2": "eure",
                            "person_3": {
                                "maskulin": "ihre",
                                "feminin": "Ihr",
                            }
                        }
                    }
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
        }


    def create_possesiv_artikel(
        self,
        fall: str,
        geschlecht_objekt: str,
        anzahl: str = None,
        person: str = None,
        geschlecht_subjekt: str = None
    ) -> str:
        grundformen: dict = {
            "singular": {
                "person_1": "mein",
                "person_2": "dein",
                "person_3": {
                    "maskulin_subjekt": "sein",
                    "feminin_subjekt": "ihr"
                }
            },
            "plural": {
                "person_1": "unser",
                "person_2": "euer",
                "person_2_no_e": "eur",
                "person_3": {
                    "maskulin_subjektiv": "ihr",
                    "feminin_subjektiv": "Ihr"
                }
            }
        }
        endungen: dict = {
            "nominativ": {
                "maskulin": "",
                "feminin": "e",
                "neutral": "",
                "plural": "e"
            },
            "akkusativ": {
                "maskulin": "en",
                "feminin": "e",
                "neutral": "",
                "plural": "e"
            },
            "dativ": {
                "maskulin": "em",
                "feminin": "er",
                "neutral": "em",
                "plural": "en"
            },
            "genitiv": {
                "maskulin": "es",
                "feminin": "er",
                "neutral": "es",
                "plural": "er"
            }
        }
        if anzahl == "plural" and person == "person_2" and not endungen[fall][geschlecht_objekt] == "":
            person = "person_2_no_e"
        try:
            possesiv_artikel: str = grundformen[anzahl][person][geschlecht_subjekt]
        except TypeError:
            possesiv_artikel: str = grundformen[anzahl][person]
        possesiv_artikel = f"{possesiv_artikel}{endungen[fall][geschlecht_objekt]}"
        return possesiv_artikel



if __name__=="__main__":
    # for testing
    lh_de = LanguageHandlerDE()

    print(lh_de.create_possesiv_artikel("dativ", "maskulin", "plural", "person_2", "neutral"))