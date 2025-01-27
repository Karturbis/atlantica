import time

from inspect import signature

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
        given_args_len = len(args)
        expected_args_len = len(signature(func).parameters)
        if given_args_len >= 1:
            if expected_args_len == given_args_len:
                # run method:
                try:
                    return func(*args)
                except Exception as e:
                    return f"ERROR in ServerMethods.main: {e}"
            else: # wrong number of arguments were given
                return f"Command {command} takes {expected_args_len} arguments, you gave {given_args_len}."
        else:  # no args where given:
            if expected_args_len == given_args_len:
                # run method:
                try:
                    return func()
                except Exception as e:
                    return f"ERROR in ServerMethods.main: {e}"
            else: # wrong number of arguments were given
                return f"Command {command} takes {expected_args_len} arguments, you gave {given_args_len}."

    def fanf(self):
        packet = network_handler.NetworkPacket(
            packet_type="command",
            command_name="new_print",
            command_attributes=["DATA"]
        )
        server.send_packet(packet, self.__connection)
        return "end_of_command"

    def ping(self):
        return f"Time:{time.time_ns()}"


thread_data = network_handler.ThreadData()
server = network_handler.NetworkServer(thread_data, ServerMethods)

if __name__ == "__main__":
    server.main()
