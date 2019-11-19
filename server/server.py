from flask import Flask, redirect
from flask import render_template
from flask import jsonify
import psutil
import shutil
import os
from bson.objectid import ObjectId
from bson import json_util
import json
import os.path as op
import subprocess
# from util.database import db_connector

app = Flask(__name__)

@app.route('/')
@app.route('/index.html')
def check_run_status():
    # return render_template('status.html')
    summary = get_summary()
    return render_template('index.html', summary=summary)

@app.route('/noallowed/status.html')
def status():
    db = db_connector()
    task_list = list()
    tasks = db.scheduler.find({})
    for task in tasks:
        config_file = task['config_file']
        task['config_file'] = op.basename(config_file)
        run_list = list()
        for run_id in task['run_ids']:
            run_list.append(get_run_status(run_id))
        task.update({'runs': run_list})
        task_list.append(task)

    return render_template('status.html', tasks=task_list, modify=True)

@app.route('/view/status.html')
def view_status():
    db = db_connector()
    task_list = list()
    tasks = db.scheduler.find({})
    for task in tasks:
        config_file = task['config_file']
        task['config_file'] = op.basename(config_file)
        run_list = list()
        for run_id in task['run_ids']:
            run_list.append(get_run_status(run_id))
        task.update({'runs': run_list})
        task_list.append(task)

    return render_template('status.html', tasks=task_list, modify=False)

@app.route('/json/status')
def json_status():
    runs = get_summay_status()
    run_infos = list()
    for run in runs:
        json_doc = json.dumps(run, default=json_util.default)
        run_infos.append(json_doc)
    return jsonify(run_infos)

@app.route('/detail/<run_id>')
def detail(run_id):
    db = db_connector()
    run = db.run.find_one({'_id':ObjectId(run_id)})
    if 'log_data_0' not in run:
        return redirect("/status.html", code=302)
    else:
        metrics = run['log_data_0'].keys()
        return render_template('charts.html', 
                               run_dir=run['run_dir'], 
                               config_file=run['config_file'], 
                               description=run['description'],
                               metrics=metrics,
                               compare_mode=False)

@app.route('/compare/<compare_id>')
def compare(compare_id):
    db = db_connector()
    run_ids = compare_id.split('_')
    filetered_metrics = ['memory', 'time', 'data_time', 'bbox_mAP_copypaste']
    metrics = list()
    for run_id in run_ids:
        run = db.run.find_one({'_id':ObjectId(run_id)})
        if 'log_data_0' not in run:
            return redirect("/status.html", code=302)
        _metrics = run['log_data_0'].keys()
        metrics.append(_metrics)

    metrics = list(set(metrics[0]) & set(metrics[1]))
    metrics = [x for x in metrics if x not in filetered_metrics]
    return render_template('charts.html', 
                           metrics=metrics,
                           compare_mode=True)



@app.route('/delete/<run_id>')
def delete(run_id):
    db = db_connector()
    run_id = ObjectId(run_id) 
    db.run.update_one({'_id':run_id},
            {"$set":{"status": "deleting"}})

    return jsonify('Pending for deleting.')

@app.route('/reschedule/<run_id>')
def reschedule(run_id):
    db = db_connector()
    run_id = ObjectId(run_id) 
    run_info = db.run.find_one({'_id': run_id})
    run_dir = run_info.get('run_dir', '')

    if op.exists(run_dir):
        process = subprocess.Popen("/bin/rm -rf %s"%(run_dir), shell=True)
        process.wait()
    
    db.run.update_one({'_id':run_id},
            {"$unset": {"run_dir":"", 
                        "current_eval":"",
                        "current_eval_html":"",
                        "current_epoch":"",
                        "est_remaining_time":"",
                        "log_last_update":"",
                        "log_data_0":"",
                        } }) 

    db.run.update_one({'_id':run_id},
            {"$set": { "status":"pending" } }) 

    return jsonify('Rescheduled.')



