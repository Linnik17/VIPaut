import asyncio
import re
import time
import numpy as np

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🔑 TOKEN
TOKEN = "8910895596:AAG5KfMwTUGvTmFYUGhQhf52b0tQb3NENug"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 💾 MEMORY
history = []
timestamps = []
MEMORY_LIMIT = 1200

# 🌍 DEFAULT LANGUAGE
user_lang = {}

# ─────────────────────────────
# 🌍 TEXT SYSTEM
# ─────────────────────────────
TEXTS = {
    "start": {
        "ru": "💎 ТРЕЙДИНГ AI ТЕРМИНАЛ\n━━━━━━━━━━\n🧠 AI: АКТИВЕН\n📊 СИГНАЛЫ: ГОТОВЫ\n📥 Отправь коэффициенты",
        "en": "💎 TRADING AI TERMINAL\n━━━━━━━━━━\n🧠 AI: ACTIVE\n📊 SIGNALS: READY\n📥 Send coefficients"
    },
    "loading": {
        "ru": "⚡ ИНИЦИАЛИЗАЦИЯ...",
        "en": "⚡ INITIALIZING..."
    },
    "no_data": {
        "ru": "📥 Нужно минимум 5 значений",
        "en": "📥 Minimum 5 values required"
    },
    "invalid": {
        "ru": "⚠️ Введи числа",
        "en": "⚠️ Send numbers"
    }
}

# 💎 MENU
menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⚡ SIGNAL", callback_data="sig")],
        [InlineKeyboardButton(text="📊 DASHBOARD", callback_data="stats")],
        [InlineKeyboardButton(text="💎 SYSTEM", callback_data="status")],
        [
            InlineKeyboardButton(text="🇷🇺 RU", callback_data="ru"),
            InlineKeyboardButton(text="🇬🇧 EN", callback_data="en")
        ]
    ]
)

# 🧹 CLEAN MEMORY
def clean():
    now = time.time()
    while timestamps and now - timestamps[0] > MEMORY_LIMIT:
        timestamps.pop(0)
        history.pop(0)

# 📥 PARSE
def parse(text):
    return [float(x) for x in re.findall(r"\d+\.?\d*", text)]

# 🌍 GET LANG
def lang(user_id):
    return user_lang.get(user_id, "ru")

# 🧠 AI ENGINE (NO RANDOM)
def analyze():
    clean()

    if len(history) < 5:
        return "📥 Need more data"

    data = history[-30:]

    avg = np.mean(data)
    std = np.std(data)

    bullish = sum(1 for x in data if x > avg)
    bearish = sum(1 for x in data if x < avg)

    low = 0
    for x in reversed(data):
        if x < 1.5:
            low += 1
        else:
            break

    high = 0
    for x in reversed(data):
        if x > 3:
            high += 1
        else:
            break

    score = 50
    score += low * 8
    score -= high * 10
    score += (bullish - bearish) * 2

    if avg < 2:
        score += 10

    if std < 1:
        score += 10
    elif std > 2:
        score -= 20

    score = max(1, min(99, int(score)))
    risk = 100 - score

    if score >= 80:
        level = "💎 ELITE SIGNAL"
        zone = "x3 – x5"
        reason = "strong accumulation + bullish pressure"
    elif score >= 60:
        level = "⚡ PRO SIGNAL"
        zone = "x2 – x3"
        reason = "trend forming"
    elif score >= 45:
        level = "⚠️ WARNING"
        zone = "x1.3 – x2"
        reason = "uncertain structure"
    else:
        level = "🚫 NO TRADE"
        zone = "—"
        reason = "market chaos"

    return f"""
{level}
━━━━━━━━━━

📊 AVG: {round(avg,2)}
📉 VOL: {round(std,2)}
🔥 BULL: {bullish}
❄ BEAR: {bearish}

🎯 SCORE: {score}%
⚠ RISK: {risk}%

━━━━━━━━━━
⚡ ZONE: {zone}

🧠 AI:
{reason}
""".strip()

# 🎬 LOADING
async def loading(msg, l):
    steps = {
        "ru": ["⚡ Запуск...", "🧠 Анализ...", "📊 Расчёт..."],
        "en": ["⚡ Starting...", "🧠 Analyzing...", "📊 Calculating..."]
    }

    m = await msg.answer(TEXTS["loading"][l])

    for s in steps[l]:
        await asyncio.sleep(0.6)
        await m.edit_text(s)

    return m

# 🚀 START
@dp.message()
async def handler(message: types.Message):

    uid = message.from_user.id
    l = lang(uid)

    if message.text == "/start":
        await message.answer(TEXTS["start"][l], reply_markup=menu)
        return

    nums = parse(message.text)

    if nums:
        for n in nums:
            history.append(n)
            timestamps.append(time.time())

        await loading(message, l)

        await message.answer(analyze(), reply_markup=menu)

    else:
        await message.answer(TEXTS["invalid"][l])

# 🎛 CALLBACKS
@dp.callback_query()
async def cb(call: types.CallbackQuery):

    uid = call.from_user.id
    l = lang(uid)

    if call.data in ["ru", "en"]:
        user_lang[uid] = call.data
        await call.message.answer("🌍 OK")
        return

    if call.data == "sig":
        await call.message.answer(analyze())

    elif call.data == "stats":
        await call.message.answer(
            f"📊 DATA: {len(history)}\n"
            f"📈 LAST: {history[-1] if history else 'NONE'}"
        )

    elif call.data == "status":
        await call.message.answer(
            "🟢 ONLINE\n⚡ AI ACTIVE\n💎 SYSTEM OK"
        )

    await call.answer()

# 🚀 RUN
async def main():
    print("💎 GLOBAL TRADING AI STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
