import requests
import os
import wandb

HOSTNAME = os.environ.get('SYNC_FARM_HOSTNAME', 'localhost')
PORT = os.environ.get('SYNC_FARM_PORT', 57891)
SYNC_FARM_USERNAME = os.environ.get('SYNC_FARM_USERNAME', 'user')
SYNC_FARM_PASSWORD = os.environ.get('SYNC_FARM_PASSWORD', 'pass')

class SyncAgent:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
            return cls.instance
    
    def init(self, timeout=5, verbose=False) -> None:
        self.run_id = wandb.run.id
        self.run_dir = wandb.run.dir.removesuffix('/files')
        self.timeout = timeout
        self.verbose = verbose
        self.data = {
            'run_id': self.run_id,
            'run_dir': self.run_dir.removesuffix('/files'),
        }
    
    def trigger_sync(self):
        try:
            if self.verbose:
                print('SYNC FARM AGENT: Sending sync request')
            r = requests.post(f'https://{HOSTNAME}:{PORT}/sync', verify=False,
                                auth=(SYNC_FARM_USERNAME, SYNC_FARM_PASSWORD),
                                data=self.data, timeout=self.timeout)
            return r
        except Exception as e:
            if self.verbose:
                print('SYNC FARM AGENT: Error! sync farm not responding')
                print(e)
        