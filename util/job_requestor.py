import os
import sys
import os.path as op
import threading
from database import db_connector
import shutil
import socket
import subprocess
from multiprocessing import Process


class Job_Requestor(object):

    run_center = "/obtrack/nightly_run"
    data_dir = "/home/haihuam/Projects/RepPoints/data"

    def __init__(self):

        self.db = db_connector()

    def setup(self, setting, selected_gpus):
        self.setting = setting
        self._id = setting['_id']
        task_id = setting['task_id']
        self.selected_gpus = selected_gpus
        self.setting.update({self.stage+"_selected_gpus": self.selected_gpus})
        self.global_setting = self.db.scheduler.find_one({'_id': task_id})
        self.run_dir = setting.get('run_dir', '')
        self.status = str()

    def dump_script(self):

        self.script_generator()
        self.script_dir = op.join(self.run_dir, self.script_name)
        self.backup_script_dir = op.join(self.run_dir, '.backup', self.script_name)
        self.backup_config_dir = op.join(self.run_dir, '.backup', 
                                         op.basename(self.setting['config_file']))
        with open(self.script_dir, 'w+') as f:
            f.write(self.script_content)

        if op.exists(self.script_dir):
            # print("Info: script %s generated."%self.script_dir)
            shutil.copyfile(self.script_dir, self.backup_script_dir)
            shutil.copyfile(self.setting['config_file'], self.backup_config_dir)
            self.status = self.stage + "_script" + "_ready"
        else:
            print("Error: script %s generated failed."%self.script_dir)
            self.status = self.stage + "_script" + "_fail"
            sys.exit(0)

        self._update_status()
        self._db_update(self.setting)
        
    def script_generator(self):
        raise NotImplementedError 

    def kick_off(self):
        """ Start a daemon thread.
        """
        if self.status == self.stage + "_script" + "_ready":
            self.status = self.stage+"_running"
            self._update_status()
            p = Process(target=process_kick_off, 
                        args=(self.setting, 
                              self.script_dir, 
                              self.stage, ))
            return p
        else:
            print("Error happened during script generation in stage %s." %self.stage)


    def _update_status(self):
        """ Update status to database
        """
        self._db_update({'status': self.status})

    def _db_update(self, update):
        self.db.run.update_one({'_id': self._id},
                {"$set": update })

def process_kick_off(setting, script_dir, stage):
    """ Process environment to run a job.
    """
    print("Info: run started for %s."%script_dir)
    run_dir = setting['run_dir']
    _id = setting['_id']
    process = subprocess.Popen("/bin/bash %s"%(script_dir), shell=True)
    process.wait()

    if op.exists(op.join(run_dir, stage+".done")):
        status = "all_done" if (stage == "train") \
                else (stage + "_done")
    else:
        status = stage + "_fail"

    print("Info: update status <%s> into db "%status)
    # New db connector, avoid warining use connection before into subprocess
    db = db_connector()
    db.run.update_one({'_id': _id},
            {"$set": {"status":status }})

