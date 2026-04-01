# Game classes
The game_classes.py file contains all "ingame" classes and their parents, such as
items, rooms and players. These classes contain normal methods and verbs.

## Verbs
Verbs are
methods, wich start with a v_ and are meant to be executed by the player. All verbs
must take all keyword arguments they are given without errors. If a verb needs any
arguments, it should catch the keyword arrguments with **kwargs and cherrypick the
values it needs. If a verb does not need any argument, the keyword arguments should
be omitted by using **_ as an argument to the method.