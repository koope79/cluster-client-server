# Сервер - держатель общих данных, он их отдает и сохраняет процессобезопасно
import os
import logging
import socket
import multiprocessing
import time

file_log = logging.FileHandler("server.log")
console_out = logging.StreamHandler()

logging.basicConfig(handlers=(file_log, console_out),
                    format='[%(asctime)s | %(levelname)s | SERVER]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

ports = []

scheduler_port = 9090
resultsData = []

# общие данные
manager = multiprocessing.Manager()
# TODO fix it
result = manager.list([0])
# TODO fix it
free_images = manager.list([0])
shapes = manager.list()

# для каждой операции свой лок, т.к. общие данные не пересакаются в разных операциях
returnLock = multiprocessing.Lock()
getLock = multiprocessing.Lock()


def start_server(_ports):
    # записываем порты
    global free_images
    global shapes
    ports = _ports
    time.sleep(1)
    listen(ports)


# основной обработчик задач от клиентов
def listen_process(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, port))
    logging.info("Creating_server_ports..")
    sock.listen(1)
    while True:
        conn, addr = sock.accept()
        logging.info("Connected: " + str(addr))
        
        data = conn.recv(1024)
        logging.info("SERVER Command " + data.decode() + " from " + str(addr))
        
        if not data:
            logging.error("Connection with " + str(addr) + " will be closed. Data not found")
            break
        
        if data.decode() == 'push_audio':
            logging.info("No DATA")
            break
        
        result.append(data.decode())
        
        print('RESULTSDATA: ', result)
        #logging.info("Connection with " + str(addr) + " will be closed")
        #close_port(port, conn)


def close_port(port, conn):
    port = port
    conn.close()
    sock = socket.socket()
    sock.connect(('', scheduler_port))
    sock.send('return_port'.encode())
    resp = sock.recv(5)
    # TODO а если не ready
    logging.info("Scheduler answer: {}".format(resp.decode()))
    if resp.decode() == 'ready':
        sock.send(port.to_bytes(3, 'big'))
    sock.close()


# запускаем на каждом порту в пуле прослушивание. Каждый порт слушает в отдельном процессе
def listen(ports):
    process = []
    for i in ports:
        main_process = multiprocessing.Process(target=listen_process, args=('', i))
        main_process.start()
        process.append(main_process)
        logging.info("Started processing on port {} ".format(i))

    #TODO вынести в функцию или класс

    # сообщаем планировщику, что все процессы запустились и можно продолжать работу
    sock = socket.socket()
    sock.connect(('', scheduler_port))
    sock.send('port_created'.encode())
    sock.close()
    for i in process:
        # ожидаем завершения процессов, иначе общие данные пропадут (Manager умирает при убивании основного процесса)
        i.join()

