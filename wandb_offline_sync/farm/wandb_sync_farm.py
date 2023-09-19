from flask import Flask, request, jsonify, Response, render_template
from functools import wraps
import os
import subprocess
import sys
import argparse
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import time

# make a queue of runs to sync
class SetQueue(queue.Queue):
    def _init(self, maxsize):
        self.queue = set()
    def _put(self, item):
        self.queue.add(item)
    def _get(self):
        return self.queue.pop()
    def get_queue(self):
        return self.queue

run_queue = SetQueue()

app = Flask(__name__)

WANDB_SYNC_FARM_USERNAME = os.environ.get('WANDB_SYNC_FARM_USERNAME', 'user')
WANDB_SYNC_FARM_PASSWORD = os.environ.get('WANDB_SYNC_FARM_PASSWORD', 'pass')

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == WANDB_SYNC_FARM_USERNAME and auth.password == WANDB_SYNC_FARM_PASSWORD:
            return f(*args, **kwargs)
        return Response('Unauthorized\n', 401, {'WWW-Authenticate': 'Basic realm="Login!"'})
    return decorated

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/sync", methods=['POST'])
@auth_required
def sync():
    global verbose, run_queue
    if verbose:
        print('Received sync request')
    wandb_run_id = request.form['run_id']
    wandb_run_dir = request.form['run_dir']
    wandb_run_dir = wandb_run_dir.removesuffix('/files')
    run_queue.put((wandb_run_id, wandb_run_dir))
    return '', 200

def sync_run(wandb_run_id, wandb_run_dir, stdout, stderr):
    subprocess.run(['wandb', 'sync', wandb_run_dir, '--include-offline', '--id', wandb_run_id], stdout=stdout, stderr=stderr)

def manage_runs(args, run_queue):
    num_threads = args.num_threads
    executor = ThreadPoolExecutor(max_workers=num_threads)
    active_threads = set()
    stdout = sys.stdout if args.verbose else subprocess.DEVNULL
    stderr = sys.stderr if args.verbose else subprocess.DEVNULL
    while True:
        time.sleep(0.01)
        if not run_queue.empty() and len(active_threads) < num_threads:
            wandb_run_id, wandb_run_dir = run_queue.get()
            future = executor.submit(sync_run, wandb_run_id, wandb_run_dir, stdout, stderr)
            active_threads.add(future)
            future.add_done_callback(lambda x: active_threads.remove(x))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host address')
    parser.add_argument('--port', type=int, default=57891, help='Port')
    parser.add_argument('--cert', type=str, default='cert.pem', help='Path to SSL certificate')
    parser.add_argument('--key', type=str, default='key.pem', help='Path to SSL key')
    parser.add_argument('--verbose', action='store_true', help='Verbose mode')
    parser.add_argument('--num_threads', type=int, default=5, help='Number of threads')
    args = parser.parse_args()
    global stderr, stdout, verbose
    verbose = args.verbose
    stdout = sys.stdout if verbose else subprocess.DEVNULL
    stderr = sys.stderr if verbose else subprocess.DEVNULL
    # manage run sync in another thread
    threading.Thread(target=manage_runs, args=(args, run_queue), daemon=True).start()
    app.run(ssl_context=(args.cert, args.key), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
