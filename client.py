"""This is the client of atlantica, this programm
provides the user with an interface to the server, where
the relevant parts of the Game happen."""

# standard imports:
import socket
import threading
import json
from pathlib import Path
from base64 import b64encode
from base64 import b64decode
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.Cipher import ChaCha20_Poly1305

# local imports:
from handler import TerminalHandler

class Client():

    def __init__(self):
        # activate the terminal handler:
        self._terminal_handler = TerminalHandler()
        self._print = self._terminal_handler.new_print
        self._input = self._terminal_handler.new_input
        # load client data:
        self._aliases = self.load_dict("parser/aliases")
        self._name = self.load_string("user_data/name")
        self._user_side_methods: dict = {
                                        # user executable:
                                        "connect": self.connect_to_server,
                                        "set_name": self.set_name,
                                        "clear": self.clear,
                                        "quit": self.quit_game,
                                        "help": self.help,
                                        # executable by the server:
                                        # all server executable methods start with s_
                                        "s_print": self._print,
                                        "s_auth": self.s_auth
                                        }
        with open("game_data/help.json", "r", encoding="utf-8") as reader:
            self._help_dict: dict = json.loads(reader.read())
        # network stuff:
        self._active_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # set localhost as standard server:
        self._server_ip: str = "127.0.0.1"
        self._server_port: int = 27300
        # encryption variables:
        self._session_key: str = None
        self._private_key: RSA.RsaKey = self._load_private_key()
        self._public_key: str = self._load_public_key()
        self._is_connected_to_server: bool = False
        self._running: bool = True

    # private methods:

    def _create_rsa_identity(self) -> RSA.RsaKey:
        return RSA.generate(2048)

    def _create_identity(self) -> None:
        identity_path = Path(f"user_data/identities/{self._name}.pub")
        public_key_path = Path(f"user_data/identities/{self._name}.pub")
        private_key_path = Path(f"user_data/identities/{self._name}.key")
        key_pair = self._create_rsa_identity()
        with open(identity_path, "wb") as pub_writer:
            pub_writer.write(key_pair.public_key().export_key())
        with open(private_key_path, "wb") as priv_writer:
            priv_writer.write(key_pair.export_key())

    def _load_private_key(self) -> RSA.RsaKey:
        priv_key_path = Path(f"user_data/identities/{self._name}.key")
        if priv_key_path.exists():
            with open(priv_key_path, "rb") as reader:
                return RSA.import_key(reader.read())
        self._create_identity()
        return self._load_private_key()

    def _load_public_key(self) -> str:
        pub_key_path = Path(f"user_data/identities/{self._name}.pub")
        if pub_key_path.exists():
            with open(pub_key_path, "rb") as reader:
                return reader.read()
        self._create_identity()
        return self._load_public_key()

    def _rsa_decrypt(self, cipher_text:str) -> str:
        cipher = PKCS1_OAEP.new(self._private_key)
        return cipher.decrypt(cipher_text)

    def _chacha20_encrypt(self, message:str) -> str:
        data = message.encode("utf-8")
        key = self._session_key
        cipher = ChaCha20_Poly1305.new(key=key)
        cipher_text = b64encode(cipher.encrypt(data)).decode("utf-8")
        tag = b64encode(cipher.digest()).decode("utf-8")
        nonce = b64encode(cipher.nonce).decode("utf-8")
        encrypted_str = json.dumps([nonce, cipher_text, tag])
        return encrypted_str

    def _chacha20_decrypt(self, cipher_text:str) -> str:
        key = self._session_key
        encrypted: list = json.loads(cipher_text)
        nonce: str = b64decode(encrypted[0].encode("utf-8"))
        cipher_text: str = b64decode(encrypted[1].encode("utf-8"))
        tag: str = b64decode(encrypted[2].encode("utf-8"))
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        try:
            return cipher.decrypt_and_verify(cipher_text, tag)
        except ValueError:
            self._print("Warning: Failed to decrypt message from server")
            return

    # public methods:

    def execute_client_side_command(self, command_stage_one:list):
        if command_stage_one[0] in self._user_side_methods:
            if len(command_stage_one) > 1:
                if command_stage_one[1] == "help" or command_stage_one[1] == "?":
                    self.help(command_stage_one[0])
                else:
                    # call the method in element 0 of the list with other list elements as args:
                    self._user_side_methods[command_stage_one[0]](
                        *command_stage_one[1:]
                        )
            else:
                self._user_side_methods[command_stage_one[0]]()
        else:
            self._print(f"There is no command {command_stage_one[0]}")

    def main_offline(self):
        """Main method, if not connected to a
        server. Take user input, parse it and
        execute commands."""
        return_str = "Client terminated gracefully"
        try:
            while self._running:
                if not self._is_connected_to_server:
                    command_stage_one: list = self.get_user_input()
                    if command_stage_one[0].startswith("s_"):
                        self._print(
                        f"There is no user executable command {command_stage_one[0]}"
                        )
                    else:
                        self.execute_client_side_command(command_stage_one)
        except Exception as e:
            return_str = f"Client terminated with exception {e}"
        finally:
            self._terminal_handler.quit_terminal_handler()
            print(return_str)
            exit(0) # the game ends

    def main_online(self):
        st = threading.Thread(target=self.send_thread)
        st.daemon = True  # thread dies if main thread dies
        st.start()
        # creating the receive thread:
        rt = threading.Thread(target=self.receive_thread)
        rt.daemon = True
        rt.start()


    def send_thread(self):
        """Take user input, check for
        local executable commands and send the
        rest to the server."""
        prompt = f"{self._name}@{self._server_ip}$>"
        while self._is_connected_to_server:
            command_stage_one: list = self.get_user_input(prompt)
            if command_stage_one[0] in self._user_side_methods:
                self.execute_client_side_command(command_stage_one)
            else:
                self.send(command_stage_one)
        # thread dies

    def receive_thread(self):
        """Take the data received from the server
        and execute commands from that"""
        while self._is_connected_to_server:
            command_stage_one: list = self.receive()
            if not command_stage_one:
                self._print("Disconnected from the server")
                self._active_socket.close()  #  disconnect from server
                self._is_connected_to_server = False
                return  # thread dies
            self.execute_client_side_command(command_stage_one)
        # thread dies

    def get_user_input(self, prompt: str = "$>") -> list:
        """Asks the user for an input, until the user
        enters one. Then returns the input."""
        user_input = None
        while not user_input:
            user_input = self._input(prompt)
        return self.parser_stage_one(user_input)

    def parser_stage_one(self, input_str:str) -> list :
        """Convert the input string into a list of words"""
        # replace aliases with their values:
        for key, value in self._aliases.items():
            input_str = input_str.replace(key, value)
        # convert string into list of lower case words:
        return input_str.lower().split(" ")

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

