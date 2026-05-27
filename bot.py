import asyncio
import re
import time
import numpy as np
import matplotlib.pyplot as plt

from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile

TOKEN = "8910895596:AAG5KfMwTUGvTmFYUGhQhf52b0tQb3NENug"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ─────────────────────────────
# 💾 SYSTEM STORAGE
# ─────────────────────────────
users = {}
history = []
timestamps = []
MEMORY_LIMIT = 1200

ADMINS = [123456789]

# ─────────────────────────────
# 🌍 LANGUAGE
# ─────────────────────────────
def lang(uid):
    return users.get(uid, {}).get("lang", "ru")

# ─────────────────────────────
# 👑 STATUS SYSTEM
# ─────────────────────────────
def status(uid):
    u = users.get(uid, {})
    if u.get("vip_until", 0) > time.time():
        return "VIP"
    return "FREE"

# ─────────────────────────────
# 🧹 MEMORY CLEANER
# ─────────────────────────────
def clean():
    now = time.time()
    while timestamps and now - timestamps[0] > MEMORY_LIMIT:
        timestamps.pop(0)
        history.pop(0)

# ─────────────────────────────
# 📥 PARSER
# ─────────────────────────────
def parse(text):
    return [float(x) for x in re.findall(r"\d+\.?\d*", text)]

# ─────────────────────────────
# 🧠 AI ENGINE (FINAL)
# ─────────────────────────────
def analyze():
    clean()

    data = history[-40:]

    if len(data) < 5:
        return "📥 NOT ENOUGH DATA"

    avg = np.mean(data)
    std = np.std(data)

    bull = sum(1 for x in data if x > avg)
    bear = sum(1 for x in data if x < avg)

    momentum = bull - bear

    score = 50
    score += momentum * 3
    score += np.sum(np.array(data) < 1.5) * 7
    score -= np.sum(np.array(data) > 3) * 9

    if std < 1:
        score += 10
    elif std > 2:
        score -= 20

    score = max(1, min(99, int(score)))
    risk = 100 - score

    if score >= 85:
        level = "💎 ELITE SIGNAL"
        zone = "x3 – x6"
        reason = "strong trend + low volatility"
    elif score >= 65:
        level = "⚡ PRO SIGNAL"
        zone = "x2 – x3"
        reason = "stable structure"
    else:
        level = "🚫 NO TRADE"
        zone = "—"
        reason = "market noise"

    return f"""
{level}
━━━━━━━━━━
📊 AVG: {round(avg,2)}
📉 VOL: {round(std,2)}
🔥 MOMENTUM: {momentum}

🎯 SCORE: {score}%
⚠ RISK: {risk}%

⚡ ZONE: {zone}

🧠 AI:
{reason}
""".strip()

# ─────────────────────────────
# 📊 GRAPH ENGINE
# ─────────────────────────────
def make_graph():
    data = history[-25:]

    plt.figure()
    plt.plot(data, marker="o")
    plt.title("SAAS AI MARKET GRAPH")
    plt.grid()

    path = "/tmp/graph.png"
    plt.savefig(path)
    plt.close()

    return path

# ─────────────────────────────
# 💎 WELCOME MESSAGE
# ─────────────────────────────
def welcome(uid):
    return f"""
💎 SAAS AI EXCHANGE TERMINAL
━━━━━━━━━━━━━━━━━━

👤 STATUS: {status(uid)}
🌍 LANG: {lang(uid).upper()}

🧠 AI CORE: ONLINE
📊 MARKET ENGINE: ACTIVE
📡 SIGNAL SYSTEM: READY

━━━━━━━━━━━━━━━━━━
📥 Send coefficients
📊 /graph - chart
💎 VIP unlock coming soon
""".strip()

# ─────────────────────────────
# 🚀 START
# ─────────────────────────────
@dp.message()
async def handler(m: types.Message):

    uid = m.from_user.id

    if uid not in users:
        users[uid] = {"lang": "ru"}

    if m.text == "/start":
        await m.answer(welcome(uid))
        return

    if m.text == "/graph":
        path = make_graph()
        await m.answer_photo(FSInputFile(path))
        return

    nums = parse(m.text)

    if nums:
        for n in nums:
            history.append(n)
            timestamps.append(time.time())

        await m.answer(analyze())
    else:
        await m.answer("⚠️ send numbers")

# ─────────────────────────────
# 🚀 RUN BOT
# ─────────────────────────────
async def main():
    print("💎 FINAL SAAS 10000 STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
