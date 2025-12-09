Atlantica is a text adventure, or as some may call it interactive fiction.

# Table of contents
- [Project state](#project-state)
- [The code](#the-code)
  - [The Parser](#the-parser)
    - [First stage](#first-stage)
    - [Second stage](#second-stage)
    - [Third stage](#third-stage)
  - [Game objects](#game-objects)
  - [Networking](#networking)
    - [client side](#the-client)
      - [client side commands](#client-side-commands)
    - [server side](#the-server)
      - [code](#server-side-code)
  - [Game state](#game-state)


# Project state
Atlantica is being rewritten with a different approach to the
game structure. It is now more focused on the parser, to have
a clean parsed input into the command executing method.
In this moment atlantica is not usable, but should be in the
future.

# The code
In the following is an outline of the theoratical functionalty of the code.

# The Parser:
The parser structure is (with small changes) from Raybert's Post https://groups.google.com/g/rec.arts.int-fiction/c/Y-S-bBojK7E/m/e-xy-z6WRfUJ

The sentences are imperative (The Implied subject is "I").
The sentence structure is:

\<verb>\<object>


## First stage:
Put Words into a list. (by splitting at spaces), convert all to lower case
Discard Articles

## Second stage:
If an "it" is found, it is replaced with the direct object from the sentence before   
remove classified words from list,
check for ANDs and THENs (they have special functions)
Classify the words:
First word is always a verb
// Verbs are also verbs with verb modifiers so also look at the second and last word to check for modifier (adverb).
Search the rest of the words (except for the last) for a preposition from the preposition list
(If a preposition is found, the word to the left is the direct object, the last word is the indirect object)
if no preposition is found, the last word is the object.
Before every object, there is one adjective allowed.
Check if there are non classified words. If there are, the input could not be interpreted

In sentences with ANDs, the sentence is copied, the verb stays and every new instance gets one of the
objects, that are seperated by the ANDs.  
In sentences with THENs, the sentence gets splited at the then and the two (or more) sentences are
executed one after the other.

If there is no object, the object is the player examples:

```bash
$> look # the player looks
```
## Third stage:
Match the objects in the sentence with game objects
game objects have the verb functions in them, match the verb with its
verb function and execute it, if possible, otherwise throw an error.

# Game Objects
Thing is the parent class for all things in the game. From thing muliple classes inherit like container, food and wapon.
The game objects have verb functions, functions that can be called by the user.

# Networking
Atlantica uses a client server model independent of the mode, for single player mode the
server does not have to open any ports on a network, it can just open the ports to the
localhost.

## The client
The client handles the first stage of [The Parser](#the-parser).
Then the client replaces all known aliases, with their values.
It also checks if the
string at index 0 matches a client side command. If the string does, the client executes the client
side command. Else the client sends the wordlist to the server.

### Client side commands
- connect to server (args: ip, port) > connects the client to the server
- set name (args: new name) > sets the player name, which will be used to connect to the server
- clear (args: none) > clears the screen
- quit game (args: none) > saves and exits the game
- add alias (args: what to alias, alias name) > add an alias to the aliases list
- print alias (args: none) > prints all aliases
- print help (args: none) > prints all available commands

## The server
The server handles the clients, as well as the game state. The server uses multithreading, to accept multiple clients. The server also handles the [second](#second-stage) and [third stage](#third-stage) of the [parser](#the-parser). The server code contains all [game object](#game-objects) classes.

### Server side code
- Thread 1
  - accept connection requests from new clients
  - create a new thread for every client
- Thread
  - handle the [game state](#game-state)
- Per client threads
  - handle the commands that the client sends
    - handle [second](#second-stage) and [third stage](#third-stage) of the [parser](#the-parser)
    - execute the commands and send replies to the user

# Game state
The game state describes the attributes of every object in the game, such as position (of the player, of an apple, of a sword...).
