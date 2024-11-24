import os
import time
import subprocess
import sqlite3
from datetime import datetime
from threading import Thread
import speedtest
from flask import Flask, jsonify

# Configuration Variables
PING_INTERVAL = 10  # in seconds
SPEEDTEST_INTERVAL = 300  # in seconds (5 minutes)
PING_TARGETS = ["8.8.8.8", "1.1.1.1", "www.google.com"]
DATABASE = "starlink_monitor.db"
FLASK_PORT = int(os.getenv("FLASK_PORT", 8080))  # Port for Flask (default: 8080)

# Flask App (to serve the SQLite data)
app = Flask(__name__)


# Utility: Create Database and Tables
def initialize_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Create Pings Table
    c.execute('''CREATE TABLE IF NOT EXISTS pings (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     timestamp TEXT NOT NULL,
                     target TEXT NOT NULL,
                     success INTEGER NOT NULL
                 )''')
    # Create Speed Tests Table
    c.execute('''CREATE TABLE IF NOT EXISTS speed_tests (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     timestamp TEXT NOT NULL,
                     download REAL NOT NULL,
                     upload REAL NOT NULL,
                     ping REAL NOT NULL
                 )''')
    conn.commit()
    conn.close()


# Log Ping Results to SQLite
def log_ping(target, success):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO pings (timestamp, target, success) VALUES (?, ?, ?)',
              (datetime.utcnow().isoformat(), target, int(success)))
    conn.commit()
    conn.close()


# Log Speed Test Results to SQLite
def log_speedtest_results(download, upload, ping_result):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO speed_tests (timestamp, download, upload, ping) VALUES (?, ?, ?)',
              (datetime.utcnow().isoformat(), download, upload, ping_result))
    conn.commit()
    conn.close()


# Run Periodic Pings
def ping_monitor():
    while True:
        for target in PING_TARGETS:
            try:
                # Perform a ping using `ping` command
                result = subprocess.run(["ping", "-c", "1", target], stdout=subprocess.DEVNULL)
                success = result.returncode == 0
            except Exception as e:
                success = 0
                print(f"Ping Error: {e}")
            log_ping(target, success)
        time.sleep(PING_INTERVAL)


# Run Periodic Speed Tests
def speedtest_monitor():
    st = speedtest.Speedtest()
    st.get_best_server()
    while True:
        try:
            download = st.download() / 1_000_000  # Convert to Mbps
            upload = st.upload() / 1_000_000      # Convert to Mbps
            ping_result = st.results.ping
            log_speedtest_results(download, upload, ping_result)
        except Exception as e:
            print(f"Speedtest Error: {e}")
        time.sleep(SPEEDTEST_INTERVAL)


# Flask API: Expose Data for Frontend
@app.route('/api/pings', methods=['GET'])
def get_pings():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM pings ORDER BY timestamp DESC LIMIT 100")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)


@app.route('/api/speedtests', methods=['GET'])
def get_speedtests():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM speed_tests ORDER BY timestamp DESC LIMIT 100")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)


# Main Function
if __name__ == "__main__":
    initialize_db()
    # Start Background Threads
    Thread(target=ping_monitor, daemon=True).start()
    Thread(target=speedtest_monitor, daemon=True).start()
    # Start Flask Server
    app.run(host='0.0.0.0', port=FLASK_PORT)