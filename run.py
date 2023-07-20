import sys
import threading
from subprocess import Popen
import socket

import cv2


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


def draw_on_frame(frame):
    # Рисуем прямоугольник
    cv2.rectangle(frame, (10, 10), (100, 100), (0, 255, 0), 2)

    # Добавляем текст
    cv2.putText(frame, 'Hello World!', (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


def stream(in_url, server):
    Popen(['ffmpeg', '-i', in_url, '-f', 'rtsp', '-rtsp_transport', 'tcp',
           f'rtsp://{server.ip}:{server.port}/test'])

    cap = cv2.VideoCapture(f'rtsp://{server.ip}:{server.port}/test')

    while True:
        ret, frame = cap.read()

        if ret:
            draw_on_frame(frame)

            # Кодирование кадра в JPEG
            frame = cv2.imencode('.jpg', frame)[1].tobytes()

            for client in server.clients:
                client.send(frame)

        else:
            break


if __name__ == '__main__':
    in_url = sys.argv[1]
    port = int(sys.argv[2])

    server = RTSPServer('localhost', port)
    stream(in_url, server)
