from handler import network_handler
from os import system

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

    def user_input_get_command(self):
        user_in = input("input$> ").split(" ")
        if len(user_in) > 1:
            return user_in[0], user_in[1:]
        # else:
        return user_in[0], []

    def func1(self):
        print("func!1")

    def new_print(self, data):
        system("clear")
        print(data)


    def fancy_func(self, data):
        print(f"FANC>!{data}")
        return "fanxcy"

if __name__ == "__main__":
    mainle = Main()
    client = network_handler.Client(mainle.main)
    client.main()
