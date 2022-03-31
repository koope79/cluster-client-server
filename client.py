# Рабочий - забирает картинки с сервера, распознает их и отдает обратно
import socket
import sys
import dlib
import cv2
import logging
import util

file_log = logging.FileHandler("client.log")
console_out = logging.StreamHandler()

logging.basicConfig(handlers=(file_log, console_out),
                    format='[%(asctime)s | %(levelname)s | CLIENT]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

# main_port
scheduler_port = 9090
scheduler_addr = '127.0.0.1'
server_addr = '127.0.0.1'

# Рабочие не спят, работают 24/7
# TODO сделать местный kill
def start_job():
    while True:
        sock = socket.socket()
        # Хотим выделенный порт для работы
        port = get_port(sock)
        sock.close()

        # Хотим картинку
        sock = socket.socket()
        arr, shape = get_img(sock, port)

        # Распознаем
        logging.info("Start detect...")
        detect(arr)
        logging.info("Detected!")

        # Снова получаем порт для работы
        sock = socket.socket()
        port = get_port(sock)
        sock.close()
        # Возвращаем назад картинку
        sock = socket.socket()
        return_img(sock, port, shape, arr)


def return_img(sock, port, shape, arr):
    logging.info("Start return img")
    # Коннектимся к выделенному порту
    sock.connect((server_addr, port))

    sock.send('return'.encode())
    resp = sock.recv(5)
    # TODO а если не ready
    if resp.decode() == 'ready':
        logging.info("...return...")
        send_img(shape, sock, arr)


def get_port(sock):
    # Коннектимся к основному порту планировщика
    logging.info("Connect to Addr: {}, port: {} for get port".format(scheduler_addr, scheduler_port))
    sock.connect((scheduler_addr, scheduler_port))
    # Хотим выделенный порт для работы
    sock.send('get_port'.encode())
    return int.from_bytes(sock.recv(3), 'big')


def get_img(sock, port):
    # Коннектимся к выделенному порту
    logging.info("Connect to Addr: {}, port: {} for get_img".format(server_addr, port))
    sock.connect((server_addr, port))
    sock.send('get'.encode())
    shape1 = sock.recv(3)
    shape2 = sock.recv(3)
    shape3 = sock.recv(3)
    shape = (int.from_bytes(shape1, 'big'), int.from_bytes(shape2, 'big'), int.from_bytes(shape3, 'big'))
    logging.info("Start read img...")
    data = sock.recv(1024)
    # TODO
    if not data:
        logging.info("Kill client process...")
        while True:
            pass

    logging.info("...read...")
    arr = util.read_data(data, sock, shape)
    logging.info("Stop read img")
    sock.close()
    return arr, shape


def detect(arr):
    detector = dlib.get_frontal_face_detector()
    logging.info(len(arr.tobytes()))
    faces = detector(arr, 1)
    max_face = max(faces, key=lambda rect: rect.width() * rect.height())
    draw_rectangle(faces, max_face, arr)


def send_img(shape, sock, arr):
    for i in shape:
        sock.send(i.to_bytes(3, 'big'))
    arr = arr.astype('float32')
    arr = arr.tobytes()
    sock.sendall(arr)


def draw_rectangle(faces, max_face, arr):
    for f in faces:
        if f == max_face:
            cv2.rectangle(arr, (f.left(), f.top()), (f.right(), f.bottom()), (0, 0, 255), 2)
        else:
            cv2.rectangle(arr, (f.left(), f.top()), (f.right(), f.bottom()), (255, 0, 0), 2)


start_job()
