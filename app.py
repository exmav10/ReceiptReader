import logging
import cherrypy
#from backend.config import API_CONNECTION
#from backend.logger import setup_logging
from flask import Flask, jsonify, make_response, request
from config import API_CONNECTION
from reader.receipt_reader import getImageResponse
import os

APP_NAME = 'Receipt Reader Backend'
logger = logging.getLogger(APP_NAME)

def create_app():
    flask_app = Flask(APP_NAME)

    @flask_app.route('/status', methods=('GET',))
    def app_status():
        response = {
            'status': getImageResponse()
        }
        return make_response(jsonify(response), 200)

    @flask_app.route('/job', methods=('POST',))
    def handle_job():
        job = request.get_json()
        #response = handle(job)
        response = { 'ok': True, 'message': "Hello" }
        return make_response(jsonify(response), 201)

    return flask_app

if __name__ == '__main__':
    #setup_logging()
    app = create_app()
    cherrypy.tree.graft(app, '/')
    cherrypy.config.update({
        'server.socket_host': API_CONNECTION['host'],
        'server.socket_port': API_CONNECTION['port'],
        'engine.autoreload.on': True
    })
    cherrypy.engine.start()