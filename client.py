from handler import TerminalHandler
from handler import NetworkHandler
from handler import InputHandler
from handler import NetworkPacket

class Client():

    def __init__(self):
        self.__name = "test"

    def connect_to_server(self, *args):
        #server_adress = input("Input the Server you want to join: ").split(":")
        server_adress = ["192.168.178.45"]
        if len(server_adress) > 1:
            server_port = int(server_adress[1])
        else:
            server_port = 27300
        server_ip = server_adress[0]
        answer = network_handler.init_client(server_ip, server_port)
        name_request = network_handler.send_data(answer)
        if (name_request.packet_class == "network_command"
        and name_request.data == "get_character_name"):
            return network_handler.send_data(
                NetworkPacket(
                    packet_class="reply", data=self.__name
                    )
                )

    def start_server(self):
        pass

    def single_player(self):
        pass

    def quit_game(self, args=None) -> None:
        """Saves and quits the game."""
        network_handler.send_command(network_handler.aktive_socket, "save")
        exit("Good bye, see you next time in Atlantica!")

    def print_inventory(self, args=None) -> None:
        """Outprints the Inventory, mark
        which item is equiped."""
        inventory = network_handler.send_command(network_handler.aktive_socket, "get_inventory")
        if inventory:
            TerminalHandler.new_print("Your inventory contains:",)
            for key, value in inventory.items():
                if value:  # check, if item is eqiupped
                    TerminalHandler.new_print(f"{key[5:]} - equipped")
                else:
                    TerminalHandler.new_print(key[5:])
        else:
            TerminalHandler.new_print("Your inventory is empty.")

    def set_name(self, name=None):
        if not name:
            print("You need to input a name")
        else:
            self.__name = name

    def print_help(self, args=None) -> None:
        """Outprints all available commands."""
        print("Available commands:\n")
        for key in input_handler.get_commands_avail():
            print(key)
        print()

client = Client()
network_handler = NetworkHandler()
input_handler = InputHandler(
    client,
    {
        "clear": ["TerminalHandler", "clear"],
        "singleplayer": ["main", "single_player"],
        "startserver": ["main", "start_server"],
        "joinserver": ["main", "connect_to_server"],
        "help": ["main", "print_help"],
        "setname": ["main", "set_name"],
    })

input_handler.input_loop()
