# Сервер - держатель общих данных, он их отдает и сохраняет процессобезопасно
import os
import logging
import socket
import multiprocessing
import time
from _thread import start_new_thread

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
result = manager.list()

# для каждой операции свой лок, т.к. общие данные не пересакаются в разных операциях
returnLock = multiprocessing.Lock()
getLock = multiprocessing.Lock()

names_mas = manager.list()

def start_server(_ports):
    # записываем порты
    ports = _ports
    time.sleep(1)
    listen(ports)

def threaded(conn, addr, file_name):
    file = open(file_name, "rb")
    print("new_thread: {}".format(addr))
    while True:
        try:
            res = conn.recv(4096)
            if res.decode() == 'client_work':
                while True:
                    file_data = file.read(4096)
                    conn.send(file_data)
                    if not file_data:
                        file.close()
                        break
                conn.close()
                break
            
        except Exception as e:
            print(e)

def tempo_port(ip, temp_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip, temp_port))
    sock.listen()
    logging.info("Started Tempo_Port 9091!")
    while True:
        conn, addr = sock.accept()
        last_name_audio = names_mas[-1]
        start_new_thread(threaded,(conn, addr, last_name_audio, ))
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
    sock.listen()
    i = 0
    while True:
        conn, addr = sock.accept()
        logging.info("Connected: " + str(addr))
        file_name = "SERVER_AUDIO{}.wav".format(i)
        file = open(file_name, "wb")
        i += 1
        #print("GOT IT")
        while True:
            data = conn.recv(4096)
            try:
                if data.decode():
                    logging.info("SERVER Command " + data.decode() + " from " + str(addr))
                    result.append(data.decode())
                    break
                    
            except Exception:
                file.write(data)
                if not data:
                    break
                
            finally:
                if not data:
                    logging.info("AUDIO FILE ON SERVER")
                    file.close()
                    names_mas.append(file_name)
                    time.sleep(2)
                    #create_tempo_port(file_name)
                    start_clients()
                    break
        
    print('RESULTSDATA: ', result)
    #logging.info("Connection with " + str(addr) + " will be closed")
    #close_port(port, conn)

def start_clients():
    sock = socket.socket()
    sock.connect(('', scheduler_port))
    sock.send('got_file_from_client'.encode())
    sock.close()

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
        
    tempo_process = multiprocessing.Process(target=tempo_port, args=('', 9091,))
    tempo_process.start()

    # сообщаем планировщику, что все процессы запустились и можно продолжать работу
    sock = socket.socket()
    sock.connect(('', scheduler_port))
    sock.send('port_created'.encode())
    sock.close()
    for i in process:
        # ожидаем завершения процессов, иначе общие данные пропадут (Manager умирает при убивании основного процесса)
        i.join()

