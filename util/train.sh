set -e 
export CUDA_VISIBLE_DEVICES=0,1
cd /obtrack/nightly_run/task_5dc917f20914b52dc1c2f925/run_1_5dc917f20914b52dc1c2f92c
# export PYTHON=/home/haihuam/anaconda3/envs/RepPoints/bin/python 
# /home/haihuam/Projects/RepPoints/mmdetection/tools/dist_train.sh /home/haihuam/Projects/RepPoints/configs_voc/reppoints_moment_r50_fpn_1x_voc.py 2 --work_dir /obtrack/nightly_run/task_5dc917f20914b52dc1c2f925/run_0_5dc917f20914b52dc1c2f92a --validate  &> train.log 
# touch train.done 


##!/usr/bin/env bash

#PYTHON=${PYTHON:-"python"}

#CONFIG=$1
#GPUS=$2

/home/haihuam/anaconda3/envs/RepPoints/bin/python  -m torch.distributed.launch --nproc_per_node=2 --master_port 0 /home/haihuam/Projects/RepPoints/mmdetection/tools/train.py /home/haihuam/Projects/RepPoints/configs_voc/reppoints_moment_r50_fpn_1x_voc.py --launcher pytorch --work_dir /obtrack/nightly_run/task_5dc917f20914b52dc1c2f925/run_0_5dc917f20914b52dc1c2f92a --validate  

