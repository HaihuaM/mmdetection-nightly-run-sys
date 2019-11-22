import os
import sys
import datetime
import subprocess
import psutil
import re, json
import os.path as op
from glob import glob
from collections import defaultdict
from database import db_connector

def check_fail(run, db, run_dir):
    if 'running' in run['status']:
        run_id = run['_id']
        run_pid = run.get('pid',0)

        if op.exists(op.join(run_dir, 'train.done')):
            db.run.update_one({"_id": run_id},
                          {"$set": {"status": 'train_done'}})
            return 

        if run_pid:
            print("check thread for %s"%run_pid)
            try:
                p = psutil.Process(int(run_pid))
                db.run.update_one({"_id": run_id},
                                  {"$set": {"status": 'train_running'}})
            except:
                db.run.update_one({"_id": run_id},
                              {"$set": {"status": 'train_fail'}})

def get_metrics(run, db, run_dir):

    current_epoch = "N/A"
    current_eval = dict()
    current_eval_html=str()
    run_id = run['_id']

    latest_chk = op.join(run_dir, 'latest.pth')
    if op.exists(latest_chk):
        latest_epoch = os.readlink(latest_chk)
        latest_epoch = latest_epoch.split(".")[0]
        current_epoch = latest_epoch
    db.run.update_one({"_id": run_id},
                      {"$set": {"current_epoch": current_epoch}})
    logs = glob(op.join(run_dir, "*.log.json"))
    logs.sort(key=os.path.getmtime) 
    if len(logs)<1:
        print("Warning: No json log in %s, skip."%(run_dir))
        return 
    else:
        for log in logs[::-1]:
            with open(log) as f:
                contents_lines = f.readlines()[::-1]
            for line in contents_lines:
                line = line.strip('\n')
                data = json.loads(line)
                keys = data.keys()
                selected_keys = [ k for k in keys if "mAP" in k]
                if len(selected_keys)>0:
                    for metric in selected_keys:
                        current_eval.update({metric: data[metric]})
                    break
            if len(current_eval)>0:
                for metric in current_eval:
                    current_eval_html += "<small>%s: %s</small></br>"%(metric, current_eval[metric])
                db.run.update_one({"_id": run_id},
                                  {"$set": {"current_eval": current_eval,
                                            "current_eval_html": current_eval_html}})
                break

def get_eta(run, db, run_dir):

    run_id = run['_id']
    est_remaining_time = "N/A"
    pattern = re.compile('.*lr:.*eta:\s(?P<eta>.*?),.*')
    if op.exists(op.join(run_dir, "train.done")):
        est_remaining_time = "00:00:00"
    else:
        train_logs = glob(op.join(run_dir, "*.log"))
        train_logs = [ x for x in train_logs if re.search(r'\d{8}_\d{6}.log$', x)]
        train_logs.sort(key=os.path.getmtime) 
        if len(train_logs)<0:
            pass
        else:
            for train_log in train_logs[::-1]:

                with open(train_log) as f:
                    line_contents = f.readlines()
                last_line = line_contents[-1].strip('\n')
                match = re.match(pattern, last_line)
                if match:
                    est_remaining_time = match['eta']
                    break

    db.run.update_one({"_id": run_id},
                      {"$set": {"est_remaining_time": est_remaining_time}})

def check_run_detail(run, db, run_dir):
    """Retrivel the detail data from the run.
    """
    run_id = run['_id']
    host_name = os.uname().nodename
    json_logs = glob(op.join(run_dir, "*.log.json"))

    if len(json_logs)<1:
        return

    json_logs.sort(key=os.path.getmtime) 
    log_dict = load_json_logs(json_logs)

    log_data = defaultdict(list)
    keys_list = list()
    for epoch in log_dict:
        keys_list.extend(log_dict[epoch].keys())
    keys_list = list(set(keys_list))
    for epoch in log_dict:    
        for k in [x for x in keys_list if x in log_dict[epoch].keys()]:
            log_data[k].extend(log_dict[epoch][k])

    mtime = datetime.datetime.fromtimestamp(int(op.getmtime(json_logs[-1])))
    db.run.update_one({"_id": run_id},
                      {"$set": {"log_data_0": log_data,
                                "host":host_name,
                                "log_last_update":mtime}})

