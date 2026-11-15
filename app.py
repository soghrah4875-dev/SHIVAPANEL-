from flask import Flask, render_template, request, jsonify
import requests
import threading
import time
import logging

app = Flask(__name__)

# Logging setup taaki errors aur success messages console me dikhein
logging.basicConfig(level=logging.INFO)

is_raiding = False

def spam_worker(session_id, thread_id, message):
    global is_raiding
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-A505FN) AppleWebKit/537.36",
        "Cookie": f"sessionid={session_id};",
        "Referer": "https://www.instagram.com/"
    }
    
    url = f"https://i.instagram.com/api/v1/direct_v2/threads/broadcast/text/"
    
    msg_count = 1
    while is_raiding:
        try:
            payload = {
                "text": message, 
                "thread_ids": f"[{thread_id}]"
            }
            
            # Request bhej rahe hain (Timeout 10 seconds rakha hai taaki network hang na ho)
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            
            if response.status_code == 200:
                logging.info(f"[{msg_count}] SHIVA PANEL: Message sent successfully!")
            elif response.status_code == 401:
                logging.warning(f"[{msg_count}] Session ID expired or Auth Error! Status: 401")
            else:
                logging.warning(f"[{msg_count}] Failed with status: {response.status_code}")
                
            msg_count += 1

        except requests.exceptions.RequestException as e:
            # Agar internet chala jaye ya connection timeout ho toh script crash nahi hogi
            logging.error(f"Network error occurred: {e}")
            
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

        # Aapki requirement ke mutabiq: Exactly 40 seconds ka gap har message ke beech
        for _ in range(40):
            if not is_raiding:
                break
            time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_raid():
    global is_raiding
    if is_raiding:
        return jsonify({"status": "SHIVA PANEL: Raid is already running in background!"})
    
    data = request.json
    session_id = data.get('session_id')
    thread_id = data.get('thread_id')
    message = data.get('message')
    
    if not session_id or not thread_id or not message:
        return jsonify({"status": "All fields are required!"}), 400
        
    is_raiding = True
    
    # Background thread start kar rahe hain
    t = threading.Thread(target=spam_worker, args=(session_id, thread_id, message))
    t.daemon = True
    t.start()
    
    return jsonify({"status": "SHIVA PANEL: Raid started successfully! Running every 40 seconds."})

@app.route('/stop', methods=['POST'])
def stop_raid():
    global is_raiding
    is_raiding = False
    return jsonify({"status": "SHIVA PANEL: Raid Stopped Successfully!"})

if __name__ == '__main__':
    # 0.0.0.0 par run karne se yeh local network par bhi accessible rahega
    app.run(host='0.0.0.0', port=5000, debug=False)
  
