# -*- coding:utf-8 -*-

import os
import sys
import json
import traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request
from utils.rpi_controller import RpiController
from bin.auth import auth

rpi_controller = RpiController()

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello, World!"


@app.route('/getNetworkConf')
# @auth.login_required
def getNetworkConf():
    try:
        result = rpi_controller.getNetworkConf()
        status = "ok" if result else "error"
    except:
        result = traceback.format_exc()
        status = "error"

    return json.dumps({"status": status, "message": result})


@app.route('/changeNetwork')
@auth.login_required
def changeNetwork():
    print json.dumps(request.args, indent=4)
    try:
        result = rpi_controller.changeNetwork(**request.args.to_dict())
    except:
        result = traceback.format_exc()

    status = "ok" if result is True else "error"
    return json.dumps({"status": status, "message": result})


@app.route('/resetNetwork')
@auth.login_required
def resetNetwork():
    try:
        result = rpi_controller.resetNetwork(**request.args.to_dict())
    except:
        result = traceback.format_exc()

    status = "ok" if result is True else "error"
    return json.dumps({"status": status, "message": result})


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )



#
# from apistar import App, Route, http
#
# def network_setter(request: http.Request, query_params: http.QueryParams):
#     if name is None:
#         return {'message': 'Welcome to API Star!'}
#     return {'message': 'Welcome to API Star, %s!' % name}
#
# def network_getter():
#     pass
#
# routes = [
#     Route('/network_conf', method='GET', handler=network_getter),
#     Route('/network_conf', method='PUT', handler=network_setter),
# ]
#
# app = App(routes=routes)
#
#
# if __name__ == '__main__':
#     app.serve('192.168.116.32', 8000, debug=True)
