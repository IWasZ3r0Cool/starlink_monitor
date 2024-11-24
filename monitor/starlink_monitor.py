import os
import time
import subprocess
import sqlite3
import logging
from datetime import datetime
from threading import Thread
from flask import Flask, jsonify
from flask_cors import CORS
try:
    import speedtest
except ImportError:
    speedtest = None

# Configuration Variables
PING_INTERVAL = 2  # Ping interval in seconds
SPEEDTEST_INTERVAL = 600  # Speedtest interval in seconds
PING_TARGETS = ["8.8.8.8", "1.1.1.1", "www.google.com"]
DATABASE = "starlink_monitor.db"
FLASK_PORT = int(os.getenv("FLASK_PORT", 8080))

# Initialize logger
logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s", level=logging.INFO)

# Flask App
app = Flask(__name__)
CORS(app)  # Allow all origins by default


# Utility: Create Database Tables if they don't exist
def initialize_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pings (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     timestamp TEXT NOT NULL,
                     target TEXT NOT NULL,
                     success INTEGER NOT NULL
                 )''')
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
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute(
            'INSERT INTO pings (timestamp, target, success) VALUES (?, ?, ?)',
            (datetime.utcnow().isoformat(), target, int(success))
        )
        conn.commit()
        logging.info(f"[DB INSERT] Ping logged: target={target}, success={success}")
    except Exception as e:
        logging.error(f"Error logging ping result for {target}: {e}")
    finally:
        conn.close()


# Log Speed Test Results to SQLite
def log_speedtest_results(download=None, upload=None, ping=None):
    try:
        if download is None or upload is None or ping is None:
            logging.warning("Speedtest results are incomplete. Skipping database entry.")
            return
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute(
            'INSERT INTO speed_tests (timestamp, download, upload, ping) VALUES (?, ?, ?, ?)',
            (datetime.utcnow().isoformat(), download, upload, ping)
        )
        conn.commit()
        logging.info(f"[DB INSERT] Speedtest logged: download={download:.2f} Mbps, upload={upload:.2f} Mbps, ping={ping:.2f} ms")
    except Exception as e:
        logging.error(f"Error logging speedtest result: {e}")
    finally:
        conn.close()


# Run Periodic Pings
def ping_monitor():
    while True:
        for target in PING_TARGETS:
            try:
                # Perform a ping command
                result = subprocess.run(["ping", "-c", "1", target], capture_output=True, text=True)
                output = result.stdout.strip()
                success = result.returncode == 0

                if success:
                    logging.info(f"[PING SUCCESS] Target: {target}, Output: {output.splitlines()[-1]}")
                else:
                    logging.error(f"[PING FAILURE] Target: {target}, Error: {result.stderr.strip()}")

                log_ping(target, success)
            except Exception as e:
                logging.error(f"Ping error for {target}: {e}")
            time.sleep(PING_INTERVAL)


def speedtest_monitor():
    if not speedtest:
        logging.error("Speedtest module is not available. Skipping speedtest monitoring.")
        return
    
    while True:
        try:
            logging.info("Starting speedtest...")
            
            # Replace with specific server(s) to limit connection attempts
            st = speedtest.Speedtest()
            st.get_servers([12345])  # Replace 12345 with a preferred server ID after running speedtest-cli --list
            st.get_best_server()
            
            # Run download and optional upload tests
            download = st.download() / 1_000_000  # Convert bits to Mbps
            upload = st.upload() / 1_000_000      # Convert bits to Mbps
            ping = st.results.ping
            
            logging.info(f"[SPEEDTEST SUCCESS] Download={download:.2f} Mbps, Upload={upload:.2f} Mbps, Ping={ping:.2f} ms")
            log_speedtest_results(download, upload, ping)
        except speedtest.ConfigRetrievalError as e:
            logging.warning(f"[SPEEDTEST FAILURE] Speedtest configuration retrieval error: {e}")
        except Exception as e:
            logging.error(f"[SPEEDTEST FAILURE] Speedtest error: {e}")
        
        time.sleep(SPEEDTEST_INTERVAL)  # Adjust interval as needed


# Flask API: Expose Data to Frontend
@app.route('/api/pings', methods=['GET'])
def get_pings():
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM pings ORDER BY timestamp DESC LIMIT 100")
        rows = c.fetchall()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        logging.error(f"Failed to fetch pings: {e}")
        return jsonify({"error": "Failed to fetch pings"}), 500


@app.route('/api/speedtests', methods=['GET'])
def get_speedtests():
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM speed_tests ORDER BY timestamp DESC LIMIT 100")
        rows = c.fetchall()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        logging.error(f"Failed to fetch speedtests: {e}")
        return jsonify({"error": "Failed to fetch speedtests"}), 500


# Main Entry Point
if __name__ == "__main__":
    initialize_db()
    
    # Start threads
    Thread(target=ping_monitor, daemon=True).start()
    Thread(target=speedtest_monitor, daemon=True).start()

    # Start Flask server
    logging.info(f"Starting Flask server on port {FLASK_PORT}")
    app.run(host='0.0.0.0', port=FLASK_PORT)