# Рабочий - забирает картинки с сервера, распознает их и отдает обратно
import socket
import logging
import os

file_log = logging.FileHandler("client.log")
console_out = logging.StreamHandler()

logging.basicConfig(handlers=(file_log, console_out),
                    format='[%(asctime)s | %(levelname)s | CLIENT_3]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

# main_port
_port = 9094
_addr = 'localhost'
#scheduler_port = 9090
#scheduler_addr = '127.0.0.1'
#server_addr = '127.0.0.1'

def listen_tempo():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((_addr, 9091))
    sock.send('client_work'.encode())
    file = open("cl3/CLIENT_3_AUDIO.wav", "wb")
    while True:
        data = sock.recv(4096)
        file.write(data)
        if not data:
            file.close()
            break
            
    sock.close()
    logging.info("CLIENT 3 GOT FILE")

def my_start():
    logging.info("START Client3!")
    #send_result(result)
    listen_tempo()

def send_result(result):
    sock = socket.socket()
    sock.connect((_addr, _port))
    sock.send(result.encode())
    sock.close()
    logging.info("SENDED2 RESULT")

my_start()

