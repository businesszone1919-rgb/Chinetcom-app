from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# --- የቴሌግራም መረጃዎች ---
BOT_TOKEN = "8696739619:AAHgsWzNmhkLBGdC_cBy-IXpiZ0RcQZZqpY"

# መረጃ የሚላክባቸው ቦታዎች (IDs) ዝርዝር
# አሁን ባለው ሁኔታ ለቻናልህ ተዘጋጅቷል፤ የግሩፕ ID ሲኖርህ እዚህ ዝርዝር ውስጥ መጨመር ትችላለህ
TARGET_CHATS = [
    "-1002426865615",  # የ Chinet com ቻናል ID
]

def send_to_telegram(message):
    """መረጃውን በ TARGET_CHATS ውስጥ ላሉ ቦታዎች በሙሉ ይልካል"""
    for chat_id in TARGET_CHATS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            print(f"Sent to {chat_id}: {response.status_code}")
        except Exception as e:
            print(f"Error sending to {chat_id}: {e}")

@app.route('/')
def index():
    # በ templates ፎልደር ውስጥ ያለውን index.html ይከፍታል
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # ከዌብሳይቱ (Frontend) የሚመጣውን መረጃ መቀበል
        data = request.get_json(force=True)
        
        if data.get('type') == 'load':
            msg = (f"🚚 *አዲስ የጭነት ጥያቄ*\n\n"
                   f"🏢 *ድርጅት:* {data.get('org', '---')}\n"
                   f"👤 *ተጠሪ:* {data.get('name', '---')}\n"
                   f"📞 *ስልክ:* {data.get('phone', '---')}\n"
                   f"📍 *መነሻ:* {data.get('from', '---')}\n"
                   f"🏁 *መድረሻ:* {data.get('to', '---')}\n"
                   f"🚛 *መኪና:* {data.get('truck', '---')}\n"
                   f"📝 *ዝርዝር:* {data.get('desc', '---')}")
        else:
            msg = (f"🚐 *አዲስ የሹፌር ምዝገባ*\n\n"
                   f"👤 *ሹፌር:* {data.get('dName', '---')}\n"
                   f"📞 *ስልክ:* {data.get('dPhone', '---')}\n"
                   f"🔢 *ሰሌዳ:* {data.get('plate', '---')}\n"
                   f"🚛 *የመኪና አይነት:* {data.get('vType', '---')}")
        
        # መልእክቱን ለሁሉም ኢላማዎች መላክ
        send_to_telegram(msg)
        return jsonify({"status": "success", "message": "መረጃው በስኬት ተልኳል!"})
        
    except Exception as e:
        print(f"Processing Error: {e}")
        return jsonify({"status": "error", "message": "ስህተት ተከስቷል"}), 400

if __name__ == '__main__':
    # Render ላይ እንዲሰራ ፖርቱን ከ Environment Variable ያነባል
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
