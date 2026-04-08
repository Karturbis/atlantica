"""This file contains the decorators needed for the game_classes.py file."""

def gets_items_from_inventory(func):
    """decorator for all verbs, that only get
    items from the players inventory"""
    def wrapper(self, game_state, direct_noun, direct_adjective, *args, **kwargs):
        matching_objects = self._get_item_id_from_inventory(game_state, direct_noun, direct_adjective)
        len_matching_objects = len(matching_objects)
        if len_matching_objects == 1:
            return func(self, game_state, matching_objects[0], *args, **kwargs)
        if len_matching_objects > 1:
            return {"clien_print": f"There are multiple items called {direct_noun}, please use an adjective."}
        # len_matching_objects == 0:
        return {"client_print": f"There is no item calles {direct_noun} in your vicinity"}
    return wrapper

def gets_items_from_room(func):
    """decorator for all verbs, that only
    get items from the room, the player
    is currently inside"""
    def wrapper(self, game_state, direct_noun, direct_adjective, *args, **kwargs):
        matching_objects = self._get_item_id_from_room(game_state, direct_noun, direct_adjective)
        len_matching_objects = len(matching_objects)
        if len_matching_objects == 1:
            return func(self, game_state, matching_objects[0], *args, **kwargs)
        if len_matching_objects > 1:
            return {"clien_print": f"There are multiple items called {direct_noun}, please use an adjective."}
        # len_matching_objects == 0:
        return {"client_print": f"There is no item calles {direct_noun} in your vicinity"}
    return wrapper

def gets_items_from_all(func):
    """decorator for all verbs, that
    use items from the room and the inventory"""
    def wrapper(self, game_state, direct_noun, direct_adjective, *args, **kwargs):
        matching_objects = self._get_item_id_from_inventory(game_state, direct_noun, direct_adjective)
        matching_objects += self._get_item_id_from_room(game_state, direct_noun, direct_adjective)
        len_matching_objects = len(matching_objects)
        if len_matching_objects == 1:
            return func(self, game_state, matching_objects[0], *args, **kwargs)
        if len_matching_objects > 1:
            return {"clien_print": f"There are multiple items called {direct_noun}, please use an adjective."}
        # len_matching_objects == 0:
        return {"client_print": f"There is no item calles {direct_noun} in your vicinity"}
    return wrapper

