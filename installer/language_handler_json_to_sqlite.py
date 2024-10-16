"""This file turns all the json files into
one sqlite database with three tables."""

import sqlite3
import json

# Parameters:
PATH_TO_JSON_FILES = "language_handler_de_data_chunked"
PATH_TO_DATABASE = "data/test_language_handler_de_data.sqlite"
JSON_FILES = {
    "adjektive": ["adjektive_a-j", "adjektive_k-s", "adjektive_t-z"],
    "nomen": ["nomen"],
    "verben": ["verben_a", "verben_b-e", "verben_f-i", "verben_j-t", "verben_u-z"],
}


con = sqlite3.connect(PATH_TO_DATABASE)
cur = con.cursor()


for table, files in JSON_FILES.items():
    print(f"started to run on {table}.")
    for file in files:
        print(f"started to run on {file}")
        raw_data: list[dict] = json.load(
            open(f"{PATH_TO_JSON_FILES}/{file}.json")
        )  # loads data from json file
        for i in range(len(raw_data)):      #  strips the data of the last_modified
            raw_data[i].pop("last_modified")#  attribute, becuase it is irrelevant
        data: list[tuple] = [  # converts list of dicts to list of tuples of dict values
            tuple(j[1] for j in raw_data[i].items()) for i in range(len(raw_data))
        ]
        cur.executemany(f"INSERT INTO {table} VALUES(?, ?, ?, ?, ?)", data)
        con.commit()  # commits the changes to the database
