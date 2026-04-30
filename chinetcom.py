from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# --- ያቀረብካቸው የቴሌግራም መረጃዎች ---
BOT_TOKEN = "8696739619:AAHgsWzNmhkLBGdC_cBy-IXpiZ0RcQZZqpY"
CHAT_ID = "-1002426865615"

def send_to_telegram(message):
    """መረጃውን ወደ ቴሌግራም ቻናል የሚልክ ተግባር"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Telegram Response: {response.status_code}")
    except Exception as e:
        print(f"የቴሌግራም ስህተት: {e}")

@app.route('/')
def index():
    # ይህ መስመር በ templates ፎልደር ውስጥ ያለውን index.html ይከፍታል
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # ከብሮውዘር የሚመጣውን መረጃ በትክክል መቀበል
        data = request.get_json(force=True)
        print(f"መረጃ ደርሷል: {data}")
        
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
        return jsonify({"status": "success", "message": "መረጃው በተሳካ ሁኔታ ተልኳል!"})
    except Exception as e:
        print(f"የማቀናበር ስህተት: {e}")
        return jsonify({"status": "error", "message": "ስህተት ተከስቷል"}), 400

if __name__ == '__main__':
    # ሰርቨሩን በፖርት 5000 ላይ ያስነሳል
    app.run(host='0.0.0.0', port=5000, debug=True)
