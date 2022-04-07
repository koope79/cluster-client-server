# Рабочий - принимает нераспознанные аудиофайлы, распознаёт и передаёт ответ на сервер
import socket
import logging
from subprocess import run, STDOUT, PIPE

file_log = logging.FileHandler("client.log")
console_out = logging.StreamHandler()

logging.basicConfig(handlers=(file_log, console_out),
                    format='[%(asctime)s | %(levelname)s | CLIENT_3]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

# main_port
_port = 9093
_addr = 'localhost'


def recognition(file_name):
    cmd = 'cd /home/pi/pocketsphinx-5prealpha/src/programs && pocketsphinx_continuous -samprate 16000 -hmm /home/pi/pocketsphinx-5prealpha/model/ru-model/zero_ru.cd_semi_4000 -jsgf /home/pi/settingsGramma/gram/my_rus_pi.gram -dict /home/pi/settingsGramma/gram/my_rus_pi_dict -infile /home/pi/nikolayDC/cluster-client-server/{} -logfn /dev/null'.format(file_name)
    output = run(cmd, stdout=PIPE, stderr=STDOUT, text=True, shell=True)
    out_str = output.stdout.rstrip()

    if len(out_str) != 0:
        send_result(out_str)

def listen_tempo():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((_addr, 9091))
    sock.send('client_work'.encode())
    file_name = "CLIENT_3_AUDIO.wav"
    file = open(file_name, "wb")
    while True:
        data = sock.recv(4096)
        file.write(data)
        if not data:
            file.close()
            logging.info("CLIENT 3 GOT FILE")
            recognition(file_name)
            break
            
    sock.close()

def my_start():
    logging.info("START Client_3!")
    listen_tempo()

def send_result(result):
    sock = socket.socket()
    sock.connect((_addr, _port))
    sock.send(result.encode())
    sock.close()
    logging.info("SENDED_3 RESULT")

my_start()
