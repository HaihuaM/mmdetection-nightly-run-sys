from flask import Flask
from flask import render_template
from flask import jsonify
import psutil
import shutil
import os
from bson.objectid import ObjectId
import json
import os.path as op
# from util.database import db_connector

app = Flask(__name__)

@app.route('/')
@app.route('/index.html')
def check_run_status():
    # return render_template('status.html')
    summary = get_summary()
    return render_template('index.html', summary=summary)

@app.route('/status.html')
def tables():
    # return render_template('status.html')
    status = get_status()
    return render_template('status.html', status=status)

@app.route('/detail/<run_id>')
def detail(run_id):
    # return render_template('status.html')
    # status = get_status()
    db = db_connector()
    run = db.run.find_one({'_id':ObjectId(run_id)})
    metrics = run['log_data_0'].keys()
    return render_template('charts.html', run_dir=run['run_dir'], metrics=metrics )

@app.route('/delete/<run_id>')
def delete(run_id):
    db = db_connector()
    run_info = db.run.find_one({'_id':ObjectId(run_id)})
    task_id = run_info['task_id']
    db.scheduler.delete_one({'_id':ObjectId(task_id)})
    db.run.delete_one({'_id':ObjectId(run_id)})
    return jsonify('Deleted.')

@app.route('/gpu_util')
def gpu_util():
    db = db_connector()
    devices = db.gpu_status.distinct('device')
    data = dict()
    for dev in devices:
        _data = db.gpu_status.find({'device':dev}).sort("check_time", -1)
        load_data = list()
        chk_time = list()
        for idx, item in enumerate(_data):
            chk_time.append(item['check_time'])
            load_data.append(int(item['load']))
            if idx > 1000:
                break
        data.update({dev: load_data[::-1], 'chk_time': chk_time[::-1]})
    return jsonify(data, devices)

@app.route('/disk_util')
def disk_util():
    total, used, free = shutil.disk_usage(__file__)
    percent = (used/total)*100
    total = bytes_2_human_readable(total)
    used = bytes_2_human_readable(used)
    free = bytes_2_human_readable(free)
    reponse_data = {'total': total,
                    'used': used,
                    'free': free,
                    'percent': percent
                   }
    return jsonify(reponse_data)

@app.route('/sys_load')
def sys_load():
    loads = os.getloadavg()
    num_cpus = psutil.cpu_count()
    users = psutil.users()
    reponse_data = {
                    'last_1': loads[0],
                    'last_5': loads[1],
                    'last_15':loads[2],
                    'percent':loads[0]/num_cpus*100,
                    'num_online_users': len(users),
                    'online_users': users
                   }
    return jsonify(reponse_data)

@app.route('/run_status/<run_id>')
def retrive_run_status(run_id):
    db = db_connector()
    run = db.run.find_one({'_id':ObjectId(run_id)})
    return jsonify(run['log_data_0'])


def bytes_2_human_readable(number_of_bytes):
    if number_of_bytes < 0:
        raise ValueError("!!! number_of_bytes can't be smaller than 0 !!!")

    step_to_greater_unit = 1024.

    number_of_bytes = float(number_of_bytes)
    unit = 'bytes'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'KB'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'MB'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'GB'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'TB'

    precision = 1
    number_of_bytes = round(number_of_bytes, precision)

    return str(number_of_bytes) + ' ' + unit

def get_status():
    db = db_connector()
    return db.run.find({})

def get_summary():
    """Check the db base to get the summary
    """
    db = db_connector()
    running = db.run.count_documents({"status":{"$in": ['train_running', 
                                                        'evaluate_running', 
                                                        'analyze_running' ]}})

    pending = db.run.count_documents({"status":{"$in":['pending', 'train_done',
                                                       'evaluate_done']}})

    failed = db.run.count_documents({"status":{"$in": ['train_failed', 
                                                       'evaluate_failed', 
                                                       'analyze_failed' ]}})

    finished =db.run.count_documents({"status": "all_done"})
    all_jobs = db.run.count_documents({})
    summary = {"running": running,
               "pending": pending,
               "failed": failed,
               "finished": finished,
               "all": all_jobs
              }

    return summary


def db_connector():

    from pymongo import MongoClient
    client = MongoClient('219.228.57.73', 27017,
                         username='dbadmin',
                         password='daohaosiquanjia')

    db = client.ob_tracker
    return db


