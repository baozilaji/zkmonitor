from flask import Flask, jsonify
from flask_cors import *
import logging
from optparse import OptionParser
import os
import json
import datetime

_DISPLAY_LAST_MINUTE = 15

parser = OptionParser()
parser.add_option("-d", "--data", dest="data",
                  help="where data to read.",
                  metavar="DIR")
(options, args) = parser.parse_args()
if not options.data:
    print("please config the data directory for this program.")
    exit(0)

if not os.path.exists(options.data):
    os.mkdir(options.data)

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, filename="%s/api.log" % (options.data,), format=LOG_FORMAT)

_date_keys = []
_date_label = []


def get_display(_value):
    if _value < 10:
        return "0"+str(_value)
    else:
        return str(_value)


def calc_keys_labels():
    global _date_keys
    global _date_label
    _date_keys = []
    _date_label = []
    _now = datetime.datetime.now()
    _minutes = _now.hour*60+_now.minute
    for _i in range(_minutes - _DISPLAY_LAST_MINUTE, _minutes):
        _hour = int(_i / 60)
        _min = _i % 60
        _key = "%s:%s" % (get_display(_hour), get_display(_min))
        _date_keys.append(_key)
        if _i % 5 == 0:
            _date_label.append(_key)
        else:
            _date_label.append("")


app = Flask(__name__)
CORS(app, resources=r'/*')


def get_server_list():
    _ret = {
        "data": []
    }
    if os.path.isdir(options.data):
        _dirs = os.listdir(options.data)
        for _dir in _dirs:
            if os.path.isdir("%s/%s" % (options.data, _dir)):
                _ret["data"].append(_dir)

    return jsonify(_ret)


@app.route("/server_list")
def server_list():
    return get_server_list()


def get_data_file(server_name, dt):
    return "%s/%s/%s.txt" % (options.data, server_name, dt)


@app.route("/data/<server_name>/<dt>")
def daily_data(server_name, dt):
    calc_keys_labels()
    _ret = {
        "data": {
            "labels": _date_label,
            "keys": _date_keys,
            "all_data": {}
        }
    }
    if os.path.isfile(get_data_file(server_name, dt)):
        with open(get_data_file(server_name, dt), "r") as _file:
            _lines = _file.readlines()
            for _line in _lines:
                _json = json.loads(_line)
                if _json['dt'] in _date_keys:
                    _ret['data']['all_data'][_json['dt']] = _json
    return jsonify(_ret)


if __name__ == "__main__":
    app.run()
