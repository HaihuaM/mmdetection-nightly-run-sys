import os
import sys
from database import db_connector
import os.path as op
from glob import glob
import re, json
from collections import defaultdict


def check_run_status():
    db = db_connector()
    runs = db.run.find({})
    pattern = re.compile('.*lr:.*eta: (?P<eta>\S+),.*')
    for run in runs:
        current_epoch = "N/A"
        current_eval = "N/A"
        est_remaining_time = "N/A"
        run_id = run['_id']
        run_dir = run['run_dir']
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
        else:
            log = log[0]
            with open(log) as f:
                contents_lines = f.readlines()[::-1]
            for line in contents_lines:
                line = line.strip('\n')
                if "mAP" in line:
                    data = json.loads(line)
                    current_eval = data['mAP']
                    break

        db.run.update_one({"_id": run_id},
                          {"$set": {"current_eval": current_eval}})

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
    run_dir = run['run_dir']
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

        db.run.update_one({"_id": _id},
                          {"$set": {"log_data_"+str(idx): log_data}})

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

if __name__ == "__main__":

    # check_run_status()
    check_run_detail()
