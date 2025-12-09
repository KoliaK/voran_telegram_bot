# fake a website so the Cloud provider won't kill it for being just a background script

from flask import Flask
from threading import Thread
from dotenv import load_dotenv
import os

app = Flask('')

@app.route('/')
def home():
    bot_name = os.getenv('BOT_NAME', 'Voran') # default name if none is available
    return f'{bot_name} is alive!'

def run():
    # default is 8080 if running locally, otherwise, using PORT from Render Cloud service
    port = int(os.environ.get("PORT", 8080))
    # turn off debug mode and use_reloader to prevent Flask from interfering with signals
    # otherwise, it will keep listening for traffic and the CTRL+C command in the terminal won't work properly 
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()