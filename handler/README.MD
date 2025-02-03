network_handler command chain:


If command is local on server and does not need
any additional data from client:
    Server:                     Client:

1) Waits for commands          send command
2) execute command             wait for reply
3) send reply                  receive reply
4) start with 1)               start with 1)

If command does need data from client, but client
command is local and needs no extra data from server:
    Server:                     Client

1) Waits for commands          send command
2) execute command             wait for reply/command
    2.1)send command           execute command
    2.3)wait for reply         send command output back
    2.4)do stuff with reply    wait for reply/command
    2.5)if finished sending    if reply is a "end_of_command"
        commands, send:        reply package, go to next step
        "end_of_command"
        reply package.
3) send reply                  receive reply
4) start with 1)               start with 1)
