# Wandb Offline Sync
Continuously sync offline wandb runs.

## Why?
If you work on computing nodes without internet access, you can use wandb in offline mode to log your runs. Normally you would sync an offline run to wandb at the end of the run, but if you have a long running job, you may want to sync your run during job's execution.

## How?
Firstly, you need to setup the sync farm:
* Install the requirements: `pip install -r requirements.txt`
* Run the script `generate_cert.sh` and follow the steps to generate a certificate, which will be used to encrypt the communication between the sync farm and the agent.
* Run `export SYNC_FARM_USERNAME=<your_username>; export SYNC_FARM_PASSWORD=<your_password>` to set the username and password for the sync farm. You can also put these commands in your `.bashrc` file.
* Run the script `sync_farm.py` in a node with internet connection. It will setup a https server that listens for sync requests. Run `sync_farm.py --help` to see the available options.
* Run `export SYNC_FARM_HOST=<sync_farm_host>; export SYNC_FARM_PORT=<sync_farm_port>` to set the host and port of the sync farm.

Then, in the code of your job, you need to setup the agent:
* import the agent: `import sync_agent`
* After calling `wandb.init(...)`, initialize the agent with: `sync_agent.init()`.
* After each call to `wandb.log(...)`, call `sync_agent.trigger_sync()` to request a sync to the farm.

## Notes
* Ensure that your job has the environment variables `SYNC_FARM_USERNAME` and `SYNC_FARM_PASSWORD` correctly set.
* Don't worry if for some minutes your run is not visible from the wandb website. Wait a few minutes and your run will appear. You can always set the `--verbose` option in the sync farm to see what is happening.
