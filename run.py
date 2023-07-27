import sys
import threading
from subprocess import Popen
import socket


class RTSPServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

        self.clients = []

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ip, port))
        sock.listen(5)

        print(f'Listening on rtsp://{ip}:{port}')

        threading.Thread(target=self.listen, args=(sock,)).start()

    def listen(self, sock):
        while True:
            client, addr = sock.accept()
            self.clients.append(client)

            threading.Thread(target=self.handle_client, args=(client, addr)).start()

    @staticmethod
    def handle_client(client, addr):
        print(f'New client joined: {addr}')

        client.send(b'RTSP/1.0 200 OK\n')

        while True:
            data = client.recv(1024)

            if not data:
                break

            # Обрабатываем RTSP запросы от клиента

            client.send(b'RTSP/1.0 200 OK\n')

        client.close()
        print(f'Client disconnected: {addr}')


def draw_overlay(output_stream):
    while True:
        try:
            overlay_process = Popen(['ffmpeg', '-i', f'{output_stream}/test', '-vf',
                                     'drawtext=text=\'Hello World!\':x=20:y=80:fontsize=20:fontcolor=white',
                                     '-codec', 'copy', f'{output_stream}/overlay'])
        except Exception as e:
            print('Error:', e)
            if overlay_process.poll() is None:
                overlay_process.kill()


def stream(in_url, server):
    Popen(['ffmpeg', '-i', in_url, '-f', 'rtsp', '-rtsp_transport', 'tcp',
           f'rtsp://{server.ip}:{server.port}/test'])

    output_stream = f'rtsp://{server.ip}:{server.port}'
    draw_overlay(output_stream)


if __name__ == '__main__':
    in_url = sys.argv[1]
    port = int(sys.argv[2])

    server = RTSPServer('localhost', port)
    stream(in_url, server)
