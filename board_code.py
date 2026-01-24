import network
import urequests
import time
import gc
import json
import os
from machine import Pin
from mfrc522 import MFRC522

# --- CONFIGURATION ---
WIFI_SSID = "Rishihood_Learner"
WIFI_PASS = "sru@2021"
SERVER_URL = "https://dvds-grand-readings-chronicles.trycloudflare.com/log_entry"
LOCATION_NAME = "loc_1"
OFFLINE_FILE = "offline_logs.json"

# --- NETWORK ---
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    time.sleep(0.2)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"Connecting to {WIFI_SSID}...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        for _ in range(10):
            if wlan.isconnected(): break
            time.sleep(1)
            
    if wlan.isconnected():
        print("WiFi OK:", wlan.ifconfig()[0])
        # Attempt to upload any saved offline data immediately
        process_offline_queue() 
        return True
    
    return False

# --- FILE STORAGE (OFFLINE) ---
def save_locally(payload):
    print("⚠️ Saving to local flash memory...")
    try:
        with open(OFFLINE_FILE, 'a') as f:
            # We add a generic timestamp just for ordering, since real time might be wrong
            payload['saved_at_uptime'] = time.ticks_ms()
            f.write(json.dumps(payload) + "\n")
        print("✅ Saved locally.")
    except Exception as e:
        print(f"❌ Storage Failed: {e}")

def process_offline_queue():
    """Reads offline file and tries to upload everything."""
    try:
        # Check if file exists
        try:
            os.stat(OFFLINE_FILE)
        except OSError:
            return # File doesn't exist, nothing to do

        print("♻️ Processing offline queue...")
        
        # Rename file to temporary so we don't conflict if new scans come in
        # (Simple implementation: just read and delete for now)
        with open(OFFLINE_FILE, 'r') as f:
            lines = f.readlines()
            
        if not lines:
            return

        print(f"Found {len(lines)} offline entries. Uploading...")
        
        failed_lines = []
        headers = {'Content-Type': 'application/json'}
        
        for line in lines:
            try:
                data = json.loads(line)
                # Try to upload
                res = urequests.post(SERVER_URL.strip(), json=data, headers=headers)
                if res.status_code == 200:
                    print(f"   Synced: {data.get('card_id')}")
                else:
                    failed_lines.append(line) # Keep it if server rejected
                res.close()
            except Exception:
                failed_lines.append(line) # Keep it if upload failed
        
        # Re-write the file with only the lines that failed (if any)
        if failed_lines:
            print(f"⚠️ {len(failed_lines)} entries failed to sync. Keeping them.")
            with open(OFFLINE_FILE, 'w') as f:
                for line in failed_lines:
                    f.write(line)
        else:
            print("🎉 All offline data synced!")
            os.remove(OFFLINE_FILE) # Clean up
            
    except Exception as e:
        print(f"Queue processing error: {e}")

# --- MAIN LOGIC ---
def log_to_server(uid_hex):
    gc.collect()
    payload = {
        "location": LOCATION_NAME,
        "card_id": uid_hex
    }
    headers = {'Content-Type': 'application/json'}
    
    # 1. Try Live Upload
    try:
        print(f"Uploading {uid_hex}...")
        res = urequests.post(SERVER_URL.strip(), json=payload, headers=headers)
        if res.status_code == 200:
            print("✅ Upload Success")
            res.close()
            # Since we are online, check if we have old data to clear
            process_offline_queue() 
        else:
            print(f"❌ Server Error {res.status_code}. Saving locally.")
            res.close()
            save_locally(payload)
            
    except Exception as e:
        print(f"❌ Network Error: {e}. Saving locally.")
        save_locally(payload)

def main():
    connect_wifi()
    
    try:
        rdr = MFRC522(sck=18, mosi=23, miso=19, rst=22, cs=5)
    except Exception as e:
        print("RFID INIT FAIL:", e)
        return

    print("READY. Scan card.")

    while True:
        # Check WiFi periodically and reconnect/sync if needed
        wlan = network.WLAN(network.STA_IF)
        if not wlan.isconnected():
            connect_wifi()

        stat, _ = rdr.request(rdr.REQIDL)
        if stat == rdr.OK:
            stat, raw_uid = rdr.anticoll()
            if stat == rdr.OK:
                uid_hex = "0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
                print("READ:", uid_hex)
                log_to_server(uid_hex)
                time.sleep(2)

main()
