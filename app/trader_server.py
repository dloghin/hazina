import asyncio
from threading import Lock, Thread
from flask import Flask, json, request
from trader import run_trader_ollama, run_trader_openai, stop_trader
from flask_executor import Executor

api = Flask(__name__)
executor = Executor(api)

# Support only one task at a time
msg_lock = Lock()
messages = []
run_lock = Lock()


def save_message(message):
    global messages
    global msg_lock
    with msg_lock:
        messages.append(message)
    print(message)


def pop_messages():
    global messages
    global msg_lock
    ret = json.dumps(messages)
    with msg_lock:
        messages = []
    return ret


def run_trader(provider):
    if provider == "ollama":
        print("[INFO] run trader with ollama")
        asyncio.run(run_trader_ollama(save_message))
    else:
        print("[INFO] run trader with openai")
        asyncio.run(run_trader_openai(save_message))
    print("[INFO] run trader done")


@api.route("/start", methods=["POST"])
def start_trader_ep():
    provider = request.args["model"]
    if provider not in ["ollama", "openai"]:
        return json.dumps({"success": False, "error": "unknown models provider"}), 201
    global run_lock
    if run_lock.acquire(blocking=False):
        executor.submit(run_trader, provider)
    else:
        return json.dumps({"success": False, "error": "a task is already running"}), 201
    return json.dumps({"success": True}), 201


@api.route("/stop", methods=["POST"])
def stop_trader_ep():
    stop_trader()
    return json.dumps({"success": True}), 201


@api.route("/messages", methods=["GET"])
def get_messages_ep():
    return json.dumps({"success": True, "data": pop_messages()}), 201


if __name__ == "__main__":
    api.run(host="0.0.0.0")
