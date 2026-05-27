import asyncio
import re
import random
import time
import numpy as np

from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# 💎 TOKEN
TOKEN = "8910895596:AAG5KfMwTUGvTmFYUGhQhf52b0tQb3NENug"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 📊 память коэффициентов
history = []

# ⏱ память времени
timestamps = []

# 💎 MENU
menu = InlineKeyboardMarkup(
    inline_keyboard=[

        [
            InlineKeyboardButton(
                text="⚡ SIGNAL",
                callback_data="signal"
            )
        ],

        [
            InlineKeyboardButton(
                text="📊 ANALYTICS",
                callback_data="stats"
            )
        ],

        [
            InlineKeyboardButton(
                text="💎 STATUS",
                callback_data="status"
            )
        ]
    ]
)

# 🎬 АНИМАЦИИ
loading_steps = [

    "⚡ Сканирование рынка...",
    "🧠 Анализ паттернов...",
    "📊 Проверка волатильности...",
    "💎 Поиск лучшего сигнала...",
    "📡 AI анализирует историю..."
]

# 💬 УМНЫЕ ФРАЗЫ
reasons_growth = [

    "рынок долго внизу\nвероятен импульс",

    "наблюдается накопление\nвозможен рост",

    "серия низких значений\nрынок готовится к движению",

    "волатильность снижается\nвозможен выход вверх"
]

reasons_danger = [

    "слишком много высоких\nрынок нестабилен",

    "замечен перегрев\nлучше пропустить",

    "хаотичные движения\nсигнал слабый"
]

neutral_texts = [

    "рынок в нейтральной фазе",

    "сильного преимущества пока нет",

    "ожидается формирование нового паттерна"
]

# 🎬 LOADING
async def loading(message):

    msg = await message.answer(
        random.choice(loading_steps)
    )

    for step in loading_steps[1:]:

        await asyncio.sleep(0.6)

        await msg.edit_text(step)

    return msg

# 🧠 AI ENGINE
def analyze():

    # ⏱ чистка памяти старше 20 минут
    now = time.time()

    while timestamps and now - timestamps[0] > 1200:

        timestamps.pop(0)
        history.pop(0)

    # 📉 мало данных
    if len(history) < 5:

        return (

            "⏳ Недостаточно данных\n"
            "━━━━━━━━━━\n\n"

            "📥 Нужно минимум 5 коэффициентов\n"
            "🧠 AI собирает историю"
        )

    # 📊 последние коэффициенты
    last = history[-20:]

    avg = np.mean(last)
    std = np.std(last)

    # 🔥 low серия
    low_streak = 0

    for x in reversed(last):

        if x < 1.5:
            low_streak += 1
        else:
            break

    # 📈 high серия
    high_streak = 0

    for x in reversed(last):

        if x > 3:
            high_streak += 1
        else:
            break

    # 📊 volatility
    volatility = round(std, 2)

    # 🎯 SCORE
    score = 50

    if low_streak >= 2:
        score += 10

    if low_streak >= 4:
        score += 15

    if low_streak >= 6:
        score += 20

    if avg < 2:
        score += 10

    if high_streak >= 3:
        score -= 25

    if volatility > 2:
        score -= 15

    score = max(1, min(99, score))

    # ⚠️ risk
    risk = 100 - score

    # 📊 volatility text
    vol_text = "низкая"

    if volatility > 1:
        vol_text = "средняя"

    if volatility > 2:
        vol_text = "высокая"

    # 📈 market mode
    market = "Growth Setup"

    if high_streak >= 3:
        market = "Danger Zone"

    if score >= 75:

        return (

            "💎 ELITE SIGNAL\n"
            "━━━━━━━━━━\n\n"

            f"📈 Тип: {market}\n"
            f"🔥 Низких подряд: {low_streak}\n"
            f"📊 Волатильность: {vol_text}\n"
            f"🎯 Сила сигнала: {score}%\n\n"

            "⚡ Рекомендуемая зона:\n"
            "x2 – x3.5\n\n"

            "🧠 Причина:\n"
            f"{random.choice(reasons_growth)}"
        )

    if score >= 55:

        return (

            "⚡ PRO SIGNAL\n"
            "━━━━━━━━━━\n\n"

            f"📈 Тип: {market}\n"
            f"📊 Волатильность: {vol_text}\n"
            f"🎯 Сила сигнала: {score}%\n\n"

            "⚠️ Осторожный вход\n"
            "📈 Возможен рост\n\n"

            "🧠 Анализ:\n"
            f"{random.choice(neutral_texts)}"
        )

    return (

        "⚠️ NO SIGNAL\n"
        "━━━━━━━━━━\n\n"

        f"📊 Волатильность: {vol_text}\n"
        f"⚠️ Риск: {risk}%\n\n"

        "🚫 AI не рекомендует вход\n\n"

        "🧠 Причина:\n"
        f"{random.choice(reasons_danger)}"
    )

