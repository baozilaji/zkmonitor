from optparse import OptionParser
import threading
import os
import time
import socket
import logging
import json
import datetime

_VERSION = "1.0.0"
_HOST = "localhost"
_PORT = "2181"
_RUNNING = True
_HEART_BEAT_DURATION = 5
_GATHER_DATA_DURATION = 60
_COLLECTING_KEYS = {
    "zk_avg_latency": "avg",
    "zk_max_latency": "max",
    "zk_min_latency": "min",
    "zk_packets_received": "receive",
    "zk_packets_sent": "send",
    "zk_num_alive_connections": "conn",
    "zk_outstanding_requests": "outstanding",
    "zk_znode_count": "znode",
    "zk_open_file_descriptor_count": "open_file",
    "zk_max_file_descriptor_count": "max_file",
}

parser = OptionParser()
parser.add_option("-c", "--cluster", dest="cluster",
                  help="declare zookeeper cluster servers, fmt: [server1[:port1][,server2[:port2]]]")
parser.add_option("-d", "--data", dest="data",
                  help="where data to save.",
                  metavar="DIR")
parser.add_option("-v", "--version", action="store_true", dest="version",
                  help="show version information.")

(options, args) = parser.parse_args()

if options.version:
    print(_VERSION)
    exit(0)

if not options.data:
    options.data = "%s/data" % (os.getcwd(), )

if not os.path.exists(options.data):
    os.mkdir(options.data)

_servers = "%s:%s" % (_HOST, _PORT)
if options.cluster:
    _servers = options.cluster

options.servers = []
__servers = _servers.split(",")
for _s in __servers:
    _ss = _s.split(":")
    if len(_ss) == 2:
        options.servers.append(_ss)
    else:
        options.servers.append([_ss[0], _PORT])

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, filename="%s/monitor.log" % (options.data,), format=LOG_FORMAT)

logging.info(options)


class Worker(threading.Thread):
    def __init__(self, _host, _port):
        threading.Thread.__init__(self)
        self.host = _host
        self.port = _port

    def __str__(self):
        return "<%s, %s>" % (self.host, self.port)

    def send(self, msg):
        _ret = "error"
        try:
            _sock = socket.socket()
            _sock.connect((self.host, int(self.port)))
            _sock.send((msg+"\n").encode("utf-8"))
            _ret = _sock.recv(10240).decode("utf-8")
            _sock.close()
        except TimeoutError as e:
            logging.error("%s send %s TimeoutError: %s", self, msg, e)
        except ConnectionResetError as e:
            logging.error("%s send %s ConnectionResetError: %s", self, msg, e)
        except Exception as e:
            logging.error("%s send %s Exception: %s", self, msg, e)
        return _ret

    def save_data(self, _json):
        _data_dir = "%s/%s_%s" % (options.data, self.host, self.port)
        if not os.path.exists(_data_dir):
            os.mkdir(_data_dir)
        _datetime = datetime.datetime.now()
        _date = _datetime.strftime("%Y-%m-%d")
        _file_path = "%s/%s.txt" % (_data_dir, _date)
        _json['dt'] = _datetime.strftime("%H:%M")
        _json['host'] = self.host
        _json['port'] = self.port
        with open(_file_path, "a") as f:
            json.dump(_json, f)
            f.write("\n")

    def parse_status(self, _status):
        _line = 0
        _json = {}
        _lines = _status.split("\n")
        for _st in _lines:
            _line += 1
            if _line == 1 or not _st:
                continue
            _s2 = _st.split("\t")
            if _s2[0] not in _COLLECTING_KEYS:
                continue
            _json[_COLLECTING_KEYS[_s2[0]]] = int(_s2[1])
        logging.info("%s status: %s" % (self, _json))
        self.save_data(_json)

    def get_status(self):
        _status = self.send("mntr")
        if _status != "error":
            self.parse_status(_status)
        logging.info("%s reset server: %s" % (self, self.send("srst")))

    def run(self):
        _last_heart_beat = time.time()
        _last_gather_data = _last_heart_beat
        while _RUNNING:
            _now = time.time()
            if _last_gather_data + _GATHER_DATA_DURATION < _now:
                _last_gather_data = _now
                self.get_status()
            elif _last_heart_beat + _HEART_BEAT_DURATION < _now:
                _last_heart_beat = _now
                logging.info("%s heart beat: %s", self, self.send("ruok"))
            time.sleep(1)


_threads = []
for _serv in options.servers:
    _worker = Worker(_serv[0], _serv[1])
    _worker.start()
    _threads.append(_worker)

for _thread in _threads:
    logging.info("waiting for %s to finished." % _thread)
    try:
        _thread.join()
    except KeyboardInterrupt:
        _RUNNING = False

logging.info("main thread finished...")
