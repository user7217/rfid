import json
import os
import datetime # Import datetime
from flask import Flask, request

app = Flask(__name__)
DB_FILE = 'rfid_logs.json'

@app.route('/log_entry', methods=['POST'])
def log_entry():
    new_entry = request.json
    
    # --- SERVER SIDE TIMESTAMPING ---
    # Get current time on the laptop
    now = datetime.datetime.now()
    new_entry['timestamp'] = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # Save to file (same as before)
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                log_history = json.load(f)
        except:
            log_history = []
    else:
        log_history = []
    
    log_history.append(new_entry)
    
    with open(DB_FILE, 'w') as f:
        json.dump(log_history, f, indent=4)
        
    print(f"✅ LOGGED: {new_entry['card_id']} at {new_entry['timestamp']}")
    return "Saved", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)