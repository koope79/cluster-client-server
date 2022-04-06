# Client_1 - распознаёт файлы и передаёт ответ серверу (файл или результата)

import socket
import logging
from subprocess import run, STDOUT, PIPE

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


def recognition():
    for i in range(1,12):
        name_file = 'rec{}.wav'.format(i)
        cmd = 'cd /home/pi/pocketsphinx-5prealpha/src/programs && pocketsphinx_continuous -samprate 16000 -hmm /home/pi/pocketsphinx-5prealpha/model/ru-model/zero_ru.cd_semi_4000 -jsgf /home/pi/settingsGramma/gram/my_rus_pi.gram -dict /home/pi/settingsGramma/gram/my_rus_pi_dict -infile /home/pi/dataSounds/16k/test1/{} -logfn /dev/null'.format(name_file)
        output = run(cmd, stdout=PIPE, stderr=STDOUT, text=True, shell=True)
        out_str = output.stdout.rstrip()

        if len(out_str) == 0:
            send_audio(name_file)
        else:
            send_result(out_str)
            
def my_start():
    logging.info("START Client1!")
    recognition()

def send_audio(name_file):
    sock = socket.socket()
    sock.connect((_addr, _port))
    file = open(name_file, "rb")
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
    
my_start()


