from flask import Flask, request, jsonify, Response, render_template
from functools import wraps
import os
import subprocess
import sys
import argparse
import base64

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
    global verbose
    if verbose:
        print('Received sync request')
    wandb_run_id = request.form['run_id']
    wandb_run_dir = request.form['run_dir']
    wandb_run_dir = wandb_run_dir.removesuffix('/files')
    global stdout, stderr
    subprocess.Popen(['wandb', 'sync', wandb_run_dir, '--id', wandb_run_id, '--include-offline'],
                         stderr=stderr, stdout=stdout)
    return '', 200

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host address')
    parser.add_argument('--port', type=int, default=57891, help='Port')
    parser.add_argument('--cert', type=str, default='cert.pem', help='Path to SSL certificate')
    parser.add_argument('--key', type=str, default='key.pem', help='Path to SSL key')
    parser.add_argument('--verbose', action='store_true', help='Verbose mode')
    args = parser.parse_args()
    global stderr, stdout, verbose
    verbose = args.verbose
    stdout = sys.stdout if verbose else subprocess.DEVNULL
    stderr = sys.stderr if verbose else subprocess.DEVNULL
    app.run(ssl_context=(args.cert, args.key), host=args.host, port=args.port)

if __name__ == "__main__":
    main()
