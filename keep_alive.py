from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot HEYN4S sedang aktif."

def run_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def start_keep_alive():
    """Menjalankan web server di thread terpisah."""
    t = Thread(target=run_server)
    t.start()