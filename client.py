"""This is the client of atlantica, this programm
provides the user with an interface to the server, where
the relevant parts of the Game happen."""

from threading import Thread

class Client():

    def __init__(self):
        self._aliases = self.load_dict("parser/aliases")
        self._name = self.load_string("user_data/name")
        self._user_side_methods: dict = {
                                        "connect": self.connect_to_server,
                                        "set_name": self.set_name,
                                        "clear": self.clear,
                                        "quit": self.quit_game,
                                        }
        self._is_connected_to_server: bool = False

    def main_offline(self):
        """Main method, if not connected to a
        server. Take user input, parse it and
        execute commands."""
        while not self._is_connected_to_server:
            user_input = input("$> ")
            command_stage_one: list = self.parser_stage_one(user_input)
            if command_stage_one[0] in self._user_side_methods:
                # call the method in element 0 of the list with other list elements as args:
                self._user_side_methods[command_stage_one[0]](*command_stage_one[1:])


    def parser_stage_one(self, input_str:str) -> list :
        """Convert the input string into a list of words"""
        # replace aliases with their values:
        for key, value in self._aliases.items():
            input_str = input_str.replace(key, value)
        # convert string into list of lower case words:
        return input_str.lower().split()

    def load_string(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as reader:
            return reader.readline()

    def dump_string(self, file_path: str, data: str) -> None:
        with open(file_path, "w", encoding="utf-8") as writer:
            writer.write(data)

    def load_dict(self, file_path: str) -> dict:
        """Loads the a dict from the given file
        and returning them as a dict."""
        seperator: str = ":"
        start_comment: str = "#"
        with open(file_path, "r", encoding="utf-8") as reader:
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
        self._name = new_name
        self.dump_string("user_data/name", new_name)
        print(f"Changed name to {self._name}.")

    def clear(self):
        pass

    def quit_game(self):
        pass


if __name__ == "__main__":

    client = Client()
    client.main_offline()
