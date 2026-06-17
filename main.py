import requests
import time
import threading
import os
from flask import Flask
from datetime import datetime
from dotenv import load_dotenv

# Load credentials
load_dotenv()

TOKEN = os.getenv("DISCORD_AUTH_TOKEN", "").strip().strip('"').strip("'")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID", "").strip().strip('"').strip("'")
PORT = int(os.getenv("PORT", 8080))

# Message interval set to exactly 60 seconds
MSG_INTERVAL = 60

def get_headers():
    return {
        "Authorization": TOKEN,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

# Diagnostic on startup
print("--- ENVIRONMENT CHECK ---")
print(f"TOKEN LOADED: {'YES' if TOKEN else 'NO'}")
print(f"CHANNEL ID: {CHANNEL_ID if CHANNEL_ID else 'MISSING'}")

# Token validation check
def validate_token():
    url = "https://discord.com/api/v9/users/@me"
    try:
        r = requests.get(url, headers=get_headers(), timeout=10)
        if r.status_code == 200:
            user = r.json()
            print(f"LOGIN SUCCESS: {user.get('username')} (ID: {user.get('id')})")
            return True
        else:
            print(f"LOGIN FAILED: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"VALIDATION EXCEPTION: {e}")
        return False

is_valid = validate_token()
print(f"INTERVAL: {MSG_INTERVAL}s")
print("-------------------------")

app = Flask(__name__)

@app.route('/')
def health_check():
    return f"Autosender Active. Target: {CHANNEL_ID if CHANNEL_ID else 'Not Set'}", 200

PROXY = os.getenv("PROXY_URL", "").strip()

def send_message():
    if not TOKEN or not CHANNEL_ID:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] SKIP: Missing Token or Channel ID.", flush=True)
        return
    
    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"
    proxies = {"http": PROXY, "https": PROXY} if PROXY else None
    
    # Track consecutive rate limits to implement backoff
    rate_limit_count = 0
    
    try:
        if not os.path.exists("msg.txt"):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: msg.txt NOT FOUND", flush=True)
            return
            
        with open("msg.txt", "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        if not content:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: msg.txt is empty.", flush=True)
            return

        while True:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Attempting to send message...", flush=True)
            try:
                response = requests.post(
                    url, 
                    headers=get_headers(), 
                    json={"content": content}, 
                    proxies=proxies,
                    timeout=15
                )
            except requests.exceptions.ProxyError:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] PROXY ERROR: Could not connect to proxy.", flush=True)
                break

            if response.status_code == 200:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Sent successfully.", flush=True)
                break
            elif response.status_code == 429:
                rate_limit_count += 1
                retry_after = response.json().get("retry_after", 5)
                
                # Conversion logic
                sleep_time = retry_after if retry_after < 100 else retry_after / 1000
                
                # If we're stuck in a loop, add extra penalty time (Exponential-ish Backoff)
                penalty = min(rate_limit_count * 2, 30) 
                total_wait = sleep_time + penalty + 0.5
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] RATE LIMITED (Attempt {rate_limit_count}): Waiting {total_wait:.1f}s (Discord: {sleep_time}s + Penalty: {penalty}s)", flush=True)
                
                if rate_limit_count > 5 and not PROXY:
                    print(f"!!! WARNING: Your hosting IP seems to be HARD BLOCKED by Discord. Use a PROXY !!!", flush=True)
                
                time.sleep(total_wait)
                continue 
            elif response.status_code == 401:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: 401 Unauthorized.", flush=True)
                break
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: {response.status_code} - {response.text}", flush=True)
                break
            
    except Exception as e:
        print(f"EXCEPTION in send_message: {e}", flush=True)

def autosender_loop():
    while True:
        send_message()
        time.sleep(MSG_INTERVAL)

# Start background thread
print("[*] Starting autosender thread...")
threading.Thread(target=autosender_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
else:
    # Support for Gunicorn
    print("[*] Web server instance started.")
