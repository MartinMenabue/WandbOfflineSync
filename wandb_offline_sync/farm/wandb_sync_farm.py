from flask import Flask, request, jsonify, Response, render_template
from functools import wraps
import os
import subprocess
import sys
import argparse

app = Flask(__name__)

SYNC_FARM_USERNAME = os.environ.get('SYNC_FARM_USERNAME', 'user')
SYNC_FARM_PASSWORD = os.environ.get('SYNC_FARM_PASSWORD', 'pass')

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == SYNC_FARM_USERNAME and auth.password == SYNC_FARM_PASSWORD:
            return f(*args, **kwargs)
        return Response('Login!', 401, {'WWW-Authenticate': 'Basic realm="Login!"'})
    return decorated

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/sync", methods=['POST'])
@auth_required
def sync():
    print('Received sync request')
    wandb_run_id = request.form['run_id']
    wandb_run_dir = request.form['run_dir']
    wandb_run_dir = wandb_run_dir.removesuffix('/files')
    subprocess.Popen(['wandb', 'sync', wandb_run_dir, '--id', wandb_run_id, '--include-offline'],
                         stderr=globals()['stderr'], stdout=globals()['stdout'])
    return '', 200

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host address')
    parser.add_argument('--port', type=int, default=57891, help='Port')
    parser.add_argument('--cert', type=str, default='cert.pem', help='Path to SSL certificate')
    parser.add_argument('--key', type=str, default='key.pem', help='Path to SSL key')
    parser.add_argument('--verbose', action='store_true', help='Verbose mode')
    args = parser.parse_args()
    global stderr, stdout
    stdout = sys.stdout if args.verbose else None
    stderr = sys.stderr if args.verbose else None
    app.run(ssl_context=(args.cert, args.key), host=args.host, port=args.port)

if __name__ == "__main__":
    main()