@app.route('/add_run/<task_id>')
def add_run(task_id):
    db = db_connector()
    task_id = ObjectId(task_id)
    task = db.scheduler.find_one({'_id': task_id})
    host_name = os.uname().nodename
    num_pre_runs = task['frequency']
    # print(num_pre_runs)

    run_list = task['run_ids']
    if len(run_list)==0:
        run_idx = 0
    else:
        latest_run_id = run_list[-1]
        latest_run = db.run.find_one({'_id': latest_run_id})
        run_idx = latest_run['run_idx'] + 1

    _filtered_fileds = ["_id", "assign_status", "frequency"]

    run_setting = {key:value for key, value in task.items() \
            if (key not in _filtered_fileds)}

    run_setting.update({
                   'task_id': task_id,
                   'run_idx': run_idx,
                   'status': 'pending',
                   'host': host_name,
                  })

    run_list.append(register_run(run_setting))
    db.scheduler.update_one(
                         {'_id':task_id}, 
                         {"$set":{
                                  "run_ids":run_list,
                                  "frequency":1+num_pre_runs,}})

    return jsonify('Added.')

def register_run(run_setting):
    """
    """
    db = db_connector()
    run = db.run
    return run.insert_one(run_setting).inserted_id


@app.route('/gpu_util')
def gpu_util():
    db = db_connector()
    hosts = db.gpu_status.distinct('host_name')
    devices = db.gpu_status.distinct('device')
    load_datas = dict()
    for host in hosts:
        data = dict()
        for dev in devices:
            if host in dev:
                _data = db.gpu_status.find({'device':dev}).sort("check_time", -1)
                load_data = list()
                chk_time = list()
                for idx, item in enumerate(_data):
                    chk_time.append(item['check_time'])
                    load_data.append(int(item['load']))
                    if idx > 100:
                        break
                data.update({dev:load_data[::-1], 'chk_time': chk_time[::-1]})
        load_datas.update({host:data})
    return jsonify(load_datas, hosts, devices)

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

@app.route('/compare_run_status/<compare_id>')
def compare_run_status(compare_id):
    db = db_connector()
    run_ids = compare_id.split('_')
    metrics = list()
    data = list()
    names = list()
    for run_id in run_ids:
        run = db.run.find_one({'_id':ObjectId(run_id)})
        config_file = op.basename(run['config_file'])
        run_idx = run['run_idx']
        names.append('->'.join([config_file,str(run_idx)]))
        if 'log_data_0' not in run:
            return redirect("/status.html", code=302)
        _metrics = run['log_data_0'].keys()
        metrics.append(_metrics)
        data.append(run['log_data_0'])

    metrics = list(set(metrics[0]) & set(metrics[1]))
    for _data in data:
        _data = {k:v for k, v in _data.items() if k in metrics}

    return jsonify({'data':data, 'names':names})

def bytes_2_human_readable(number_of_bytes):
    """Convert byters to readable format.
    """
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

def get_summay_status():
    db = db_connector()
    return db.run.find({},{'config_file', 
                           'run_dir',
                           'status',
                           'run_idx', 
                           'description',
                           'host', 
                           'train_num_gpu',
                           'current_epoch',
                           'current_eval',
                           'log_last_update',
                           'current_eval_html',
                           'est_remaining_time'})

def get_run_status(run_id):
    db = db_connector()
    return db.run.find_one({'_id': run_id},{'config_file', 
                           'run_dir',
                           'status',
                           'run_idx', 
                           'description',
                           'host', 
                           'train_num_gpu',
                           'current_epoch',
                           'current_eval',
                           'log_last_update',
                           'current_eval_html',
                           'est_remaining_time'})

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
    hosts = db.gpu_status.distinct('host_name')
    summary = {"running": running,
               "pending": pending,
               "failed": failed,
               "finished": finished,
               "all": all_jobs,
               "hosts":hosts
              }

    return summary





def db_connector():

    from pymongo import MongoClient
    client = MongoClient('219.228.57.73', 27017,
                         username='dbadmin',
                         password='daohaosiquanjia')

    # db = client.db_test
    db = client.ob_tracker

    return db


