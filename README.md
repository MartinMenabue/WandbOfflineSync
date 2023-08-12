# Wandb Offline Sync
Continuously sync offline wandb runs.

## Why?
If you work on computing nodes without internet access, you can use wandb in offline mode to log your runs. Normally you would sync an offline run to wandb at the end of the run, but if you have a long running job, you may want to sync your run during job's execution.

## Get Started
This project has two components:
* Farm: a https server that listens for sync requests and syncs the runs to wandb.
* Agent: a python module that you use in your code to request a sync to the farm.

To get started:
* Install the package: `pip install wandb-offline-sync`
* Generate a SSL certificate for the sync farm. You can use the command: `openssl req -newkey rsa:4096 -nodes -keyout key.pem -x509 -days 365 -out cert.pem`
* Run `export WANDB_SYNC_FARM_USERNAME=<your_username>; export WANDB_SYNC_FARM_PASSWORD=<your_password>` to set the username and password for the sync farm. You can also put these commands in your `.bashrc` file. Replace `<your_username>` and `<your_password>` with your credentials. If these variables are not set, the farm will use the default credentials `("user", "pass")`
* Run the farm with the command `wandb_sync_farm` in a node with internet connection. After that, the farm will listen for sync requests. Run `wandb_sync_farm --help` to see all the available options.
* Run `export WANDB_SYNC_FARM_HOST=<sync_farm_ip_address_or_hostname>; export WANDB_SYNC_FARM_PORT=<sync_farm_port>` to set the hostname and port of the sync farm. You can also put these commands in your `.bashrc` file. These variables will be used by the agent.

Then, in the code of your job, to use the agent:
* import the agent: `from wandb_offline_sync import agent`
* After calling `wandb.init(...)`, initialize the agent with: `agent.init()`. You can pass a `frequency` argument to set the minimum time between syncs (in seconds). For example, if you set `frequency=60`, the agent will request a sync at most once per minute. The default value for the frequency is 5 minutes.
* After each call to `wandb.log(...)`, call `agent.trigger_sync()` to request a sync to the farm.

## Notes
* In the first minutes of the run, it may happen that the sync farm fails in syncing the run to wandb. Don't worry, after some minutes the sync farm should be able to sync the run. You can always set the --verbose option when you run the sync farm to see what is happening.
