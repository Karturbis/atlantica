
# Table of contents
- [Project state](#project-state)
- [The Parser](./parser.md)
    - [First stage](./parser.md#first-stage)
    - [Second stage](./parser.md#second-stage)
    - [Third stage](./parser.md#third-stage)
- [Game objects](#game-objects)
- [Networking](./networking.md)
    - [client side](./networking.md#the-client)
    - [client side commands](./networking.md#client-side-commands)
    - [server side](./networking.md#the-server)
    - [server side code](./networking.md#server-side-code)
- [Game state](#game-state)

# Project state
Atlantica is being rewritten with a different approach to the
game structure. It is now more focused on the parser, to have
a clean parsed input into the command executing method.
In this moment atlantica is not usable. 

# Game Objects
Thing is the parent class for all things in the game. From thing muliple classes inherit like container, food and wapon.
The game objects have verb functions, functions that can be called by the user.

# Game state
The game state describes the attributes of every object in the game, such as position (of the player, of an apple, of a sword...).

# Game classes
These are all Objects in the game. All items inherit from Thing.