import os
import sys
import socket

class MpvIPCClient:
    def __init__(self, path):
        self.path = path 

    def _connect_and_send(self, value):
        with socket.socket(socket.AF_UNIX) as sock:

            # connect to the ipc:unix_socket
            
            try:
                sock.connect(self.path)
            except ConnectionRefusedError:
                # It means the socket file is there
                return print('[IPC]: socket is not accessible') 
            
            except FileNotFoundError:
                return print('[IPC]: socket is not found')

            # Send the command
            command = '{}\r\n'.format(value)
            return sock.send(command.encode())

    def toggle_pause(self):
        # Pause the mpv instance
        return self._connect_and_send('cycle pause')

    def toggle_mute(self):
        # Toggle mute the current mpv instance
        return self._connect_and_send('cycle mute')

    def toggle_loop(self):
        return self._connect_and_send('cycle loop-file')

    def set_voluem(self, amount=10):
        # Increase volume by x percent(default 10)
        return self._connect_and_send('set volume {}'.format(amount))



