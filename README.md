# Wandb Offline Sync
Continuously sync offline wandb runs.

## Why?
If you work on computing nodes without internet access, you can use wandb in offline mode to log your runs. Normally you would sync an offline run to wandb at the end of the run, but if you have a long running job, you may want to sync your run during job's execution.

## How it works
This project has two components:
* Farm: a https server that listens for sync requests and syncs the runs to wandb.
* Agent: a python module that you use in your code to request the syncs to the farm.

## Quickstart
* Install this package: `pip install wandb-offline-sync`
* Generate a SSL certificate for the sync farm. You can use the command: `openssl req -newkey rsa:4096 -nodes -keyout key.pem -x509 -days 365 -out cert.pem`. This command will create two files: `cert.pem` and `key.pem`.
* Run `export WANDB_SYNC_FARM_USERNAME=<your_username>; export WANDB_SYNC_FARM_PASSWORD=<your_password>` to set the username and password for the sync farm. You can also put these commands in your `.bashrc` file. Replace `<your_username>` and `<your_password>` with your credentials. If these variables are not set, the farm will use the default credentials `("user", "pass")`
* Run the farm with the command `wandb_sync_farm --cert=<path_to_cert.pem> --key=<path_to_key.pem>` in a node with internet connection. The farm will listen for sync requests. Run `wandb_sync_farm --help` to see all the available options.
* Run `export WANDB_SYNC_FARM_HOST=<sync_farm_ip_address_or_hostname>; export WANDB_SYNC_FARM_PORT=<sync_farm_port>` to set the hostname and port of the sync farm. You can also put these commands in your `.bashrc` file. These variables will be used by the agent.

In the code of your job:
* Import the agent: `from wandb_offline_sync import agent`
* After calling `wandb.init(...)`, initialize the agent with: `agent.init(...)`. You can pass a `frequency` argument to set the minimum time between syncs (in seconds). For example, if you set `frequency=60`, the agent will request a sync at most once per minute. The default value for the frequency is 5 minutes.

Each time `wandb.log(...)` is called, the agent will check if the minimum time interval (given by the frequency) between syncs has passed, and if so, it will request a sync to the farm.

When `wandb.finish()` is called, the agent will wait some seconds (default is 30) to ensure that previous syncs have been completed, and then it will request a final sync to the farm.

## Notes
* If you run the farm with `--verbose`, it may happen that in the first minutes of the run, the output shows the error `.wandb file is empty`, and the run is not synced to the wandb server. Don't worry, after some minutes the data of the run will be available and will be synced to the wandb server.
