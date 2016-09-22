# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import twitteranalyzer
from flask import Flask, jsonify, render_template, request, make_response, send_from_directory, send_file
from threading import Thread
import urllib
import json
import Queue as queue
import zipfile

app = Flask(__name__)

def th(key,q):  
    while True:
        print("th fn starts")
        results="" 
        results=twitteranalyzer.doProcessing(key,q)

threadlist=[]



with open('keys.json') as data_file:    
    keys = json.load(data_file)

@app.route('/', methods = ['GET', 'POST'])
def GetInsights():
    q = queue.Queue()
    results = ""
    handle = ""
    handles= ""
    if request.method == 'POST':
        if request.form['handle'] == "":
            print("no handle")
        else:
            handle = request.form['handle']
            handles = handle.splitlines()

            for h in handles:
                q.put(h)


            for key in keys:
                print('Thread Start for all handles with'+key['accessToken'])
                t= Thread(target=th,args=(key,q))
                t.daemon = True
                t.start()
                threadlist.append(t)
                
            for b in threadlist:
                b.join()
    q.join()

    for threads in threadlist:
        print(threads)

    results = "Completed!"


    return render_template('wpi.html',handles=handles,results=results)

@app.route('/wpidownload', methods = ['GET', 'POST'])
def GetFile():
    zf = zipfile.ZipFile('download.zip', mode='w')
    print os.listdir("json/")[1]
    for f in os.listdir("json/"):
        print f
        if f.endswith(".json"):
            zf.write("json/"+f)
    zf.close()
    try:
        for f in os.listdir("json/"):
            #print f
            if f.endswith(".json"):
                os.remove("json/"+f)
    except Exception as ex:
        print ex
    return send_file('download.zip',as_attachment=True)
            #users = request.form['handle']
        #results[str(user)] = None
        #return send_from_directory('/', 'download.zip', as_attachment=True)
    return render_template('wpi.html')
#test edit
# testing
port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port), debug=True)
