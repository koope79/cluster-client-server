# Рабочий - забирает картинки с сервера, распознает их и отдает обратно
import socket
import logging

file_log = logging.FileHandler("client.log")
console_out = logging.StreamHandler()

logging.basicConfig(handlers=(file_log, console_out),
                    format='[%(asctime)s | %(levelname)s | CLIENT_1]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

# main_port
_port = 9092
_addr = 'localhost'
#scheduler_port = 9090
#scheduler_addr = '127.0.0.1'
#server_addr = '127.0.0.1'

# Рабочие не спят, работают 24/7
# TODO сделать местный kill

def my_start():
    logging.info("START Client1!")
    #result = 'push_audioy'
    #send_result(result)
    send_audio()


def send_audio():
    sock = socket.socket()
    sock.connect((_addr, _port))
    file = open("rec1.wav", "rb")
    while True:
        file_data = file.read(4096)
        sock.send(file_data)
        if not file_data:
            break
    sock.close()
    logging.info("File Sended")

def send_result(result):
    sock = socket.socket()
    sock.connect((_addr, _port))
    sock.send(result.encode())
    sock.close()
    logging.info("SENDED1 RESULT")

def create_sock():
    sock = socket.socket()
    

my_start()


