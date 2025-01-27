from handler import network_handler

class ServerMethods():

    def __init__(self, connection, connection_id):
        self.__connection = connection
        self.__connection_id = connection_id

    def main(self, command, args):
        if not args:
            args = []
        try:
            func = getattr(self, command)
        except AttributeError:
            return f"There is no command called {command}"
        if len(args) >= 1:
                return func(*args)
        else:
                return func()

    def fanf(self):
        packet = network_handler.NetworkPacket(
            packet_type="command",
            command_name="new_print",
            command_attributes=["DATA"]
        )
        server.send_packet(packet, self.__connection)
        return "end_of_command"

    def new_print(self, data):
        return f"nPP{data}"


thread_data = network_handler.ThreadData()
server = network_handler.Server(thread_data, ServerMethods)
server.main()
