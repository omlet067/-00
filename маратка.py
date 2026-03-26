import os, asyncio, random, json, time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import time
ADMIN_ID = 7560933378 

TOKEN = os.getenv("TYCOON_TOKEN")
DB_FILE = "economy_visual.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- СТИЛЬНЫЙ МАГАЗИН И ПРЕДМЕТЫ ---
# Эмодзи обязательны для визуала
ITEMS = {
    "⚡ энергетик": [6000, 0, "Разовый флекс (в разработке)"],
    "👟 подкрадули": [1500, 0, "Лютый стиль | Без дохода"],
    "⛺ палатка": [5000, 50, "Бизнес 'в лесу' | Доход: 50 GC/час"], # Окупаемость ~4 дня
    "📦 пункт_wb": [25000, 200, "Пункт выдачи | Доход: 200 GC/час"], # Окупаемость ~5 дней
    "🏢 майнинг_отель": [150000, 800, "Ферма в подвале | Доход: 800 GC/час"], # Окупаемость ~7 дней
    "🚀 стартап": [1000000, 5000, "Глитч-корпорация | Доход: 5 000 GC/час"], # Для миллионеров
    "👑 статус олигарха" : [9999999, 0 "Статус очень богатого человека в чате"]
}

# --- СИСТЕМА ДАННЫХ (ОПТИМИЗИРОВАННАЯ) ---
users = {}
db_is_dirty = False # Флаг: нужно ли сохранять данные?

def save_db():
    global db_is_dirty
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        db_is_dirty = False
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")

def load_db():
    global users
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
        except:
            users = {}

def get_u(user: types.User):
    global db_is_dirty
    uid = str(user.id)
    if uid not in users:
        users[uid] = {
            "name": user.first_name,
            "coins": 1000,
            "inventory": [],
            "last_work": 0,
            "last_bonus": 0
            "luck_until": 0
            "last_slots": 0
        }
        db_is_dirty = True # Нового юзера надо сохранить
    else:
        # Проверка новых полей для старых игроков
        for key in ["luck_until", "last_slots"]:
            if key not in users[uid]:
                users[uid][key] = 0
                db_is_dirty = True
    return users[uid]
    

# --- ВИЗУАЛЬНЫЕ КОМАНДЫ ---
@dp.message(Command("профиль", prefix="."))
async def profile_visual(message: types.Message):
    args = message.text.split()
    
    # Определяем, чей профиль смотрим
    if len(args) > 1 and args[1].isdigit():
        target_id = args[1] # Смотрим чужой ID
    else:
        target_id = str(message.from_user.id) # Смотрим свой

    # Проверяем, есть ли такой игрок в базе
    if target_id not in users:
        return await message.reply("❌ Игрок с таким ID не найден в базе данных.")

    u = users[target_id]
    
    # Считаем доход
    total_income = 0
    inventory = u.get("inventory", [])
    for item in inventory:
        if item in ITEMS:
            total_income += ITEMS[item][1]

    inv_text = ", ".join(inventory) if inventory else "отсутствует"
    
    # Экранируем имя от спецсимволов HTML
    name = u.get('name', 'Игрок').replace('<', '&lt;').replace('>', '&gt;')

    text = (
        f"👤 <b>ПРОФИЛЬ: {name}</b>\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"💰 Баланс: <code>{u.get('coins', 0):,} GC</code>\n"
        f"📈 Доход: <code>{total_income:,} GC/час</code>\n"
        f"🎒 Инвентарь: <i>{inv_text}</i>\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"🆔 ID: <code>{target_id}</code>"
    ).replace(",", " ")

    await message.answer(text, parse_mode="HTML")

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

@dp.message(Command("пить", prefix="."))
async def drink_energy(message: types.Message):
    u = get_u(message.from_user)
    
    if "⚡ энергетик" not in u["inventory"]:
        return await message.reply("🛒 Сначала купи его в <code>.маркет</code>!", parse_mode="HTML")
    
    u["inventory"].remove("⚡ энергетик")
    # Устанавливаем удачу на 10 минут от текущего момента
    u["luck_until"] = time.time() + 180
    
    global db_is_dirty; db_is_dirty = True
    
    await message.reply("🥤 <b>Глитч-Раш выпит!</b>\nТвои чувства обострены. Удача в казино повышена на 3 минуты! 🔥", parse_mode="HTML")

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

@dp.message(Command("удалить_аккаунт", prefix="."))
async def delete_my_profile(message: types.Message):
    global db_is_dirty
    uid = str(message.from_user.id)
    args = message.text.split()
    
    if uid not in users:
        return await message.reply("❌ У тебя и так нет профиля в базе.")

    # Проверка на подтверждение (нужно написать .удалить_аккаунт ДА)
    if len(args) < 2 or args[1].upper() != "ДА":
        return await message.reply(
            "⚠️ <b>ВНИМАНИЕ!</b>\n"
            "Это удалит твой баланс, инвентарь и все достижения навсегда.\n\n"
            "Чтобы подтвердить, напиши: <code>.удалить_аккаунт ДА</code>", 
            parse_mode="HTML"
        )
    
    # Удаляем юзера из словаря
    del users[uid]
    db_is_dirty = True # Помечаем, что надо сохранить файл
    
    await message.answer("🗑 <b>Твой профиль был полностью удален.</b>\nДо встречи!", parse_mode="HTML")

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
        ["🍔поел бургеры", "+200 GC"]
        ["💸батя дал на додеп", "+300 GC"]
    job = random.choice(jobs)
    await message.reply(f"⚒ Ты **{job[0]}** и получил ` {salary} GC `!")

