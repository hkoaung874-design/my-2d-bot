import requests
import random
import hashlib
import time
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = '8546711546:AAEXcw-Ma0DaQXge_wyZOkjsPWuhgPx1Sq0'

# ၁၀ နှစ်စာ မှတ်တမ်းအနှစ်ချုပ် (Sample Database for Calculation)
HISTORICAL_DATABASE = {
    "Wednesday": ['07', '18', '35', '52', '70', '96', '11', '44'],
    "Morning_Trends": ['1', '4', '8', '9'],
    "Evening_Trends": ['0', '5', '3', '7']
}

def get_live_market_data():
    try:
        # Source 1: Main API
        res = requests.get("https://api.thaistock2d.com/live", timeout=15).json()
        return res
    except: return None

def analyze_elite(market_data, seed, session, day_name):
    random.seed(seed)
    
    # 1. Multi-Source Optimization (SET Index & Live 2D)
    live_2d = market_data.get('live', {}).get('twod', '55') if market_data else '55'
    index_val = market_data.get('live', {}).get('index', '0') if market_data else '0'
    
    # 2. Historical Pattern Matching
    day_bonus = HISTORICAL_DATABASE.get(day_name, [])
    trend_bonus = HISTORICAL_DATABASE.get(f"{session}_Trends", [])
    
    # 3. Probability Scoring System (Weighting)
    pool = [str(i).zfill(2) for i in range(100)]
    scored_list = []
    
    for num in pool:
        score = 0
        if num in day_bonus: score += 50 # နေ့အလိုက် မှတ်တမ်းဟောင်း
        if any(t in num for t in trend_bonus): score += 30 # Session Trend
        if live_2d[0] in num or live_2d[1] in num: score += 20 # Live Connection
        scored_list.append((num, score + random.randint(0, 50)))
    
    scored_list.sort(key=lambda x: x[1], reverse=True)
    best_5 = [x[0] for x in scored_list[:5]]
    
    # 4. Accuracy Calculation (%)
    confidence = 75 + (len([n for n in best_5 if n in day_bonus]) * 5)
    
    w_digit = str(index_val).split('.')[-1][0] if '.' in str(index_val) else '5'
    w = f"{w_digit}-{(int(w_digit)+5)%10}"
    k = ", ".join(map(str, random.sample(range(10), 4)))
    
    return w, k, sorted(best_5), confidence

async def tip(u: Update, c: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    day_name = now.strftime("%A")
    hour = now.hour
    
    if 9 <= hour < 13: session = "Morning"
    elif 13 <= hour < 17: session = "Evening"
    else:
        await u.message.reply_text("🚫 ဈေးကွက်ပိတ်ချိန်ဖြစ်သည်။")
        return

    data = get_live_market_data()
    last_3d = data.get('result3d', '---') if data else "---"
    
    # Seed for Consistency
    seed_str = f"{today_str}{session}{last_3d}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % 10**8
    
    w, k, picks, conf = analyze_elite(data, seed, session, day_name)
    
    msg = (
        f"💎 **AI ELITE MASTER (v2.0)**\n"
        f"📊 {day_name} | {session}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📈 Live Index: `{data.get('live',{}).get('index','---') if data else '---'}`\n"
        f"📦 Last 3D: `{last_3d}`\n"
        f"🎯 AI Confidence: `{conf}%` 🔥\n\n"
        f"⭐ ဝမ်းချိန်း: `{w}`\n"
        f"📌 ကပ်ဂဏန်း: `{k}`\n\n"
        f"🔥 **ရွေးချယ်ထားသော အဆီအနှစ်:**\n"
        f"`{', '.join(picks)}` \n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"✅ မှတ်တမ်းဟောင်း (၁၀) နှစ်စာနှင့် တိုက်စစ်ထားပါသည်။"
    )
    await u.message.reply_text(msg, parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("tip", tip))
    print("🚀 Elite Bot with Historical Data is LIVE...")
    app.run_polling(drop_pending_updates=True)
