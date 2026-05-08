from flask import Flask, render_template, request, jsonify
import requests
import os
import threading

app = Flask(__name__)

# --- የቴሌግራም መረጃዎች ---
BOT_TOKEN = "8696739619:AAHgsWzNmhkLBGdC_cBy-IXpiZ0RcQZZqpY"
ADMIN_ID = "7900431028"
CHANNEL_ID = "-1003606657314"
GROUP_ID = "-1003961942282"
AGENT_USERNAME = "chinetcomet"

def send_to_telegram(chat_id, message, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown", "reply_markup": reply_markup}
    try: return requests.post(url, json=payload, timeout=15).json()
    except: return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json(force=True)
        form_type = data.get('type')
        
        if form_type == 'load':
            msg = (f"🚚 *አዲስ የጭነት ጥያቄ*\n"
                   f"👤 የጭነት ባለቤት: {data.get('org', '---')}\n"
                   f"📞 ስልክ: {data.get('phone', '---')}\n"
                   f"📍 የጭነት መነሻ: {data.get('from', '---')}\n"
                   f"🏁 የጭነት መድረሻ: {data.get('to', '---')}\n"
                   f"📦 አይነት: {data.get('cargo', '---')}\n"
                   f"⚖️ መጠን: {data.get('amount', '---')}\n"
                   f"🚛 መኪና: {data.get('truckType', '---')}\n"
                   f"💰 ዋጋ: {data.get('price', '---')}\n"
                   f"📅 ቀን: {data.get('date', '---')}")
        else:
            msg = (f"🚛 *ጭነት እፈልጋለሁ (ሹፌር)*\n"
                   f"🚐 መኪና: {data.get('vType', '---')}\n"
                   f"🔢 ታርጋ: {data.get('plate', '---')}\n"
                   f"📍 ያለበት: {data.get('currentCity', '---')}\n"
                   f"🏁 መዳረሻ: {data.get('targetCity', '---')}\n"
                   f"👤 ሹፌር: {data.get('driverName', '---')}\n"
                   f"📞 ስልክ: {data.get('driverPhone', '---')}\n"
                   f"👥 ረዳት: {data.get('helperName', '---')}\n"
                   f"📞 ረዳት ስልክ: {data.get('helperPhone', '---')}")

        markup = {"inline_keyboard": [[{"text": "✅ Approve", "callback_data": "approve_post"},{"text": "❌ Reject", "callback_data": "reject_post"}]]}
        send_to_telegram(ADMIN_ID, f"⚠️ *አዲስ ጥያቄ መጥቷል!*\n\n{msg}", markup)
        return jsonify({"status": "success", "message": "መረጃው ተልኳል፤ አድሚን ሲያጸድቀው ይለጠፋል።"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

def bot_polling():
    last_update_id = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=20"
            updates = requests.get(url).json()
            if "result" in updates:
                for update in updates["result"]:
                    last_update_id = update["update_id"]
                    if "callback_query" in update:
                        cb = update["callback_query"]
                        raw_text = cb["message"]["text"].replace("⚠️ አዲስ ጥያቄ መጥቷል!\n\n", "")
                        
                        if cb["data"] == "approve_post":
                            lines = raw_text.split('\n')
                            # ታርጋ፣ ስምና ስልክን የማጣራት ስራ
                            filtered = [l for l in lines if not any(x in l for x in ["📞 ስልክ", "👤 ሹፌር", "👤 የጭነት ባለቤት", "👥 ረዳት", "📞 ረዳት ስልክ", "🔢 ታርጋ"])]
                            final_post = "\n".join(filtered) + f"\n\n📩 *መረጃውን ለማግኘት ኤጀንቱን ያነጋግሩ*👇"
                            agent_markup = {"inline_keyboard": [[{"text": "👤 Contact Agent", "url": f"https://t.me/{AGENT_USERNAME}"}]]}
                            
                            send_to_telegram(CHANNEL_ID, final_post, agent_markup)
                            send_to_telegram(GROUP_ID, final_post, agent_markup)
                            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText", 
                                          json={"chat_id": ADMIN_ID, "message_id": cb["message"]["message_id"], "text": f"✅ ተለጥፏል\n\n{raw_text}"})
                        elif cb["data"] == "reject_post":
                            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText", 
                                          json={"chat_id": ADMIN_ID, "message_id": cb["message"]["message_id"], "text": f"❌ ውድቅ ተደርጓል\n\n{raw_text}"})
        except: pass

threading.Thread(target=bot_polling, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
