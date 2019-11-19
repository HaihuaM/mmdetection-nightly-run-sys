import os
import sys
from database import db_connector
import os.path as op
from glob import glob
import re, json
from collections import defaultdict
import datetime
import subprocess


def check_run_status():
    db = db_connector()
    runs = db.run.find({})
    pattern = re.compile('.*lr:.*eta:\s(?P<eta>.*?),.*')
    for run in runs:
        current_epoch = "N/A"
        current_eval = dict()
        current_eval_html=str()
        est_remaining_time = "N/A"
        run_id = run['_id']
        run_dir = run.get('run_dir','')
        if op.exists(run_dir):
            latest_chk = op.join(run_dir, 'latest.pth')
            if op.exists(latest_chk):
                latest_epoch = os.readlink(latest_chk)
                latest_epoch = latest_epoch.split(".")[0]
                current_epoch = latest_epoch
            db.run.update_one({"_id": run_id},
                              {"$set": {"current_epoch": current_epoch}})
            log = glob(op.join(run_dir, "*.log.json"))
            if len(log)>1 :
                print("Warning: There are more than one json log in %s, skip."%(run_dir))
                pass
            elif len(log)<1:
                print("Warning: No json log in %s, skip."%(run_dir))
                continue 
            else:
                log = log[0]
                print(log)
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
            for metric in current_eval:
                current_eval_html += "<small>%s: %s</small></br>"%(metric, current_eval[metric])
            db.run.update_one({"_id": run_id},
                              {"$set": {"current_eval": current_eval,
                                        "current_eval_html": current_eval_html}})

            
            if op.exists(op.join(run_dir, "train.done")):
                est_remaining_time = "00:00:00"
            else:
                train_log = op.join(run_dir, 
                                    op.basename(log).replace('.json', ''))
                if op.exists(train_log):
                    with open(train_log) as f:
                        line_contents = f.readlines()
                    last_line = line_contents[-1].strip('\n')
                    match = re.match(pattern, last_line)
                    if match:
                        est_remaining_time = match['eta']

            db.run.update_one({"_id": run_id},
                              {"$set": {"est_remaining_time": est_remaining_time}})

def check_run_detail():
    db = db_connector()
    runs = db.run.find({})
    for run in runs:
        _id = run['_id']
        print('Update run data for %s'%(_id))
        check_single_run_detail(_id)


def check_single_run_detail(_id):
    """Retrivel the detail data from the run.
    """
    db = db_connector()
    run = db.run.find_one({'_id':_id})
    run_dir = run.get('run_dir','')
    host_name = os.uname().nodename
    if op.exists(run_dir):
        json_logs = glob(op.join(run_dir, "*.log.json"))
        log_dicts = load_json_logs(json_logs)
        for idx, log_dict in enumerate(log_dicts):
            log_data = defaultdict(list)
            keys_list = list()
            for epoch in log_dict:
                keys_list.extend(log_dict[epoch].keys())
            keys_list = list(set(keys_list))
            for epoch in log_dict:    
                for k in [x for x in keys_list if x in log_dict[epoch].keys()]:
                    log_data[k].extend(log_dict[epoch][k])

            update_time = datetime.datetime.now().strftime("%c")
            db.run.update_one({"_id": _id},
                              {"$set": {"log_data_"+str(idx): log_data,
                                        "host":host_name,
                                        "log_last_update":update_time}})
    else:
        pass

def load_json_logs(json_logs):
    # load and convert json_logs to log_dict, key is epoch, value is a sub dict
    # keys of sub dict is different metrics, e.g. memory, bbox_mAP
    # value of sub dict is a list of corresponding values of all iterations
    log_dicts = [dict() for _ in json_logs]
    for json_log, log_dict in zip(json_logs, log_dicts):
        with open(json_log, 'r') as log_file:
            for l in log_file:
                log = json.loads(l.strip())
                epoch = log.pop('epoch')
                log.pop('mode')
                log.pop('iter')
                if epoch not in log_dict:
                    log_dict[epoch] = defaultdict(list)
                for k, v in log.items():
                    log_dict[epoch][k].append(v)
    return log_dicts

def check_deleting_runs():
    host_name = os.uname().nodename
    db = db_connector()
    runs = db.run.find({'status': 'deleting', 'host':host_name})
    for run in runs:
        run_dir = run.get('run_dir', '')
        run_id = run['_id']
        task_id = run['task_id']
        task_info = db.scheduler.find_one({'_id':task_id})
        num_runs = task_info['frequency']
        run_id_list = task_info['run_ids']

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
    check_run_detail()
    check_deleting_runs()