max_bet = 50000 # Поставь предел, выше которого нельзя ставить
    if bet > max_bet:
        return await message.reply(f"⚠️ Максимальная ставка: <code>{max_bet} GC</code>", parse_mode="HTML")

# Проверяем, действует ли еще удача
    is_lucky = time.time() < u.get("luck_until", 0)
    
    # Если юзер под энергетиком, убираем самые плохие иконки из рандома
    icons = ["💎", "🎰", "🍋", "🍒", "🔔"]
    if not is_lucky:
        icons.append("💩") # Какашка выпадает только трезвым :)
        icons.append("⚙️")

    res = [random.choice(icons) for _ in range(3)]
    
    # Дальше твой код с проверкой выигрыша...

@dp.message(Command("казино", "слоты", prefix="."))
async def casino_visual(message: types.Message):
    u = get_u(message.from_user)
    now = time.time()
    args = message.text.split()

    # 1. ПРОВЕРКА КД (10 секунд)
    last_slots = u.get("last_slots", 0)
    if now - last_slots < 10:
        rem = int(10 - (now - last_slots))
        return await message.reply(f"⏳ <b>Тормози!</b> Барабаны еще остывают. Жди {rem} сек.", parse_mode="HTML")
    
    # 2. ПРОВЕРКА СТАВКИ
    if len(args) < 2 or not args[1].isdigit(): 
        return await message.reply("🎰 Введи ставку! Пример: <code>.слоты 100</code>", parse_mode="HTML")

    bet = int(args[1])
    if bet > 50000: 
        return await message.reply("⚠️ Максимальная ставка в казино: <code>50 000 GC</code>", parse_mode="HTML")
    if bet > u["coins"] or bet <= 0: 
        return await message.reply("❌ Недостаточно GC на балансе!")

    # 3. ЛОГИКА УДАЧИ (ЭНЕРГЕТИК)
    is_lucky = now < u.get("luck_until", 0)
    
    # Если юзер под энергосом — убираем какашку и шестеренку из списка
    if is_lucky:
        slots_icons = ["💎", "🎰", "🍋", "🍒", "🔔", "⭐"]
    else:
        slots_icons = ["💎", "🎰", "🍋", "🍒", "💩", "⚙️", "🔔"]

    # Фиксируем время крутки и списываем ставку сразу
    u["last_slots"] = now
    u["coins"] -= bet
    
    # 4. ВИЗУАЛ (КРУЧЕНИЕ)
    msg = await message.answer("🎰 <b>[ 🎰 | 🎰 | 🎰 ]</b>\n<i>Крутим барабаны...</i>", parse_mode="HTML")
    
    # Сократил анимацию до 2 этапов, чтобы не спамить запросами к Telegram
    for _ in range(2):
        await asyncio.sleep(0.7)
        fake_res = [random.choice(slots_icons) for _ in range(3)]
        await msg.edit_text(f"🎰 <b>[ {' | '.join(fake_res)} ]</b>\n<i>Барабаны вращаются...</i>", parse_mode="HTML")

    # 5. ФИНАЛЬНЫЙ РЕЗУЛЬТАТ
    res = [random.choice(slots_icons) for _ in range(3)]
    
    win = 0
    if res[0] == res[1] == res[2]:
        win = bet * 7 # Нерф до x7
        win_text = f"🔥 <b>ДЖЕКПОТ! x7</b>\nВыигрыш: <code>+{win} GC</code>"
    elif res[0] == res[1] or res[1] == res[2] or res[0] == res[2]:
        win = int(bet * 1.5) # Нерф до x1.5 (более стабильно)
        win_text = f"✅ <b>Победа! x1.5</b>\nВыигрыш: <code>+{win} GC</code>"
    else:
        win_text = f"❌ <b>Проигрыш!</b>\nПотеряно: <code>-{bet} GC</code>"

    u["coins"] += win
    
    # Используем глобальный флаг для автосейва
    global db_is_dirty
    db_is_dirty = True
    
    # Добавляем плашку удачи в финальное сообщение
    luck_status = "\n\n🍀 <i>Эффект удачи помог!</i>" if is_lucky else ""
    
    await asyncio.sleep(0.5)
    await msg.edit_text(f"🎰 <b>[ {' | '.join(res)} ]</b>\n\n{win_text}{luck_status}", parse_mode="HTML")

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

    tax = int(amount * 0.3) # 30% налог
    final_amount = amount - tax
    # Отдаем получателю final_amount, а у отправителя списываем полный amount

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
