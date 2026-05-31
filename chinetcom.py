from flask import Flask, render_template, request, jsonify
import requests
import os
import threading

app = Flask(__name__)

# --- የቴሌግራም እና የቦት መረጃዎች ---
BOT_TOKEN = "8696739619:AAHgsWzNmhkLBGdC_cBy-IXpiZ0RcQZZqpY"
ADMIN_ID = "7900431028"
CHANNEL_ID = "-1003606657314"
GROUP_ID = "-1003961942282"
AGENT_USERNAME = "chinetcomet"

BOT_LINK = "https://t.me/chinetcombot"
CHANNEL_LINK = "https://t.me/chinetcom"
GROUP_LINK = "https://t.me/chinetcometh"

COUNTER_FILE = "id_counter.txt"

def get_next_post_id():
    """የመጨረሻውን ቁጥር ከፋይል አንብቦ በአንድ ይጨምራል፣ ፋይሉ ከሌለ አዲስ ይፈጥራል"""
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            f.write("1")
        current_id = 1
    else:
        with open(COUNTER_FILE, "r") as f:
            try:
                current_id = int(f.read().strip())
            except ValueError:
                current_id = 1
    
    next_id = current_id + 1
    with open(COUNTER_FILE, "w") as f:
        f.write(str(next_id))
        
    return f"CC{current_id:05d}"

