# Atlantica
Atlantica is a text adventure, or as some may call it interactive fiction.

# Project state
The project is in development right now, it is not possible to play at the
moment.

# Project architecture
Atlantica is a server client program with planned multi player support.
The server is the source of truth and runs most commands the user enters.
Commands which can be run on the client must be unimportant for the game
state, such as clearing the screen and getting help information on commands.