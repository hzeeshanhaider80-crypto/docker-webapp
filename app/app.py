
"""A small Flask web app that counts visits using Redis."""

import os
import socket

import redis
from flask import Flask, jsonify, render_template
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

# Load secret key securely from environment variables.
secret_key = os.getenv("SECRET_KEY")

if not secret_key:
    raise RuntimeError("SECRET_KEY environment variable is required")

app.config["SECRET_KEY"] = secret_key

# Enable CSRF protection for state-changing requests.
csrf = CSRFProtect(app)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
APP_VERSION = os.getenv("APP_VERSION", "local")

# Redis connection
cache = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    socket_connect_timeout=2,
    decode_responses=True
)


def get_visits():
    """Increment visit counter and return its value."""
    try:
        return cache.incr("visits")
    except redis.exceptions.RedisError:
        return None


@app.route("/")
def home():
    return render_template(
        "index.html",
        visits=get_visits(),
        version=APP_VERSION,
        container=socket.gethostname(),
    )


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/api/info")
def info():
    return jsonify(
        version=APP_VERSION,
        container=socket.gethostname()
    )
