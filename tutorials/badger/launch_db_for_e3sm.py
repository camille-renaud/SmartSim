from glob import glob
from smartsim import Experiment
from smartsim.settings import SbatchSettings, RunSettings
from smartsim.database import SlurmOrchestrator
from smartsim.utils.log import get_logger, log_to_file
from smartsim import slurm
import sys
import os
import time
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-j", "--jobid", type=int, help="jobid")
parser.add_argument("-N", "--nodes", type=int, help="number of database nodes")
args = parser.parse_args()

E3SM_JOBID = args.jobid
DB_NODES=args.nodes
db_port=6379

case_dir = '/lustre/scratch3/turquoise/cbegeman/E3SM-Output/20211108_WCYCL1850NS_ne4_oQU480_master/'
os.chdir(case_dir)

if os.path.exists('{}/db_debug.log'.format(case_dir)):
    os.system('rm {}/db_debug.log'.format(case_dir))
log_to_file('{}/db_debug.log'.format(case_dir))
logger = get_logger()
logger.debug('E3SM JOBID={}'.format(E3SM_JOBID))
logger.debug('DB NODES={}'.format(DB_NODES))

if DB_NODES > 0:
    exp = Experiment("db", launcher="local")
    db = SlurmOrchestrator(port=db_port,
                           db_nodes=DB_NODES, # only 1 database (not a cluster)
                           batch=False, # not launching as a seperate batch workload
                           interface="ib0", # high speed network to use (usually ipogif0 for aries CrayXC 50)
                           alloc=E3SM_JOBID# launching into this allocation
                          )
    exp.start(db)
    logger.debug(f"SSDB={db.hosts[0]}:{db_port}")

#exp.stop(db)