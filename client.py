from handler import network_handler

import client_methods


class Client():

    def __init__(self):
        pass

    def connect_to_server(self, server_ip: str, server_port:int=27300):
        cl_methods = client_methods.Client_Methods()
        client = network_handler.NetworkClient(cl_methods.main, server_ip, server_port)
        client.main()