def send_to_telegram(chat_id, message, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": reply_markup
    }
    try:
        return requests.post(url, json=payload, timeout=15).json()
    except:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json(force=True)
        form_type = data.get('type')
        
        if form_type == 'load':
            org = data.get('org', '---')
            phone = data.get('phone', '---')
            dep = data.get('from', '---')
            to = data.get('to', '---')
            cargo = data.get('cargo', '---')
            amount = data.get('amount', '---')
            truck = data.get('truckType', '---')
            price = data.get('price', '---')
            date = data.get('date', '---')

            admin_msg = (
                "⚠️ <b>አዲስ ጥያቄ መጥቷል! [ጭነት]</b>\n\n"
                "📦 <b>[የሚጫን ጭነት አለኝ]</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f" ○   <b>የጭነት ባለቤት:-</b> {org}\n"
                f" ○   <b>ስልክ:-</b> <code>{phone}</code>\n"
                f" ○   <b>መነሻ (From):-</b> {dep}\n"
                f" ○   <b>መድረሻ (To):-</b> {to}\n"
                f" ○   <b>የጭነት አይነት:-</b> <code>{cargo}</code>\n"
                f" ○   <b>መጠን:-</b> {amount} ኩንታል/ቶን\n"
                f" ○   <b>የሚፈለግ መኪና:-</b> {truck}\n"
                f" ○   <b>የተመደብ ዋጋ:-</b> {price} ETB\n"
                f" ○   <b>ቀን:-</b> {date}\n"
                "━━━━━━━━━━━━━━━━━━━━"
            )
        else:
            v_type = data.get('vType', '---')
            plate = data.get('plate', '---')
            curr_city = data.get('currentCity', '---')
            target_city = data.get('targetCity', '---')
            driver = data.get('driverName', '---')
            d_phone = data.get('driverPhone', '---')
            h_phone = data.get('helperPhone', '---')

            # ለአድሚን መጀመሪያ 'መድረሻ (To)' ተብሎ ወጥ በሆነ ፎርማት ይላካል
            admin_msg = (
                "⚠️ <b>አዲስ ጥያቄ መጥቷል! [መኪና]</b>\n\n"
                "🚨 <b>[አስቸኳይ ጭነት እፈልጋለሁ (መኪና አለኝ)]</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f" ○   <b>የመኪና አይነት:-</b> {v_type}\n"
                f" ○   <b>ታርጋ:-</b> <code>{plate}</code>\n"
                f" ○   <b>የአሁኑ መገኛ:-</b> {curr_city}\n"
                f" ○   <b>መድረሻ (To):-</b> {target_city}\n"
                f" ○   <b>ሹፌር:-</b> {driver}\n"
                f" ○   <b>ስልክ:-</b> <code>{d_phone}</code>\n"
                f" ○   <b>ረዳት ስልክ:-</b> <code>{h_phone}</code>\n"
                "━━━━━━━━━━━━━━━━━━━━"
            )

        markup = {
            "inline_keyboard": [[
                {"text": "✅ Approve", "callback_data": f"approve_{form_type}"},
                {"text": "❌ Reject", "callback_data": "reject_post"}
            ]]
        }
        send_to_telegram(ADMIN_ID, admin_msg, markup)
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
                        raw_text = cb["message"]["text"]
                        cb_data = cb["data"]
                        
                        if "approve_" in cb_data:
                            post_id = get_next_post_id()
                            lines = raw_text.split('\n')
                            
                            cargo = "---"
                            dep = "---"
                            to = "---"
                            amount = "---"
                            price = "---"
                            v_type = "---"
                            curr = "---"

                            # ከአድሚን መልዕክት ላይ መረጃዎችን የመለያያ ዘዴ (በጣም ጠንካራ ሎጅክ)
                            for l in lines:
                                val = l.split(':-')[-1].strip() if ':-' in l else (l.split(':')[-1].strip() if ':' in l else "---")
                                if "የጭነት አይነት" in l: cargo = val
                                if "መነሻ" in l: dep = val
                                if "መድረሻ" in l: to = val  # 'መድረሻ (To)' ወይም 'መድረሻ ከተማ' የሚሉትን ሁሉ ይይዛል
                                if "መጠን" in l: amount = val
                                if "የተመደብ ዋጋ" in l or "ዋጋ" in l: price = val
                                if "የመኪና አይነት" in l: v_type = val
                                if "የአሁኑ መገኛ" in l: curr = val

                            if "load" in cb_data:
                                final_post = (
                                    f"📦 <b>[የሚጫን ጭነት አለኝ] - ID: <code>{post_id}</code></b>\n"
                                    "━━━━━━━━━━━━━━━━━━━━\n"
                                    "🟢 <b>አዲስ የጭነት ጥያቄ መጥቷል!</b>\n\n"
                                    f" ○   <b>የጭነት አይነት:-</b> <code>{cargo}</code>\n"
                                    f" ○   <b>መነሻ (From):-</b> {dep}\n"
                                    f" ○   <b>መድረሻ (To):-</b> {to}\n"
                                    f" ○   <b>መጠን:-</b> {amount}\n"
                                    f" ○   <b>የተመደበ ዋጋ:-</b> {price}\n"
                                    "━━━━━━━━━━━━━━━━━━━━"
                                )
                            else:
                                final_post = (
                                    f"🚨 <b>[አስቸኳይ ጭነት እፈልጋለሁ] - ID: <code>{post_id}</code></b>\n"
                                    "━━━━━━━━━━━━━━━━━━━━\n"
                                    "🔴 <b>ነፃ መኪና አለ! (የጭነት ጥያቄ)</b>\n\n"
                                    f" ○   <b>የመኪና አይነት:-</b> {v_type}\n"
                                    f" ○   <b>የአሁኑ መገኛ:-</b> {curr}\n"
                                    f" ○   <b>መድረሻ (To):-</b> {to}\n"  # መድረሻ ከተማ እዚህ ጋር በትክክል ይወጣል
                                    " ○   <b>የመጫኛ ዝግጁነት:-</b> ወዲያውኑ\n"
                                    "━━━━━━━━━━━━━━━━━━━━"
                                )
                            
                            final_post += f"\n\n✨ <b>ያሉበት ቦታ ሆነው ጭነት ወይም መኪና ለማግኘት ሊንኩን ይጫኑ</b> 👇\n🔗 {BOT_LINK}"
                            final_post += f"\n\n📩 <b>መረጃውን ለማግኘት ኤጀንቱን ያነጋግሩ</b> 👇"
                            
                            agent_url = f"https://t.me/{AGENT_USERNAME}?text=ሰላም%20የመለያ%20ቁጥር%20{post_id}%20ጭነት%20መረጃ%20እፈልጋለሁ"
                            
                            post_markup = {
                                "inline_keyboard": [
                                    [{"text": f"👤 ኤጀንቱን አግኝ (ID: {post_id})", "url": agent_url}],
                                    [{"text": "📢 Join Channel", "url": CHANNEL_LINK},
                                     {"text": "👥 Join Group", "url": GROUP_LINK}]
                                ]
                            }
                            
                            send_to_telegram(CHANNEL_ID, final_post, post_markup)
                            send_to_telegram(GROUP_ID, final_post, post_markup)
                            
                            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText", 
                                          json={
                                              "chat_id": ADMIN_ID, 
                                              "message_id": cb["message"]["message_id"], 
                                              "text": f"✅ <b>ተለጥፏል (ID: {post_id})</b>\n\n{raw_text}",
                                              "parse_mode": "HTML"
                                          })
                        
                        elif cb_data == "reject_post":
                            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText", 
                                          json={
                                              "chat_id": ADMIN_ID, 
                                              "message_id": cb["message"]["message_id"], 
                                              "text": f"❌ <b>ውድቅ ተደርጓል</b>\n\n{raw_text}",
                                              "parse_mode": "HTML"
                                          })
        except Exception as e:
            pass

threading.Thread(target=bot_polling, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