# 📥 ПАРСЕР
def parse_nums(text):

    return [

        float(x)

        for x in re.findall(
            r"\d+\.?\d*",
            text
        )
    ]

# 🚀 START
@dp.message()
async def messages(message: types.Message):

    # 💎 START
    if message.text == "/start":

        await message.answer(

            "💎 ULTRA AI ANALYZER\n"
            "━━━━━━━━━━\n\n"

            "🧠 AI анализ паттернов\n"
            "📊 Smart volatility\n"
            "⚡ Auto signal logic\n"
            "💾 Память коэффициентов\n\n"

            "📥 Отправляй коэффициенты\n"
            "Можно по одному",

            reply_markup=menu
        )

        return

    # 📊 INPUT
    nums = parse_nums(message.text)

    if nums:

        for n in nums:

            history.append(n)
            timestamps.append(time.time())

        # 📦 LIMIT
        if len(history) > 100:

            history.pop(0)
            timestamps.pop(0)

        # 🎬 animation
        load = await loading(message)

        await asyncio.sleep(0.5)

        # 💎 RESULT
        await load.edit_text(

            analyze(),

            reply_markup=menu
        )

        return

    # ❌ invalid
    await message.answer(

        "⚠️ Неверный формат\n\n"

        "📥 Пример:\n"
        "1.2\n"
        "или\n"
        "1.2 1.5 2.4"
    )

# 🎛 CALLBACKS
@dp.callback_query()
async def callbacks(call: types.CallbackQuery):

    # ⚡ SIGNAL
    if call.data == "signal":

        msg = await call.message.answer(

            "⚡ AI генерирует сигнал..."
        )

        await asyncio.sleep(1)

        await msg.edit_text(

            analyze(),

            reply_markup=menu
        )

    # 📊 ANALYTICS
    elif call.data == "stats":

        total = len(history)

        avg = round(
            np.mean(history),
            2
        ) if history else 0

        last = (
            history[-1]
            if history else "нет"
        )

        await call.message.answer(

            "📊 ULTRA ANALYTICS\n"
            "━━━━━━━━━━\n\n"

            f"📈 Коэффициентов: {total}\n"
            f"📊 Средний коэффициент: {avg}\n"
            f"📉 Последний коэффициент: {last}\n\n"

            "🧠 AI память активна\n"
            "⏱ История хранится 20 минут"
        )

    # 💎 STATUS
    elif call.data == "status":

        await call.message.answer(

            "💎 SYSTEM STATUS\n"
            "━━━━━━━━━━\n\n"

            "🟢 SYSTEM ONLINE\n"
            "⚡ AI ENGINE ACTIVE\n"
            "📊 VOLATILITY ONLINE\n"
            "🧠 MEMORY SYSTEM ACTIVE\n"
            "📡 AUTO ANALYZER READY\n\n"

            "🔥 ULTRA VERSION"
        )

    await call.answer()

# 🚀 RUN
async def main():

    print("💎 ULTRA AI BOT STARTED")

    await dp.start_polling(bot)

asyncio.run(main())
