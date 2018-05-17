# -*- coding:utf-8 -*-

from flask import make_response, jsonify
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    if username == 'root':
        return '@^hly012501_Pi31415926$'
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'status': 'error', 'message': 'Unauthorized access'}), 403)