class Train(Job_Requestor):
    
    def __init__(self):
        super(Train, self).__init__()
        self.script_name = "train.sh"
        self.stage = "train"
        self.pre_status = "pending"

    def setup(self, setting, selected_gpus):
        super(Train, self).setup(setting, selected_gpus)
        self._create_run_dir()

    def _create_run_dir(self):
        """A run step will contain 3 stage, and run_dir created in the train stage.
        """
        task_name = 'task_'+str(self.setting['task_id'])
        run_name = '_'.join(['run', 
                             str(self.setting['run_idx']), 
                             str(self.setting['_id'])])
    
        run_dir = op.join(Job_Requestor.run_center, task_name, run_name)
        back_dir = op.join(run_dir, '.backup')
        try: 
            os.makedirs(run_dir)
            os.makedirs(back_dir)
        except:
            print("Error: run dir %s create failed"%(run_dir))
            sys.exit(0)
    
        os.symlink(Job_Requestor.data_dir, op.join(run_dir, 'data')) 
        
        self.run_dir = run_dir
        self.setting.update({'run_dir':run_dir})
        self._db_update({'run_dir': run_dir})

    def script_generator(self):
        dist_train = self.global_setting.get('dist_train', True)
        if dist_train:
            self._get_free_tcp_port()
            self.generate_disttrain_scipts()
        else:
            self.generate_singletrain_scipts()

    def _get_free_tcp_port(self):
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.bind(('', 0))
        addr, port = tcp.getsockname()
        tcp.close()
        self.dist_train_port = port

    def generate_disttrain_scipts(self):
        """ Function to generate distributed training scripts.
        Paramters: setting.
        Return: script content.
        """
        train_py = "/home/haihuam/Projects/RepPoints/mmdetection/tools/train.py"
        py = self.global_setting.get('python', sys.executable)
        ex_options = self.global_setting.get('train_options', str())
        
        if os.access(py, os.X_OK):
            content = "set -e \n"
            content += "export CUDA_VISIBLE_DEVICES=" + \
                      ",".join(self.selected_gpus)+ " \n"

            content += "cd %s \n"%(self.run_dir)
            content += "%s -m torch.distributed.launch "%(py)
            content += "--nproc_per_node=%s "%(self.setting['train_num_gpu'])
            content += "--master_port %s "%(self.dist_train_port)
            content += "%s %s --launcher pytorch "%(train_py, self.setting['config_file'])
            content += "--work_dir %s "%(self.run_dir)
            content += "--validate %s &> %s.log \n"%(ex_options, self.stage)
            content += "touch train.done \n"
            # return content
            self.script_content = content
        else:
            print("Error: %s is not executable."%py)
            sys.exit(0)

    def generate_singletrain_scipts(self):
        """ Function to generate distributed training scripts.
        Paramters: setting.
        Return: script content.
        """
        py = self.global_setting.get('python', sys.executable)
        ex_options = self.global_setting.get('train_options', str())
        train_py = "/home/haihuam/Projects/RepPoints/mmdetection/tools/train.py"
        if os.access(py, os.X_OK):
            content = "set -e \n"
            content += "export CUDA_VISIBLE_DEVICES=" + \
                      ",".join(self.selected_gpus)+ " \n"
            content += "cd %s \n"%(self.run_dir)
            content += "%s %s %s "%(py, train_py, self.setting['config_file'])
            content += "--work_dir %s "%(self.run_dir)
            content += "--validate %s &> %s.log \n"%(ex_options, self.stage)
            content += "touch train.done \n"

            self.script_content = content
        else:
            print("Error: %s is not executable."%py)
            sys.exit(0)



class Analyze(Job_Requestor):
    def __init__(self):
        super(Analyze, self).__init__()
        self.script_name = "analyze.sh"
        self.stage = "analyze"
        self.pre_status = "evaluate_done"


    def script_generator(self):
        """ Function to generate the scripts to analyze the log.
        """
        analyze_tool = "/home/haihuam/Projects/RepPoints/mmdetection/tools/analyze_logs.py"
        ex_options = self.global_setting.get('analyze_options', str())
        py = self.global_setting.get('python', sys.executable)
        if os.access(py, os.X_OK):
            content = "set -e \n" 
            content += "cd %s \n"%(self.run_dir)
            content += "%s %s plot_curve *.log.json "%(py, analyze_tool)
            content += "--keys loss loss_cls loss_pts_init "
            content += "loss_pts_refine "
            content += "--out losses.pdf %s &> analyze.log \n"%(ex_options)

            content += "touch analyze.done \n"
            self.script_content = content
        else:
            print("Error: %s is not executable."%py)
            sys.exit(0)

class Evaluate(Job_Requestor):
    def __init__(self):
        super(Evaluate, self).__init__()
        self.script_name = "evaluate.sh"
        self.stage = "evaluate"
        self.pre_status = "train_done"


    def script_generator(self):
        """ Function to generate distributed training scripts.
        Paramters: setting.
        Return: script content.
        """
        py = self.global_setting.get('python', sys.executable)
        ex_options = self.global_setting.get('evaluate_options', str())
        train_py = "/home/haihuam/Projects/RepPoints/mmdetection/tools/train.py"
        if os.access(py, os.X_OK):
            content = "set -e \n"
            content += "export CUDA_VISIBLE_DEVICES=" + \
                      ",".join(self.selected_gpus)+ " \n"
            content += "cd %s \n"%(self.run_dir)
            
            content += "%s %s %s --work_dir %s --validate %s &> train.log \n"%(py, 
                                                                         train_py,
                                                                         self.setting['config_file'],
                                                                         self.run_dir,
                                                                         ex_options)
            content += "touch evaluate.done \n"

            self.script_content = content
        else:
            print("Error: %s is not executable."%py)
            sys.exit(0)
