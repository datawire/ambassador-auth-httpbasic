from flask import Flask, request, redirect, jsonify

app = Flask(__name__)


@app.route("/healthz", methods=["GET"])
def healthz():
    return "OK", 200
