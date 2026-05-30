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

# ትክክለኛ ሊንኮች
BOT_LINK = "https://t.me/chinetcombot"
CHANNEL_LINK = "https://t.me/chinetcom"
GROUP_LINK = "https://t.me/chinetcometh"

def send_to_telegram(chat_id, message, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",  # የ HTML ታጎች እንዲሰሩ
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
        
        # 1. መረጃው 'የሚጫን ጭነት አለኝ' ከሆነ (Load Form)
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

            # ለአድሚን የሚላከው (ሁሉንም ሚስጥራዊ መረጃ የያዘ)
            admin_msg = (
                "⚠️ <b>አዲስ ጥያቄ መጥቷል! [ጭነት]</b>\n\n"
                "📦 <b>[የሚጫን ጭነት አለኝ]</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🟢 <b>አዲስ የጭነት ጥያቄ መጥቷል!</b>\n\n"
                f" ○   <b>የጭነት ባለቤት:-</b> {org}\n"
                f" ○   <b>ስልክ:-</b> <code>{phone}</code>\n"
                f" ○   <b>መነሻ (From):-</b> {dep}\n"
                f" ○   <b>መድረሻ (To):-</b> {to}\n"
                f" ○   <b>የጭነት አይነት:-</b> <code>{cargo}</code>\n"
                f" ○   <b>መጠን:-</b> {amount} ኩንታል/ቶን\n"
                f" ○   <b>የሚፈለግ መኪና:-</b> {truck}\n"
                f" ○   <b>የተመደበ ዋጋ:-</b> {price} ETB\n"
                f" ○   <b>ቀን:-</b> {date}\n"
                "━━━━━━━━━━━━━━━━━━━━"
            )
        
        # 2. መረጃው 'አስቸኳይ ጭነት እፈልጋለሁ' ከሆነ (Truck Form)
        else:
            v_type = data.get('vType', '---')
            plate = data.get('plate', '---')
            curr_city = data.get('currentCity', '---')
            target_city = data.get('targetCity', '---')
            driver = data.get('driverName', '---')
            d_phone = data.get('driverPhone', '---')
            h_phone = data.get('helperPhone', '---')

            # ለአድሚን የሚላከው (ሁሉንም ሚስጥራዊ መረጃ የያዘ)
            admin_msg = (
                "⚠️ <b>አዲስ ጥያቄ መጥቷል! [መኪና]</b>\n\n"
                "🚨 <b>[አስቸኳይ ጭነት እፈልጋለሁ (መኪና አለኝ)]</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🔴 <b>ነፃ መኪና አለ! (የጭነት ጥያቄ)</b>\n\n"
                f" ○   <b>የመኪና አይነት:-</b> {v_type}\n"
                f" ○   <b>ታርጋ:-</b> <code>{plate}</code>\n"
                f" ○   <b>የአሁኑ መገኛ:-</b> {curr_city}\n"
                f" ○   <b>መድረሻ ከተማ:-</b> {target_city}\n"
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
        
        # ውሂቡን (Data) በቴሌግራም መልዕክት ውስጥ በድብቅ ለማስተላለፍ 'Text' ላይ አንጨምረውም
        # ይልቁንም አድሚኑ ጋር በተለየ ማርክአፕ ወይም መልዕክት መልክ እናስቀምጠዋለን።
        # ነገር ግን መረጃውን በቀላሉ መልሶ ለማግኘት እንዲመች አድሚን ቻት ላይ እንልካለን።
        
        # ለአድሚኑ መረጃውን ለመለየት እንዲመቸው ዋናውን ዳታ በጽሑፉ ግርጌ በድብቅ (Hidden HTML tag) እናስቀምጠዋለን
        if form_type == 'load':
            hidden_data = f"<a href='hidden://data?type=load&dep={dep}&to={to}&cargo={cargo}&amount={amount}&truck={truck}&price={price}'> </a>"
        else:
            hidden_data = f"<a href='hidden://data?type=truck&v_type={v_type}&curr={curr_city}&target={target_city}'> </a>"
            
        send_to_telegram(ADMIN_ID, admin_msg + hidden_data, markup)
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
                            # ከጽሑፉ ውስጥ የ entity ሊንኩን በመፈለግ ዳታውን በንፅህና እንመዝግባለን
                            entities = cb["message"].get("entities", [])
                            final_post = ""
                            
                            # የትኛው ፎርም እንደሆነ ከ callback_data እንለያለን
                            if "load" in cb_data:
                                # በምስል 1000054092.jpg መሰረት ንፁህ የቻናል ፖስት መገንባት (ሚስጥራዊ መረጃ የሌለው)
                                # ጽሑፉን ከቀጥታ መስመሮቹ ላይ እንፈልገዋለን
                                lines = raw_text.split('\n')
                                cargo = "---"
                                dep = "---"
                                to = "---"
                                amount = "---"
                                price = "---"
                                
                                for l in lines:
                                    if "የጭነት አይነት" in l: cargo = l.split(':-')[-1].strip()
                                    if "መነሻ" in l: dep = l.split(':-')[-1].strip()
                                    if "መድረሻ" in l: to = l.split(':-')[-1].strip()
                                    if "መጠን" in l: amount = l.split(':-')[-1].strip()
                                    if "የተመደበ ዋጋ" in l: price = l.split(':-')[-1].strip()
                                
                                final_post = (
                                    "📦 <b>[የሚጫን ጭነት አለኝ]</b>\n"
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
                                # በምስል 1000054094.jpg መሰረት ንፁህ የቻናል ፖስት መገንባት (ሚስጥራዊ መረጃ የሌለው)
                                lines = raw_text.split('\n')
                                v_type = "---"
                                curr = "---"
                                
                                for l in lines:
                                    if "የመኪና አይነት" in l: v_type = l.split(':-')[-1].strip()
                                    if "የአሁኑ መገኛ" in l: curr = l.split(':-')[-1].strip()
                                
                                final_post = (
                                    "🚨 <b>[አስቸኳይ ጭነት እፈልጋለሁ (መኪና አለኝ)]</b>\n"
                                    "━━━━━━━━━━━━━━━━━━━━\n"
                                    "🔴 <b>ነፃ መኪና አለ! (የጭነት ጥያቄ)</b>\n\n"
                                    f" ○   <b>የመኪና አይነት:-</b> {v_type}\n"
                                    f" ○   <b>የአሁኑ መገኛ:-</b> {curr}\n"
                                    " ○   <b>የመጫኛ ዝግጁነት:-</b> ወዲያውኑ\n"
                                    "━━━━━━━━━━━━━━━━━━━━"
                                )
                            
                            # በምስል 1000054096.jpg ላይ የታዩትን የግርጌ ጽሑፎች በሙሉ ማካተት
                            final_post += f"\n\n✨ <b>ያሉበት ቦታ ሆነው ጭነት ወይም መኪና ለማግኘት ሊንኩን ይጫኑ</b> 👇\n🔗 {BOT_LINK}"
                            final_post += f"\n\n📩 <b>መረጃውን ለማግኘት ኤጀንቱን ያነጋግሩ</b> 👇"
                            
                            # የሊንክ አዝራሮች (Inline Buttons)
                            post_markup = {
                                "inline_keyboard": [
                                    [{"text": "👤 ኤጀንቱን አግኝ (Contact)", "url": f"https://t.me/{AGENT_USERNAME}"}],
                                    [{"text": "📢 Join Channel", "url": CHANNEL_LINK},
                                     {"text": "👥 Join Group", "url": GROUP_LINK}]
                                ]
                            }
                            
                            # ለቻናል እና ግሩፕ መለጠፍ
                            send_to_telegram(CHANNEL_ID, final_post, post_markup)
                            send_to_telegram(GROUP_ID, final_post, post_markup)
                            
                            # የአድሚኑን መልዕክት ሁኔታ መቀየር
                            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText", 
                                          json={
                                              "chat_id": ADMIN_ID, 
                                              "message_id": cb["message"]["message_id"], 
                                              "text": f"✅ <b>ተለጥፏል</b>\n\n{raw_text}",
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
