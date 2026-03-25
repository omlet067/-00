import os, asyncio, random, json, time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
ADMIN_ID = 7560933378 

TOKEN = "BOT_TOKEN"
DB_FILE = "economy_visual.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- СТИЛЬНЫЙ МАГАЗИН И ПРЕДМЕТЫ ---
# Эмодзи обязательны для визуала
ITEMS = {
    "⚡ энергетик": [150, 0, "Разовый флекс (в разработке)"],
    "👟 подкрадули": [1500, 0, "Лютый стиль +10 к уважению"],
    "⛺ палатка": [5000, 250, "Бизнес 'в лесу' | Доход: 250 GC/час"],
    "📦 пункт_wb": [15000, 900, "Пункт выдачи заказов | Доход: 900 GC/час"],
    "🏢 майнинг_отель": [100000, 7000, "Ферма в подвале | Доход: 7000 GC/час"]
}

users = {}

# --- СИСТЕМА ДАННЫХ ---
def save_db():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def load_db():
    global users
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
        except: users = {}

def get_u(user: types.User):
    uid = str(user.id)
    if uid not in users:
        users[uid] = {
            "name": user.first_name,
            "coins": 1000,
            "inventory": [],
            "last_work": 0
        }
    return users[uid]

# --- ВИЗУАЛЬНЫЕ КОМАНДЫ ---

@dp.message(Command("профиль", "баланс", prefix="+"))
async def profile_visual(message: types.Message):
    u = get_u(message.from_user)
    
    # Визуальное оформление инвентаря
    if u["inventory"]:
        # Оставляем только эмодзи для компактности
        inv_icons = " ".join([i.split()[0] for i in u["inventory"] if len(i.split()) > 0])
    else:
        inv_icons = "▫️ Пусто"

    # Разделитель и статус авторитета
    status = "👑 Олигарх" if u["coins"] > 50000 else "☹️ Бомж"
    line = "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"

    text = (f"👤 **{u['name']}**\n"
            f"┣ {status}\n"
            f"┣ {line}\n"
            f"┣ 💰 ` {u['coins']} GC `\n"
            f"┣ {line}\n"
            f"┣ 🎒 **ИНВЕНТАРЬ**\n"
            f"┗ {inv_icons}")
    await message.reply(text, parse_mode="Markdown")

@dp.message(Command("магазин", "маркет", prefix="."))
async def shop_visual(message: types.Message):
    # Заголовок
    text = "🛒 <b>ГЛИТЧ-МАРКЕТ</b>\n"
    text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"
    
    for item, info in ITEMS.items():
        # Форматируем цену (делаем пробелы в числах для красоты)
        price = f"{info[0]:,} GC".replace(",", " ")
        # Доход
        income = f"+{info[1]} GC/час" if info[1] > 0 else "▫️ Без дохода"
        
        # Название товара (убираем эмодзи для команды покупки)
        cmd_name = item.split()[-1]
        
        # Собираем блок товара
        text += (f"🔹 <b>{item.upper()}</b>\n"
                 f"┣ Цена: <code>{price}</code>\n"
                 f"┣ <code>{income}</code>\n"
                 f"┣ {info[2]}\n"
                 f"┗ <code>.купить {cmd_name}</code>\n\n")
    
    text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"
    
    # ОТПРАВЛЯЕМ ЧЕРЕЗ HTML (это важно!)
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("купить", prefix="."))
async def buy_cmd(message: types.Message):
    u = get_u(message.from_user)
    args = message.text.split()
    
    if len(args) < 2: 
        return await message.reply("❌ Напиши, что хочешь купить!\nПример: <code>.купить wb</code>", parse_mode="HTML")
    
    # Слово, которое ввёл юзер (например, "wb" или "палатка")
    target = args[1].lower()
    
    # Ищем подходящий предмет в магазине
    item_key = None
    for name in ITEMS:
        # Проверяем, есть ли введённое слово внутри названия из ITEMS
        if target in name.lower():
            item_key = name
            break
            
    if not item_key: 
        return await message.reply("❓ Такого товара нет в магазине. Проверь <code>.маркет</code>", parse_mode="HTML")
    
    price = ITEMS[item_key][0]
    
    if u["coins"] < price: 
        return await message.reply(f"❌ Недостаточно GC! Нужно: <code>{price}</code>", parse_mode="HTML")
    
    # Списываем деньги и добавляем в инвентарь
    u["coins"] -= price
    u["inventory"].append(item_key)
    save_db()
    
    await message.reply(f"✅ Успешно куплено: <b>{item_key}</b>\nТвой баланс: <code>{u['coins']} GC</code>", parse_mode="HTML")

