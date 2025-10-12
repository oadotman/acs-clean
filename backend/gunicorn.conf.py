# Gunicorn configuration for AdCopySurge Backend VPS Deployment
import multiprocessing
import os

# Server socket
bind = "unix:/run/adcopysurge/gunicorn.sock"
backlog = 2048

# Worker processes - optimized for VPS
workers = min(4, multiprocessing.cpu_count() * 2 + 1)  # Cap at 4 workers for VPS
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 60  # Increased for AI processing
keepalive = 2

# Logging
accesslog = "/var/log/adcopysurge/access.log"
errorlog = "/var/log/adcopysurge/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "adcopysurge-backend"

# Server mechanics
daemon = False
pidfile = "/run/adcopysurge/gunicorn.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Environment variables
raw_env = [
    "PYTHONPATH=/home/deploy/adcopysurge/backend",
    "PYTHONDONTWRITEBYTECODE=1",
    "PYTHONUNBUFFERED=1",
]

# Worker process callbacks
def on_starting(server):
    server.log.info("Starting AdCopySurge API server")

def on_reload(server):
    server.log.info("Reloading AdCopySurge API server")

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_fork(server, worker):
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_worker_init(worker):
    worker.log.info("Worker initialized")

def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal")
