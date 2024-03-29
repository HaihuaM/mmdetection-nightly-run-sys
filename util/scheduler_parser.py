#!/usr/bin/env python

"""
Parse a scheduler run configure file, to register the task into mongodb.
"""
__author__ = "haihuam"
__date__ = "2019-11-07"

import os
import sys
import time
import datetime
import argparse
from database import db_connector
import os.path as op

def task_conf_parser(config_file):
    """
    A file parser.
    """
    import yaml

    with open(config_file) as cfg:
        content = cfg.read()

    # Use FullLoader to support int format
    schedulers = yaml.load(content, Loader=yaml.FullLoader)
    db = db_connector()
    num_success_registered = 0

    for task in schedulers:
        config_file = schedulers[task]['config_file']
        indb_run = db.scheduler.find_one({'config_file':config_file})

        if indb_run !=None :
            if (schedulers[task].get('mode','normal')!="append"):
                print("Config file %s already started run, you can check.."%(config_file))
                continue
            else:
                # import pdb; pdb.set_trace()
                print("Append run for %s"%(config_file))
                append_runs(indb_run, schedulers[task])
                num_success_registered += 1
        else:
            register_runs(schedulers[task])
            num_success_registered += 1
    print("INFO: %s tasks registered."%(num_success_registered))

def register_runs(task):
    """
    Register tasks into mongodb
    Paramters: task
    Returns: None
    """
    db = db_connector()
    scheduler = db.scheduler
    farm = task.get('farm', 'False')
    task.update({'farm': farm.upper()})
    task.update({'assign_status': False})
    task.update({'submitted_time': datetime.datetime.now()})
    scheduler.insert_one(task)

def append_runs(task_info, setting):

    db = db_connector()
    scheduler = db.scheduler
    task_id = task_info['_id']
    num_pre_runs = task_info['frequency']
    run_ids = task_info['run_ids']
    host_name = os.uname().nodename
    
    freq = setting['frequency']
    farm = setting.get('farm', 'False')
    setting.update({'farm': farm.upper()})

    _filtered_fileds = ["_id", "assign_status", "frequency"]
    
    for idx in range(freq):
        run_setting = {key:value for key, value in setting.items() \
                if (key not in _filtered_fileds)}

        run_setting.update({
                       'task_id': task_id,
                       'run_idx': idx+num_pre_runs,
                       'status': 'pending',
                       'host': host_name,
                      })

        run_ids.append(register_run(run_setting))

    scheduler.update_one(
                         {'_id':task_id}, 
                         {"$set":{
                                  "run_ids":run_ids,
                                  "frequency":freq+num_pre_runs,}})




def check_and_assign():
    """
    Check unassigned task then register runs.
    """
    from time import time
    db = db_connector()
    scheduler = db.scheduler
    unassigned_task = scheduler.find({'assign_status': False})
    host_name = os.uname().nodename
    for idx, task in enumerate(unassigned_task):
        task_id = task['_id']
        freq = int(task['frequency'])
        run_ids = list()
        _filtered_fileds = ["_id", "assign_status", "frequency"]
        
        for idx in range(freq):
            run_setting = {key:value for key, value in task.items() \
                    if (key not in _filtered_fileds)}

            run_setting.update({
                           'task_id': task_id,
                           'run_idx': idx,
                           'status': 'pending',
                           'host': host_name,
                          })

            run_ids.append(register_run(run_setting))

        scheduler.update_one(
                             {'_id':task_id}, 
                             {"$set":{"assign_status":True,
                                      "run_ids":run_ids}})
        


def register_run(run_setting):
    """
    """
    db = db_connector()
    run = db.run
    return run.insert_one(run_setting).inserted_id


if __name__ == "__main__":


    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-c', '--config', help='configure file, yaml format.')

    args = parser.parse_args()
    if op.exists(args.config):
        task_conf_parser(args.config)
        check_and_assign()
    else:
        print("Error: Config file doest not exist."%args.Config)
        sys.exit(0)
    

