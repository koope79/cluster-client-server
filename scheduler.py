# Планировщик - основной связующий элемент. Знает информацию о свободных и использующихся портах, а так же какие клиенты
# их используют

import argparse
import sys
import logging
import os
import socket
import server
import multiprocessing

file_log = logging.FileHandler("scheduler.log")
console_out = logging.StreamHandler()

logging.basicConfig(handlers=(file_log, console_out),
                    format='[%(asctime)s | %(levelname)s | SCHEDULER]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

# TODO сделать массив
manager = multiprocessing.Manager()
ports = []


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='path to file with hosts')
    parser.add_argument("-c", "--config", help='path to config file')
    parser.add_argument("-p", "--port", help='count of clients in pull', default=2)
    return parser


def run_client():
    try:
        logging.info("Run client...")
        os.system('python3 /home/pi/nikolayDC/cluster-client-server/client1.py')
    except:
        logging.error("error while create workers")


def run_other_clients(hosts: str, config: str):
    try:
        # host_file = open(hosts)
        # config_file = open(config)
        # path_to_client_file = config_file.readline().replace("\n", "")
        for i in range(2,4):
            os.system('python3 /home/pi/nikolayDC/cluster-client-server/client{}.py'.format(i))
    except:
        logging.error("error while run others clients")


def server_port_listen(data, conn, addr, hosts, config):
    # сигнал от сервера, что процессы на портах создались
    if data.decode() == 'port_created':
        run_client()
        
    if data.decode() == 'got_file_from_client':
        run_other_clients(hosts, config)


def port_listen(func, main_port, hosts, config):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', main_port))
    sock.listen()
    logging.info("Port 9090 created.")
    while True:
        conn, addr = sock.accept()
        logging.info("Connected_SCHEDULER: " + str(addr))
        data = conn.recv(1024)
        logging.info("Command " + data.decode() + " from " + str(addr))

        if not data:
            break
            
        func(data, conn, addr, hosts, config)
        
        logging.info("Scheduler Connection with " + str(addr) + " will be closed")
        conn.close()
        

def start_scheduler(hosts: str, config: str):
    server_port_listen_process = multiprocessing.Process(target=port_listen,
                                                         args=(server_port_listen, 9090, hosts, config))
    server_port_listen_process.start()
    server.start_server(ports)
    # клиент запускается после сигнала сервера


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])
    # инициализируем возможные порты
    start_port = 9092
    for i in range(0, int(args.port)):
        ports.append(start_port)
        start_port += 1
    start_scheduler(args.host, args.config)