####################
# Network methods: #
####################

    def send(self, data: list) -> None:
        """Sending data to the server"""
        data_enc = self._chacha20_encrypt(json.dumps(data))
        self._active_socket.sendall(data_enc.encode("utf-8"))

    def receive(self) -> list:
        "receives data from the server"
        incoming: str = self._active_socket.recv(2048)
        if not incoming:  # the server has disconnected
            return None
        data = self._chacha20_decrypt(incoming)
        return json.loads(data)

############################
# user executable methods: #
############################

    def connect_to_server(self, server: str = None, port: str = None):
        if not server:
            server = self._server_ip
        else:
            self._server_ip = server
        if not port:
            port = self._server_port
        else:
            try:
                port = int(port)
            except ValueError:
                self._print(
                    "Could not connect to server, the Port has to be an Integer."
                    )
        try:
            # connect to the server:
            self._active_socket.connect((server, port))
            self._active_socket.sendall(self._public_key)
            answer = self._active_socket.recv(2048)
            if not answer:
                self._print(f"Failed to connect to server: connection dropped")
                return
            self._session_key = self._rsa_decrypt(answer)
            self._is_connected_to_server = True
            self.main_online()
        except socket.error as e:
            self._print(f"Failed to connect to the server: {e}")

    def set_name(self, new_name:str=None):
        if not new_name:
            self.help("set_name")
            return
        self._name = new_name
        identity_path = Path(f"user_data/identities/{self._name}.pub")
        if not identity_path.exists():
            self._create_identity()
        self.dump_string("user_data/name", self._name)
        self._print(f"Changed name to {self._name}")

    def clear(self):
        self._terminal_handler.clear_screen()

    def quit_game(self):
        if self._is_connected_to_server:
            self.send(["/quit_game"])
        self._running = False

    def help(self, func_name:str = None):
        if not func_name:
            # add all local user executable methods, because they are always available:
            available_methods_help: dict = {
                key:value for key, value in self._user_side_methods.items()
                if not key.startswith("s_")
                }
            # add help strings to the dict
            for key in available_methods_help:
                available_methods_help[key] = self._help_dict["short"][key]
            # bring dict into alphabetical order
            available_methods_help = dict(sorted(available_methods_help.items()))
            # print the help
            for command, explanation in available_methods_help.items():
                self._print(f"{command} - {explanation}")
            # execute a server side help
            if self._is_connected_to_server:
                self.send(["help"])
        else:
            try:
                self._print(self._help_dict["long"][func_name])
            except KeyError:
                self._print(f"There is no help entry for {func_name}")

###############################
# server executeable methods: #
###############################

    def s_auth(self):
        self.send(["auth_response", self._name])

if __name__ == "__main__":
    client = Client()
    client.main_offline()

