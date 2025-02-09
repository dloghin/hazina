import asyncio
from threading import Lock, Thread
from flask import Flask, json, request
from trader import run_trader_ollama, run_trader_openai, stop_trader

api = Flask(__name__)

lock = Lock()
messages = []

def save_message(message):
    global messages
    global lock
    with lock:
      messages.append(message)
    print(message)

def pop_messages():
    global messages
    ret = json.dumps(messages)
    with lock:
      messages = []
    return ret

def run_trader(provider):
    if provider == "ollama":
      asyncio.run(run_trader_ollama(save_message))
    else:
      asyncio.run(run_trader_openai(save_message))

@api.route('/start', methods=['POST'])
def start_trader_ep():
    provider = request.args['model']
    if provider not in ["ollama", "openai"]:
       return json.dumps({"success": False, "error": "unknown models provider"}), 201
    task = Thread(target=run_trader, args=[provider])
    task.start()
    return json.dumps({"success": True}), 201

@api.route('/stop', methods=['POST'])
def stop_trader_ep():
    stop_trader()
    return json.dumps({"success": True}), 201

@api.route('/messages', methods=['GET'])
def get_messages_ep():
    return json.dumps({"success": True, "data": pop_messages()}), 201

if __name__ == '__main__':
    api.run()