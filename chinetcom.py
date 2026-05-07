from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# --- የቴሌግራም መረጃዎች ---
BOT_TOKEN = "8696739619:AAHgsWzNmhkLBGdC_cBy-IXpiZ0RcQZZqpY"

# ትክክለኛዎቹን IDs እዚህ ጋር እናረጋግጣለን
TARGET_CHATS = [
    "-1003606657314",  # የቻናል ID
    "-1003961942282",  # የግሩፕ ID
]

def send_to_telegram(message):
    """መረጃውን ወደ ቴሌግራም ይልካል እና ውጤቱን በ Log ያሳያል"""
    for chat_id in TARGET_CHATS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=payload, timeout=15)
            # ይህ መስመር በ Render Log ላይ ውጤቱን ያሳያል (በጣም አስፈላጊ ነው)
            print(f"DEBUG: Telegram Response for {chat_id}: {response.text}")
        except Exception as e:
            print(f"DEBUG: Connection Error for {chat_id}: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json(force=True)
        print(f"DEBUG: Received data: {data}") # የመጣውን መረጃ ቼክ ለማድረግ
        
        if data.get('type') == 'load':
            msg = (f"🚚 *አዲስ የጭነት ጥያቄ*\n\n"
                   f"🏢 *ድርጅት:* {data.get('org', '---')}\n"
                   f"👤 *ተጠሪ:* {data.get('name', '---')}\n"
                   f"📞 *ስልክ:* {data.get('phone', '---')}\n"
                   f"📍 *መነሻ:* {data.get('from', '---')}\n"
                   f"🏁 *መድረሻ:* {data.get('to', '---')}\n"
                   f"🚛 *መኪና:* {data.get('truck', '---')}")
        else:
            msg = (f"🚐 *አዲስ የሹፌር ምዝገባ*\n\n"
                   f"👤 *ሹፌር:* {data.get('dName', '---')}\n"
                   f"📞 *ስልክ:* {data.get('dPhone', '---')}\n"
                   f"🔢 *ሰሌዳ:* {data.get('plate', '---')}\n"
                   f"🚛 *አይነት:* {data.get('vType', '---')}")
        
        send_to_telegram(msg)
        return jsonify({"status": "success", "message": "መረጃው ተልኳል!"})
    except Exception as e:
        print(f"DEBUG: Server Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
