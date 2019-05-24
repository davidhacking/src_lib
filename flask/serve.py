# -*- coding: utf-8 -*-
from flask import Flask, request, redirect
from flask import jsonify
import json
import sys
from flask import render_template
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF-8')

app = Flask(__name__, static_folder='html', static_url_path='/html')


def getOrPostData(paraName):
	if request.method == 'POST':
		return request.form[paraName]
	elif request.method == 'GET':
		return request.args.get(paraName)
	return None
	pass


@app.route('/', methods=['GET', 'POST'])
def index():
	return redirect('/html/index.html')
	pass


@app.route('/hello', methods=['GET', 'POST'])
def hello():
	return "nice"
	pass


if __name__ == '__main__':
	from sys import platform
	if platform == "linux" or platform == "linux2":
		import os
		pidfile = open('pid', 'w')
		pidfile.write(str(os.getpid()))
		pidfile.close()
	app.run(host='0.0.0.0', port=1937, threaded=True)
