import os
import json
import datetime
from flask import Flask
from flask.json import JSONEncoder
import calendar
from datetime import datetime
from flask import request, jsonify

class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                if obj.utcoffset() is not None:
                    obj = obj - obj.utcoffset()
                millis = int(
                    calendar.timegm(obj.timetuple()) * 1000 +
                    obj.microsecond / 1000
                )
                return millis
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


# create the flask object
app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

@app.route('/custom')
def custom_jsonencoder():
    now = datetime.now()
    return jsonify({'now': now})



@app.route('/deneme', methods=['GET'])
def deneme():
    if request.method == 'GET':
        return jsonify({'ok': True, 'message': 'aferin aydin'}), 200

if __name__ == '__main__':
    app.run(debug=True)