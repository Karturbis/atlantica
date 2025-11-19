"""Data classes"""


class Container:
    """A Container is an element in a Chunk,
    which contains Items or triggers Events,
    when inspected."""

    def __init__(
        self, container_id: str, items: list, events: str, description: str
    ) -> None:
        self.__container_id: str = container_id
        self.__items: list = items
        self.__events: list = events
        self.__description: str = description

    def get_items(self) -> list:
        """Returns a list of the
        ids of the items, which
        are in the Container."""
        return self.__items

    def get_events(self) -> list:
        """Returns a list of event
        ids, of the containers' events."""
        return self.__events

    def get_description(self) -> str:
        """Returns the description
        of the container."""
        return self.__description


class Item:
    """An Item is a small objekt,
    that can be found in atlanctica.
    Items are spawning in Chunks, in
    Containers and when enemys die.
    Examples for an Item would be:
    sword, apple, axe, lantern..."""

    def __init__(
        self,
        item_id: str,
        nutrition: int,
        description: str,
        damage: int,
        crit_damage: int,
    ) -> None:
        self.__item_id: str = item_id
        self.__nutrition: int = nutrition
        self.__description: str = description
        self.__damage: int = damage
        self.__crit_damage: int = crit_damage

    def get_nutrition(self) -> int:
        return self.__nutrition

    def get_description(self) -> str:
        return self.__description

    def get_damage(self) -> int:
        return self.__damage

    def get_crit_damage(self) -> int:
        return self.__crit_damage


class Chunk:
    """A Chunk is the coordinates
    unit. Every Chunk contains some
    stuff e.g items, characters (can be
    good or evil), or Containers.
    Every Chunk has the data about which
    Chunks are next to it so when the player
    walks, the current Chunk has the information
    about what will be the next Chunk."""

    def __init__(
        self,
        chunk_id: str = None,
        north_chunk_id: str = None,
        east_chunk_id: str = None,
        south_chunk_id: str = None,
        west_chunk_id: str = None,
        description: str = None,
        items: str = None,
        characters: str = None,
        containers: list = None,
        add_commands: str = None,
        rem_commands: str = None,
    ) -> None:
        self.__chunk_id: str = chunk_id
        self.__north_chunk_id: str = north_chunk_id
        self.__east_chunk_id: str = east_chunk_id
        self.__south_chunk_id: str = south_chunk_id
        self.__west_chunk_id: str = west_chunk_id
        self.__description: str = description
        if items:
            self.__items: list = items.split(", ")
        else:
            self.__items: list = []
        if containers:
            self.__containers: list = containers.split(", ")
        else:
            self.__containers: list = []
        if characters:
            self.__characters: list = characters.split(", ")
        else:
            self.__characters: list = []
        self.__add_commands = add_commands
        self.__rem_commands = rem_commands

    def get_chunk_id(self) -> str:
        """Returns the id of the current chunk"""
        return self.__chunk_id

    def get_north_chunk_id(self) -> str:
        """Returns the chunk_id of
        the chunk, which lays NORTH of
        the current chunk."""
        return self.__north_chunk_id

    def get_east_chunk_id(self) -> str:
        """Returns the chunk_id of
        the chunk, which lays EAST of
        the current chunk."""
        return self.__east_chunk_id

    def get_south_chunk_id(self) -> str:
        """Returns the chunk_id of
        the chunk, which lays SOUTH of
        the current chunk."""
        return self.__south_chunk_id

    def get_west_chunk_id(self) -> str:
        """Returns the chunk_id of
        the chunk, which lays WEST of
        the current chunk."""
        return self.__west_chunk_id

    def get_description(self) -> str:
        """Returns the descriptio
        of the current chunk."""
        return self.__description

    def get_containers(self) -> list:
        return self.__containers

    def get_items(self) -> list:
        """Returns a list of items,
        that the current chunk
        contains at the moment."""
        return self.__items

    def remove_item(self, item: str) -> None:
        """Removes an Item from a Chunk"""
        self.__items.remove(item)

    def add_item(self, item: str) -> None:
        """Add an Item to a Chunk"""
        self.__items.append(item)

    def get_characters(self) -> list:
        """Returns a list of Characters,
        that the current chunk contains."""
        return self.__characters

    def get_add_commands(self) -> dict:
        """Returns the not standard commands,
        which are possible to be executed
        within the current Chunk."""
        return self.__add_commands

    def get_rem_commands(self) -> dict:
        """Returns the standart commands,
        which can not be used within
        the current Chunk"""
        return self.__rem_commands