# fake a website so the Cloud provider won't kill it for being just a background script

from flask import Flask
from threading import Thread
from dotenv import load_dotenv
import os

app = Flask('')

@app.route('/')
def home():
    bot_name = os.getenv('BOT_NAME')
    return f'{bot_name} is alive!'

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()