from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# --- የቴሌግራም መረጃዎች ---
BOT_TOKEN = "8696739619:AAHgsWzNmhkLBGdC_cBy-IXpiZ0RcQZZqpY"
TARGET_CHATS = ["-1003606657314", "-1003961942282"]

def send_to_telegram(message):
    for chat_id in TARGET_CHATS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload, timeout=15)
        except Exception as e:
            print(f"Error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json(force=True)
        if data.get('type') == 'load':
            # የአስጫኝ መልእክት ስልክ ቁጥር ተጨምሮበታል
            msg = (f"🚚 *አዲስ የጭነት ጥያቄ (መኪና ፈላጊ)*\n\n"
                   f"👤 *ባለቤት/ድርጅት:* {data.get('org', '---')}\n"
                   f"📞 *ስልክ:* {data.get('phone', '---')}\n"
                   f"📍 *መነሻ ቦታ:* {data.get('from', '---')}\n"
                   f"🏁 *መድረሻ ቦታ:* {data.get('to', '---')}\n"
                   f"📦 *የጭነት አይነት:* {data.get('cargo', '---')}\n"
                   f"⚖️ *የጭነት መጠን:* {data.get('amount', '---')}\n"
                   f"🚛 *የመኪና አይነት:* {data.get('truckType', '---')}\n"
                   f"💰 *የሚከፈል ዋጋ:* {data.get('price', '---')}\n"
                   f"📅 *የመጫኛ ቀን:* {data.get('date', '---')}")
        else:
            msg = f"🚐 *አዲስ የሹፌር ምዝገባ*\n\n👤 ሹፌር: {data.get('dName')}\n📞 ስልክ: {data.get('dPhone')}"
        
        send_to_telegram(msg)
        return jsonify({"status": "success", "message": "መረጃው በተሳካ ሁኔታ ተልኳል!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