@dp.message(Command("инфо", "помощь", "help", prefix=".+"))
async def info_cmd(message: types.Message):
    text = (
        "📖 <b>СПРАВКА GLITCH TYCOON</b>\n"
        "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"
        "💰 <b>ЭКОНОМИКА:</b>\n"
        "• <code>.профиль</code> — твой баланс и шмотки\n"
        "• <code>.работа</code> — заработать коины (раз в 30 мин)\n"
        "• <code>.передать [сумма]</code> — перевод (через реплай)\n\n"
        
        "🛒 <b>БИЗНЕС:</b>\n"
        "• <code>.маркет</code> — магазин предприятий\n"
        "• <code>.купить [название]</code> — покупка бизнеса\n"
        "<i>(Бизнесы приносят доход каждый час!)</i>\n\n"
        
        "🎰 <b>АЗАРТ:</b>\n"
        "• <code>.казино [ставка]</code> — слоты (шанс x15)\n"
        "• <code>.топ</code> — список богачей чата\n\n"
        
        "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        "🤖 <i>Версия: 1.2.0 Visual Edition</i>"
    )
    
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("работа", prefix="+"))
async def work_visual(message: types.Message):
    u = get_u(message.from_user)
    now = time.time()
    
    if now - u["last_work"] < 1800: # КД 30 минут
        rem = int((1800 - (now - u["last_work"])) / 60)
        return await message.reply(f"⏳ **ЖДИ!** Работать можно раз в 30 минут. Осталось {rem} мин.")
    
    salary = random.randint(200, 600)
    u["coins"] += salary
    u["last_work"] = now
    save_db()
    
    jobs = [
        ["📦 разгрузил WB-заказы", "+400 GC"],
        ["🛠 настроил роутер соседке", "+250 GC"],
        ["💾 продал конфиг в Майне", "+600 GC"],
        ["🪙вложился в крипту", "+300 GC"],
        ["💦поработал(а) на трассе", "+5 GC"]
    ]
    job = random.choice(jobs)
    await message.reply(f"⚒ Ты **{job[0]}** и получил ` {salary} GC `!")

@dp.message(Command("казино", "слоты", prefix="."))
async def casino_pro_visual(message: types.Message):
    u = get_u(message.from_user)
    args = message.text.split()
    
    if len(args) < 2 or not args[1].isdigit():
        return await message.reply("⚠️ Формат: `.казино [ставка]`")
    
    bet = int(args[1])
    if bet > u["coins"] or bet <= 0:
        return await message.reply("🚫 Недостаточно GC или неверная ставка!")

    # КРАСИВЫЕ КРУТЯЩИЕСЯ БАРАБАНЫ
    msg = await message.answer("🎰 **КРУТИМ СЛОТЫ...**")
    symbols = ["💎", "🎰", "🍋", "🍒", "💩"]
    
    # Анимация кручения
    spin_frames = [
        f"🎰 | 💎 | 🍋 | 🍒 |",
        f"🎰 | 🍋 | 💎 | 🎰 |",
        f"🎰 | 🎰 | 🍒 | 💎 |"
    ]
    
    for _ in range(3):
        await msg.edit_text(random.choice(spin_frames))
        await asyncio.sleep(0.4)

    # Финальный результат
    res = [random.choice(symbols) for _ in range(3)]
    line = " | ".join(res)
    
    if res[0] == res[1] == res[2]: # Джекпот
        u["coins"] += bet * 15
        result = f"🔥 **ДЖЕКПОТ!** Выигрыш: `+{bet * 15}` GC"
    elif res[0] == res[1] or res[1] == res[2] or res[0] == res[2]: # Пара
        u["coins"] += bet * 2
        result = f"✅ **ПОБЕДА!** Выигрыш: `+{bet * 2}` GC"
    else: # Проигрыш
        u["coins"] -= bet
        result = f"❌ **ПРОИГРЫШ!** Потеряно: `-{bet}` GC"
        
    save_db()
    
    final_text = (f"🎰 **КАЗИНО ГЛИТЧА**\n"
                  f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                  f"| {line} |\n"
                  f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"
                  f"{result}")
    await msg.edit_text(final_text, parse_mode="Markdown")

