# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import send_file
import json
import sys
import os.path
import hashlib

reload(sys)  # Reload does the trick!

app = Flask(__name__, static_folder='html', static_url_path='/html')


def getOrPostData(paraName):
	if request.method == 'POST':
		return request.form.get(paraName, None)
	elif request.method == 'GET':
		return request.args.get(paraName, None)
	return None
	pass


@app.route('/hello', methods=['GET', 'POST'])
def hello():
	return "nice"
	pass


@app.route('/get_file', methods=['GET', 'POST'])
def get_model():
	filepath = getOrPostData("filepath")
	return send_file(filepath, mimetype='image/gif')
	pass


if __name__ == '__main__':
	from sys import platform

	if platform == "linux" or platform == "linux2":
		import os

		pidfile = open('pid', 'w')
		pidfile.write(str(os.getpid()))
		pidfile.close()
	app.run(host='0.0.0.0', port=6333, threaded=True)
