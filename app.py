import logging
import cherrypy
#from backend.config import API_CONNECTION
#from backend.logger import setup_logging
from flask import Flask, jsonify, make_response, request
from config import API_CONNECTION
from reader.receipt_reader import getImageResponse
import os
import cv2

APP_NAME = 'Receipt Reader Backend'
logger = logging.getLogger(APP_NAME)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

def create_app():
    flask_app = Flask(APP_NAME)
    flask_app.config['APP_ROOT'] = APP_ROOT

    @flask_app.route('/status', methods=('GET',))
    def app_status():
        response = {
            'status': getImageResponse()
        }
        return make_response(jsonify(response), 200)

    @flask_app.route('/image/reader', methods=('POST',))
    def handle_job():
        #job = request.get_json()
        #print(job)s
        file = request.files['file']
        if file:
            filename = "image_from_ios.jpg"
            
            # create the folders when setting up your app
            #os.makedirs('/receipt_reader/test_images', exist_ok=True)
            # when saving the file
            #full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(os.path.join(app.config['APP_ROOT'], filename))
            return make_response(jsonify({'ok': True, 'message': getImageResponse()}), 201)
        

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