@dp.message(Command("топ", prefix="+"))
async def top_players(message: types.Message):
    # 1. Загружаем свежие данные из базы
    load_db()
    
    # 2. Сортируем словарик пользователей по значению "coins" (от большего к меньшему)
    # Берем только первые 5 человек
    sorted_users = sorted(users.items(), key=lambda x: x[1].get("coins", 0), reverse=True)[:5]
    
    if not sorted_users:
        return await message.reply("📈 В списке пока пусто!")

    # 3. Формируем красивый список
    text = "👑 <b>ТОП МАЖОРОВ ЧАТА</b>\n"
    text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"
    
    for i, (uid, data) in enumerate(sorted_users, 1):
        name = data.get("name", "Аноним")
        coins = data.get("coins", 0)
        
        # Выделяем первое место короной
        icon = "🥇" if i == 1 else f"{i}."
        text += f"{icon} <b>{name}</b> — <code>{coins:,} GC</code>\n".replace(",", " ")

    text += "\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"
    
    await message.answer(text, parse_mode="HTML")

# --- СТИЛЬНЫЙ ПЕРЕВОД (ПО РЕПЛАЮ) ---
@dp.message(Command("передать", "дать", prefix="."))
async def transfer_coins_visual(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("⚠️ Ответь на сообщение получателя!")

    # Регистрация
    sender = get_u(message.from_user)
    receiver = get_u(message.reply_to_message.from_user)

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        return await message.reply("⚠️ Формат: `.передать 500`")

    amount = int(args[1])

    if amount <= 0 or message.from_user.id == message.reply_to_message.from_user.id:
        return await message.reply("🚫 Неверная сумма или получатель.")

    if sender["coins"] < amount:
        return await message.reply(f"❌ Недостаточно средств! Баланс: `{sender['coins']} GC`", parse_mode="Markdown")

    # Перевод
    sender["coins"] -= amount
    receiver["coins"] += amount
    save_db()

    # Красивая анимация передачи
    msg = await message.answer(f"💸 **ПЕРЕВОД...**\n`[{message.from_user.first_name}]` ➟ `[{message.reply_to_message.from_user.first_name}]`")
    await asyncio.sleep(0.5)
    
    transfer_frames = ["💰     ", "  💰   ", "   💰  ", "   💰", "     💰"]
    for f in transfer_frames:
        await msg.edit_text(f"💸 **ПЕРЕВОД...**\n`{amount} GC`\n`[{message.from_user.first_name}]` {f} `[{message.reply_to_message.from_user.first_name}]`")
        await asyncio.sleep(0.1)

    # Итоговый текст
    final_text = (f"✅ **ПЕРЕВОД ВЫПОЛНЕН**\n"
                  f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                  f"💸 Отправитель: `{message.from_user.first_name}`\n"
                  f"💸 Получатель: `{message.reply_to_message.from_user.first_name}`\n"
                  f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                  f"💰 Сумма: ` {amount} GC `")
    await msg.edit_text(final_text, parse_mode="Markdown")

    ADMIN_ID = 7560933378  # ВСТАВЬ СЮДА СВОЙ ID (БЕЗ КАВЫЧЕК)

@dp.message(Command("зачислить", prefix="."))
async def set_balance(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("❌ Ты не админ.")

    args = message.text.split()
    if len(args) < 2: return await message.reply("Пример: `.зачислить 999999` (реплаем на юзера)")

    amount = int(args[1])
    # Если ответил на сообщение — выдаст тому челу, если нет — тебе
    target_user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    
    u = get_u(target_user)
    u["coins"] = amount
    save_db()
    await message.reply(f"👑 Баланс `{target_user.first_name}` изменен на `{amount} GC`")

@dp.message(Command("ворк", prefix="."))
async def work_visual(message: types.Message):
    u = get_u(message.from_user)

    # Весь этот блок должен быть ВНУТРИ функции (с отступом в 4 пробела или 1 Tab)
    if message.from_user.id != ADMIN_ID:
        if time.time() - u.get("last_work", 0) < 1800:
            rem = int((1800 - (time.time() - u["last_work"])) / 60)
            return await message.reply(f"⏳ Жди {rem} мин.")

    salary = random.randint(200, 600)
    u["coins"] += salary
    u["last_work"] = time.time()
    save_db()
    await message.reply(f"⚒ Ты поработал и получил ` {salary} GC `!")
# --- ФОНОВЫЙ ДОХОД (РАЗ В ЧАС) ---
async def passive_income():
    while True:
        await asyncio.sleep(3600)
        for uid in users:
            for item in users[uid]["inventory"]:
                if item in ITEMS:
                    users[uid]["coins"] += ITEMS[item][1]
        save_db()
        print("💸 Доход начислен!")

# Команда КУПИТЬ не меняется, она просто добавляет предмет в инвентарь

async def main():
    load_db()
    asyncio.create_task(passive_income())
    print("--- Glitch Visual Tycoon Ready ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
