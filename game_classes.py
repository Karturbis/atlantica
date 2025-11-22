"""All classes for game participants, such as
items and players."""

class Thing():

    def __init__(self):
        self.export_verbs()

    def export_verbs(self) -> None:
        """create a list of verbs in the current class
        all verbs are methods, which start with v_.
        add the verbs to the verbs file."""
        self_verbs: list = [method[2:] for method in dir(self) if
                callable(getattr(self, method))
                and method.startswith("v_")
                ]
        with open("parser/verbs", "r", encoding="utf-8") as reader:
            file_verbs: list = reader.readlines()
        # add only verbs to file, wich it does not contain yet
        verbs_to_add: list = [verb for verb in self_verbs and not verb in file_verbs]
        with open("parser/verbs", "a", encoding="utf-8") as writer:
            writer.writelines(verbs_to_add)


class Food(Thing):

    def __init__(self):
        pass


class Apple(Food):

    def __init__(self):
        pass


class Potato(Food):

    def __init__(self):
        pass


class Weapon(Thing):

    def __init__(self):
        pass


class MeeleWeapon(Weapon):

    def __init__(self):
        pass


class Sword(MeeleWeapon):

    def __init__(self):
        pass


class Axe(MeeleWeapon):

    def __init__(self):
        pass


class RangeWeapon(Weapon):

    def __init__(self):
        pass


class Bow(RangeWeapon):

    def __init__(self):
        pass


class Player():

    def __init__(self):
        pass