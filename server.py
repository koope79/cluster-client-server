# Сервер - держатель общих данных, он их отдает и сохраняет процессобезопасно
import os
import logging
import socket
import multiprocessing
import time
import _thread

file_log = logging.FileHandler("server.log")
console_out = logging.StreamHandler()

logging.basicConfig(handlers=(file_log, console_out),
                    format='[%(asctime)s | %(levelname)s | SERVER]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

ports = []
scheduler_port = 9090

# общие данные
manager = multiprocessing.Manager()
result = manager.list()

th_lock = _thread.allocate_lock()
names_mas = manager.list()
count = None


def start_server(_ports):
    global count
    # записываем порты
    ports = _ports
    count = len(ports)
    time.sleep(1)
    listen(ports)

def threaded(conn, addr, file_name):
    global count
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
                    
                logging.info("FILE SENDED FROM TEMPO: {}".format(file_name))
                th_lock.acquire()
                count -= 1
                if count == 0:
                    names_mas.remove(file_name)
                th_lock.release()
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
        global count
        conn, addr = sock.accept()
        th_lock.acquire()
        if count == 0:
            count = 2
        th_lock.release()
        last_name_audio = names_mas[-1]
        #print(last_name_audio)
        _thread.start_new_thread(threaded,(conn, addr, last_name_audio,))
        

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
                    start_clients()
                    break
                
        print('RESULTSDATA: ', result)
        #conn.close()
        

def start_clients():
    sock = socket.socket()
    sock.connect(('', scheduler_port))
    sock.send('got_file_from_client'.encode())
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
    tempo_process.join()
    for i in process:
        # ожидаем завершения процессов, иначе общие данные пропадут (Manager умирает при убивании основного процесса)
        i.join()

