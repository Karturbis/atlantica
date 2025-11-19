# Project description:

As of right now, atlcantica is an unfinished text adventure.

At the moment functional:

start a server by executing server.py
start the client by executing client.py

connecting to the server using join command

Ingame (connected to the server):
Go in every direction,
rest (does no really do anything yet),
pickup items,
equip items, unequip items,
drop Items,
list inventory,
quit (saves the game and exits),
inspect (See all items in current Chunk),
help (print all available commands),
eat (removes item from inventory and adds
nutrition value of item to saturation value of the player).
disconnect (disconnects from server)

# Installation:
### General
1) Download the code as zip file, or git clone the code
2) In the project folder create a directory named 'saves'
### Linux
1) Create virtual environment,
Activate virtual environment
```bash
python3 -m venv atlantica venv
```
2) Install dependencies
```bash
python3 -m pip install -r requirements.txt
```
### Windows
1) Install dependencies
```bash
python -m pip install -r requirements.txt
```

# Run the game:
1) Run the server.py file
2) In another terminal, run the client.py file
