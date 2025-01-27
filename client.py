from os import system

from handler import TerminalHandler
from handler import network_handler

class Main():

    def __init__(self):
        pass

    def main(self, command, args = None):
        if not args:
            args = []
        func = getattr(self, command)
        if len(args) >= 1:
            return func(*args)
        else:
            return func()

    def user_input_get_command(self, prompt="input$>"):
        user_in = input(f"{prompt} ").split(" ")
        if len(user_in) > 1:
            return user_in[0], user_in[1:]
        # else:
        return user_in[0], []

    def func1(self):
        print("func!1")

    def new_print(self, data):
        system("clear")
        print(data)

if __name__ == "__main__":
    mainle = Main()
    client = network_handler.Client(mainle.main)
    client.main()
