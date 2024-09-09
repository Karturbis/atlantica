import sqlite3
import json

lines = 12

with open("language_handler_de_data/verben_0-500000.json", "r") as reader:
    data = json.load(reader)

print(data)