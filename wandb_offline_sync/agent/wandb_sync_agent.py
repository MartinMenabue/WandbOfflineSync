import requests
import os
import wandb
import time

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

HOSTNAME = os.environ.get('SYNC_FARM_HOSTNAME', 'localhost')
PORT = os.environ.get('SYNC_FARM_PORT', 57891)
SYNC_FARM_USERNAME = os.environ.get('SYNC_FARM_USERNAME', 'user')
SYNC_FARM_PASSWORD = os.environ.get('SYNC_FARM_PASSWORD', 'pass')

class SyncAgent:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
            return cls.instance
    
    def init(self, frequency=300, timeout=5, verbose=False):
        self.frequency = frequency
        self.timeout = timeout
        self.verbose = verbose

        try:
            self.run_id = wandb.run.id
            self.run_dir = wandb.run.dir.removesuffix('/files')
            self.data = {
                'run_id': self.run_id,
                'run_dir': self.run_dir.removesuffix('/files'),
            }
            self.old_time = time.time()
        except:
            print('SYNC FARM AGENT - ERROR: wandb is not initialized. Call wandb.init() before initializing the agent')
    
    def trigger_sync(self, force=False):
        if not hasattr(self, 'run_id'):
            print('SYNC FARM AGENT - ERROR: agent is not initialized. Call agent.init() before triggering sync')
            return
        
        if not force and (time.time() - self.old_time) < self.frequency:
            print('SYNC FARM AGENT - Delay has not passed. Not triggering sync')
            return
        
        self.old_time = time.time()
        try:
            if self.verbose:
                print('SYNC FARM AGENT - Sending sync request')
            r = requests.post(f'https://{HOSTNAME}:{PORT}/sync', verify=False,
                                auth=(SYNC_FARM_USERNAME, SYNC_FARM_PASSWORD),
                                data=self.data, timeout=self.timeout)
            return r
        except Exception as e:
            if self.verbose:
                print('SYNC FARM AGENT - ERROR: sync farm not responding')
                print(e)
        