from flask import Flask
from flask import render_template
from flask import jsonify
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
            if idx > 5:
                break
        data.update({dev: load_data[::-1], 'chk_time': chk_time[::-1]})
    return jsonify(data, devices)

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


