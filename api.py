from flask import Flask, jsonify
from flask_cors import *
import logging
from optparse import OptionParser
import os
import json

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


@app.route("/data/<server_name>")
def daily_data(server_name):
    _ret = {
        "data": {

        }
    }
    return json.dumps(_ret)


if __name__ == "__main__":
    app.run()
