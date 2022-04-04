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
result = manager.list([0])

# для каждой операции свой лок, т.к. общие данные не пересакаются в разных операциях
returnLock = multiprocessing.Lock()
getLock = multiprocessing.Lock()


def start_server(_ports):
    # записываем порты
    ports = _ports
    time.sleep(1)
    listen(ports)

def tempo_port(ip, temp_port, file_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, temp_port))
    sock.listen()
    file = open(file_name, "rb")
    logging.info("Started Tempo_Port 9091!")
    while True:
        conn, addr = sock.accept()
        res = conn.recv(4096)
        
        if res.decode() == 'client2_work':
            while True:
                file_data = file.read(4096)
                conn.send(file_data)
                if not file_data:
                    break
            conn.close()
            logging.info("FILE SENDED FROM TEMPO")

def create_tempo_port(file_name):
    tempo_process = multiprocessing.Process(target=tempo_port, args=('', 9091, file_name))
    tempo_process.start()
    #tempo_process.join()

# основной обработчик задач от клиентов
def listen_process(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, port))
    logging.info("Created server port {}!".format(port))
    sock.listen(1)
    file_name = "TEST1.wav"
    file = open(file_name, "wb")
    while True:
        conn, addr = sock.accept()
        logging.info("Connected: " + str(addr))
            
        while True:
            data = conn.recv(4096)
            #logging.info(type(data))
            try:
                if data.decode():
                    logging.info("SERVER Command " + data.decode() + " from " + str(addr))
                    break
                    
            except Exception:
                file.write(data)
                if not data:
                    break
            finally:
                if not data:
                    logging.info("AUDIO FILE ON SERVER")
                    file.close()
                    time.sleep(1)
                    create_tempo_port(file_name)
                    sock = socket.socket()
                    sock.connect(('', scheduler_port))
                    sock.send('got_file_from_client'.encode())
                    sock.close()
                    break
                    
        #result.append(data.decode())
        
        #print('RESULTSDATA: ', result)
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

    #TODO вынести в функцию или класс

    # сообщаем планировщику, что все процессы запустились и можно продолжать работу
    sock = socket.socket()
    sock.connect(('', scheduler_port))
    sock.send('port_created'.encode())
    sock.close()
    for i in process:
        # ожидаем завершения процессов, иначе общие данные пропадут (Manager умирает при убивании основного процесса)
        i.join()

