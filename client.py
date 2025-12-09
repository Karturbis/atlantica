"""This is the client of atlantica, this programm
provides the user with an interface to the server, where
the relevant parts of the Game happen."""

from threading import Thread

class Client():

    def __init__(self):
        self._aliases = self.load_aliases()

    def main(self):
        running = True
        while running:
            user_input = input("$> ")
            command_stage_one: str = self.parser_stage_one(user_input)
            #TODO: implement connection with server

    def parser_stage_one(self, input_str:str) -> list :
        """Convert the input string into a list of words"""
        # replace aliases with their values:
        for key, value in self._aliases.items():
            input_str = input_str.replace(key, value)
        # convert string into list of lower case words:
        return input_str.lower().split()

    def load_aliases(self) -> dict:
        """Loads the aliases from the aliases
        file and writing returning them as a dict."""
        seperator: str = ":"
        start_comment: str = "#"
        alias_file_path: str = "parser/aliases"
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