def load_json_logs(json_logs):
    # load and convert json_logs to log_dict, key is epoch, value is a sub dict
    # keys of sub dict is different metrics, e.g. memory, bbox_mAP
    # value of sub dict is a list of corresponding values of all iterations
    # log_dicts = [dict() for _ in json_logs]
    log_dict = dict()
    for json_log in json_logs:
        base_ep = 0
        with open(json_log, 'r') as log_file:
            max_ep = 0
            for l in log_file:
                log = json.loads(l.strip())
                epoch = int(log.pop('epoch')) + base_ep
                max_ep = epoch if epoch > max_ep else max_ep
                log.pop('mode')
                log.pop('iter')
                if epoch not in log_dict:
                    log_dict[epoch] = defaultdict(list)
                for k, v in log.items():
                    log_dict[epoch][k].append(v)
        base_ep = max_ep
    return log_dict


def check_run_status():

    host_name = os.uname().nodename
    db = db_connector()
    runs = db.run.find({'host': host_name})
    for run in runs:
        run_dir = run.get('run_dir', '')
        if op.exists(run_dir):
            # check 'train_fail' or not.
            check_fail(run, db, run_dir)
            # get metrics
            get_metrics(run, db, run_dir)
            # get ETA
            get_eta(run, db, run_dir)
            # check run detail
            check_run_detail(run, db, run_dir)
        else:
            print("Info: directory not created for %s"%(run['_id']))


def check_stop_runs():
    host_name = os.uname().nodename
    db = db_connector()
    runs = db.run.find({'status': 'stopping', 'host':host_name})
    for run in runs:
        run_dir = run.get('run_dir', '')
        run_id = run['_id']
        run_pid = run.get('pid', 0)
        if run_pid:
            print("check thread for %s"%run_pid)
            try:
                p = psutil.Process(int(run_pid))
                # kill the process
                for c in p.children(recursive=True):
                            c.kill()
                db.run.update_one({'_id':run_id}, 
                                    {"$set": {"status": "train_stopped"}})
                print("Stop run: %s -> %s"%(host_name, str(run_id)))
            except:
                print("Warning: process not exists.")
                db.run.update_one({'_id':run_id}, 
                                    {"$set": {"status": "train_stopped"}})


def check_deleting_runs():
    host_name = os.uname().nodename
    db = db_connector()
    runs = db.run.find({'status': 'deleting', 'host':host_name})
    for run in runs:
        run_dir = run.get('run_dir', '')
        run_id = run['_id']
        run_pid = run.get('pid',0)
        task_id = run['task_id']
        task_info = db.scheduler.find_one({'_id':task_id})
        num_runs = task_info['frequency']
        run_id_list = task_info['run_ids']

        if run_pid:
            print("check thread for %s"%run_pid)
            try:
                p = psutil.Process(int(run_pid))
                for c in p.children(recursive=True):
                            c.kill()
                db.run.update_one({"_id": run_id},
                                  {"$set": {"status": 'train_stopped'}})
            except:
                print("Job process not exits.")

        # Clean directory
        if op.exists(run_dir):
            process = subprocess.Popen("/bin/rm -rf %s"%(op.dirname(run_dir)), shell=True)
            process.wait()
        else: 
            pass
    
        if run_id in run_id_list:
           run_id_list.remove(run_id)

        db.scheduler.update_one({'_id':task_id},
                            {"$set": {"run_ids": run_id_list,
                                      "frequency":num_runs-1}})

        db.run.delete_one({'_id':run_id})
        print("Deleted run: %s -> %s"%(host_name,str(run_id)))

if __name__ == "__main__":

    check_run_status()
    check_deleting_runs()
    check_stop_runs()
