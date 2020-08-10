from flask import Flask, jsonify
from flask_cors import *
import logging
from optparse import OptionParser
import os

parser = OptionParser()
parser.add_option("-d", "--data", dest="data",
                  help="where data to read.",
                  metavar="DIR")
(options, args) = parser.parse_args()
if not options.data:
    print("please config the data directory for this program.")
    exit(0)

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
    _ret = {
        "data": {

        }
    }
    if os.path.isfile(get_data_file(server_name, dt)):
        with open(get_data_file(server_name, dt), "r") as _file:
            print(_file)
    return jsonify(_ret)


if __name__ == "__main__":
    app.run()
