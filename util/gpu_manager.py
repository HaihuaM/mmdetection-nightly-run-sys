import os
import sys
from database import db_connector
import time
import datetime

class GPU_Manager(object):

    def __init__(self, threshold = 80):
        self.threshold = threshold
        self.util_id_list = self.get_availabe_gpu_ids()
        # self.util_id_list = ["0", "1", "2", "3"]
        self.num_gpu_available = len(self.util_id_list)


    def get_availabe_gpu_ids(self):
      """Function to check the GPU status with a utilization threshold
         Paramters: gpu utilization threshold 
         Return: the devices id under the threshold
      """
      # gpu_util=os.popen('nvidia-smi --query-gpu=utilization.gpu --format=csv ').read()
      gpu_util =os.popen('nvidia-smi --query-gpu=utilization.memory --format=csv ').read()
      gpu_util = [ util for util in gpu_util.split() if '%' not in util][1:]
      gpu_util = [ int(util) for util in gpu_util]
      util_id_list=list()
      for idx, util in enumerate(gpu_util):
          if util>self.threshold:
              util_id_list.append(str(idx))
      return util_id_list

    def assign_gpus(self, num_gpu):
        """
        """
        selected_gpus = list()
        if num_gpu > self.num_gpu_available:
            print("Error: number of gpus is %s, you try to assign with %s"%(self.num_gpu_available, num_gpu))
        else:
            for i in range(num_gpu):
                selected_gpus.append(self.util_id_list.pop())

        self.num_gpu_available = len(self.util_id_list)
        return selected_gpus


    def update_db(self):

      gpu_util=os.popen('nvidia-smi --query-gpu=utilization.gpu --format=csv ').read()
      gpu_utils = [ util for util in gpu_util.split() if '%' not in util][1:]
      host_name = os.uname()[1]
      check_time = datetime.datetime.now()
      db = db_connector()
      for idx, util in enumerate(gpu_utils):
          device_id = ".".join([host_name, str(idx)])
          db.gpu_status.insert_one({"device":device_id, 
                                    "host_name":host_name,
                                    "check_time":check_time, 
                                    "load": util})
if __name__ == "__main__":
    g = GPU_Manager()
    g.update_db()
