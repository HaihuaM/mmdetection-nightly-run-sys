#!/usr/bin/env python

"""
Check pending jobs and trigger runs when resource is available.
"""
__author__ = "haihuam"
__date__ = "2019-11-07"

import os
import sys
import os.path as op
from database import db_connector
from gpu_manager import GPU_Manager
from job_requestor import Train, Evaluate, Analyze

class Run_Manager(object):


    def __init__(self):

        self.db = db_connector()

    def job_assigner(self, *job_requests):

        gpu_manager = GPU_Manager()
        assert (gpu_manager.num_gpu_available >= 0)

        process_list = list()
        for job_request in job_requests:
            while True:
                request = job_request()
                num_candidates = self.db.run.count_documents({"$and":[
                    {request.stage+"_num_gpu":{"$lte": gpu_manager.num_gpu_available}}, 
                    {"status":request.pre_status}]})

                if num_candidates > 0:
                    candidates = self.db.run.find({"$and":[
                        {request.stage+"_num_gpu":{"$lte": gpu_manager.num_gpu_available}}, 
                        {"status":request.pre_status}]}).sort("priority", -1)

                    setting = candidates[0]
                    selected_gpus = gpu_manager.assign_gpus(setting[request.stage+'_num_gpu'])
                    request.setup(setting, selected_gpus)
                    request.dump_script()
                    process_list.append(request.kick_off())
                else:
                    # print("No valid jobs for stage %s"%request.stage)
                    break

        if len(process_list):
            for p in process_list:
                p.start()
        else:
            print("No valid jobs for stage %s"%request.stage)

    def run(self):

        self.job_assigner(Train, Evaluate, Analyze)


if __name__ == "__main__":

    run_manager = Run_Manager()
    run_manager.run()
