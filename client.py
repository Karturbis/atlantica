"""This is the client of atlantica, this programm
provides the user with an interface to the server, where
the relevant parts of the Game happen."""

from threading import Thread

# local imports:
from parser import stage_one

class Client():

    def __init__(self):
        self.__aliases = self.load_aliases()

    def main(self):
        running = True
        while running:
            user_input = input("$> ")
            command_stage_one: str = stage_one(user_input, self.__aliases)

    def load_aliases(self) -> dict:
        """Loads the aliases from the aliases
        file and writing returning them as a dict."""
        seperator: str = ":"
        start_comment: str = "#"
        alias_file_path: str = "user_data/aliases"
        with open(alias_file_path, "r", encoding="utf-8") as reader:
            lines: list = reader.readlines()
            return_dict: dict = {}
            for line in lines:
                if not line.startswith(start_comment):
                    line = line.strip("\n").split(seperator)
                    return_dict[line[0]] = line[1]
            return return_dict


############################
# user executable methods: #
############################

    def connect_to_server(self, ip, port):
        pass

    def set_name(self, new_name):
        pass

    def clear(self):
        pass

    def quit_game(self):
        pass



if __name__ == "__main__":

    client = Client()
    client.main()