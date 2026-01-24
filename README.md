
---

# ESP32 RFID Attendance System (Store-and-Forward)

This project implements a robust RFID attendance logging system designed for unstable network environments. It uses an ESP32 and RC522 module to scan cards and sync data to a Python Flask server.

**Key Features:**

* **Online Mode:** Real-time data transmission to a central server via a secure Cloudflare Tunnel (bypassing strict firewalls).
* **Offline Mode:** Automatically saves data to local flash memory when Wi-Fi or the server is unreachable.
* **Auto-Sync:** Uploads the local backlog automatically once connectivity is restored.

---

## 🛠️ Hardware Requirements

* **ESP32 Development Board** (ESP-WROOM-32 or similar)
* **MFRC522 RFID Reader Module**
* **Jumper Wires** (Female-to-Male)
* **Host Computer** (Running the Python Server & Cloudflared)
* **Micro-USB Cable** (Data capable)

## 🔌 Wiring Diagram

Connect the MFRC522 reader to the ESP32 pins as follows:

| MFRC522 Pin | ESP32 Pin | Function |
| --- | --- | --- |
| **SDA (SS)** | GPIO 5 | Chip Select |
| **SCK** | GPIO 18 | SPI Clock |
| **MOSI** | GPIO 23 | SPI MOSI |
| **MISO** | GPIO 19 | SPI MISO |
| **IRQ** | *Not Connected* | Interrupt |
| **GND** | GND | Ground |
| **RST** | GPIO 22 | Reset |
| **3.3V** | 3.3V | Power (Do not use 5V) |

---

## 💻 Part 1: Server Setup

### 1. Install Dependencies

Ensure Python is installed on your host machine. Install the required Flask framework:

```bash
pip install flask

```

### 2. Set Up Cloudflare Tunnel

The system uses Cloudflare Tunnels to allow the ESP32 to communicate with your localhost server, even if you are behind a university or office firewall.

1. **Install `cloudflared`:**
* **macOS:** `brew install cloudflare/cloudflare/cloudflared`
* **Windows:** Download `cloudflared.exe` from the official Cloudflare website.


2. **Start the Tunnel:**
Run the following command in your terminal to expose port 5050:
```bash
cloudflared tunnel --url http://localhost:5050

```


3. **Copy the URL:**
Note the unique URL provided in the terminal output (ending in `.trycloudflare.com`). You will need this for the ESP32 configuration.

### 3. Prepare the Server Script

Ensure `server.py` is in your project directory. No modification is needed unless you want to change the database filename or port.

---

## 🤖 Part 2: Board Setup (ESP32)

### 1. Install MicroPython Firmware

1. Download and install **Thonny IDE**.
2. Connect your ESP32 to the computer via USB.
3. Open Thonny and go to **Tools > Options > Interpreter**.
4. Select **MicroPython (ESP32)** from the dropdown.
5. Click **"Install or update MicroPython"** (bottom right).
6. Select the target USB port and the firmware variant. Click **Install**.

### 2. Upload Libraries

The `main.py` script requires the `mfrc522.py` library to interface with the hardware.

1. Open the `mfrc522.py` file provided in this repository (or download a compatible driver).
2. Save it directly to the **MicroPython Device** root directory via Thonny.

### 3. Configure and Upload Main Script

1. Open `main.py` in Thonny.
2. **Update Configuration:** Locate the configuration section at the top of the file and update the following:
* `WIFI_SSID`: Your Wi-Fi network name.
* `WIFI_PASS`: Your Wi-Fi password.
* `SERVER_URL`: The Cloudflare Tunnel URL you generated in Part 1 (ensure there are no trailing spaces).


3. **Save to Device:** Save the file as `main.py` on the ESP32.

---

## 🚀 Running the System

Follow this specific order every time you restart the system:

1. **Start the Cloudflare Tunnel:**
Run the `cloudflared` command in a terminal. **Note:** If you restart the tunnel, the URL will change. You must update `main.py` with the new URL.
2. **Start the Python Server:**
Run `python server.py` in a separate terminal window.
3. **Power the ESP32:**
Plug in the board. Monitor the Thonny console or the Python server terminal.
* **Success:** The server terminal will print "✅ LOGGED" when a card is scanned.
* **Offline:** The board will print "⚠️ Saving to local flash memory" if the server is unreachable.



---

## ❓ Troubleshooting

* **Upload Failed: Unsupported protocol:** Check `main.py`. The `SERVER_URL` likely has a leading or trailing space (e.g., `" https://..."`).
* **Error -202 / SSL Handshake Fail:** The ESP32 system time is incorrect. Ensure the board can access the internet to sync time via NTP.
* **Web Filter Violation (403):** The network (e.g., University Wi-Fi) is blocking the tunneling service. Connect the ESP32 to a mobile hotspot instead.
