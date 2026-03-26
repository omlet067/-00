import os, asyncio, random, json, time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

ADMIN_ID = 7560933378
TOKEN = os.getenv("TYCOON_TOKEN")
DB_FILE = "economy_visual.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- СТИЛЬНЫЙ МАГАЗИН И ПРЕДМЕТЫ ---
ITEMS = {
    "⚡энергетик": [6000, 0, "🥤 Энергетический напиток | Дарует удачу в казино на 3 минуты | Одноразовый"],
    "👟подкрадули": [1500, 0, "👟 Стильные кеды | +100 к крутости | Не приносят дохода, но ты выглядишь шикарно"],
    "⛺палатка": [5000, 50, "🏕 Лесная палатка | Пассивный доход: 50 GC/час | Окупаемость: ~4 дня"],
    "📦пункт_wb": [25000, 200, "📦 Собственный пункт выдачи Wildberries | Пассивный доход: 200 GC/час | Окупаемость: ~5 дней"],
    "🏢майнинг_отель": [150000, 800, "🏭 Майнинг-ферма в подвале | Пассивный доход: 800 GC/час | Окупаемость: ~7.8 дней"],
    "🚀стартап": [1000000, 5000, "🚀 IT-стартап 'Glitch Corp' | Пассивный доход: 5 000 GC/час | Окупаемость: ~8.3 дней"],
    "👑статус_олигарха": [9999999, 0, "👑 Элитный статус | Подтверждение твоего богатства | Доступ в закрытый клуб олигархов"]
}

# --- СИСТЕМА ДАННЫХ ---
users = {}
db_is_dirty = False

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
            "last_bonus": 0,
            "luck_until": 0,
            "last_slots": 0
        }
        db_is_dirty = True
    else:
        # Проверка новых полей для старых игроков
        for key in ["luck_until", "last_slots"]:
            if key not in users[uid]:
                users[uid][key] = 0
                db_is_dirty = True
    return users[uid]

# --- КОМАНДЫ ---

# --- МАГАЗИН ---
@dp.message(Command("магазин", "маркет", prefix="."))
async def shop_visual(message: types.Message):
    text = "🛒 <b>ГЛИТЧ-МАРКЕТ</b>\n"
    text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"
    
    # Красивые названия для отображения
    display_names = {
        "⚡энергетик": "⚡ ЭНЕРГЕТИК",
        "👟подкрадули": "👟 ПОДКРАДУЛИ", 
        "⛺палатка": "⛺ ПАЛАТКА",
        "📦пункт_wb": "📦 ПУНКТ WB",
        "🏢майнинг_отель": "🏢 МАЙНИНГ-ОТЕЛЬ",
        "🚀стартап": "🚀 СТАРТАП",
        "👑статус_олигарха": "👑 СТАТУС ОЛИГАРХА"
    }
    
    for item, info in ITEMS.items():
        price = f"{info[0]:,} GC".replace(",", " ")
        income = f"+{info[1]} GC/час" if info[1] > 0 else "▫️ Без дохода"
        
        # Красивое название для вывода
        nice_name = display_names.get(item, item)
        
        # Команда для покупки
        cmd_name = item.replace("⚡", "").replace("👟", "").replace("⛺", "").replace("📦", "").replace("🏢", "").replace("🚀", "").replace("👑", "")
        
        text += (f"🔹 <b>{nice_name}</b>\n"
                 f"┣ Цена: <code>{price}</code>\n"
                 f"┣ {income}\n"
                 f"┣ 📝 {info[2]}\n"
                 f"┗ <code>.купить {cmd_name}</code>\n\n")
    
    text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
    text += "💡 <i>Подсказка: бизнесы приносят доход каждый час автоматически!</i>"
    
    await message.answer(text, parse_mode="HTML")

# --- ПРОФИЛЬ ---
@dp.message(Command("профиль", prefix="."))
async def profile_visual(message: types.Message):
    args = message.text.split()
    
    if len(args) > 1 and args[1].isdigit():
        target_id = args[1]
    else:
        target_id = str(message.from_user.id)

    if target_id not in users:
        return await message.reply("❌ Игрок с таким ID не найден в базе данных.")

    u = users[target_id]
    
    # Считаем доход и собираем информацию о предметах
    total_income = 0
    inventory = u.get("inventory", [])
    business_items = []
    decorative_items = []
    
    for item in inventory:
        if item in ITEMS:
            income = ITEMS[item][1]
            total_income += income
            if income > 0:
                # Красивые названия для бизнесов
                business_names = {
                    "⛺палатка": "⛺ Палатка",
                    "📦пункт_wb": "📦 Пункт WB", 
                    "🏢майнинг_отель": "🏢 Майнинг-отель",
                    "🚀стартап": "🚀 Стартап"
                }
                business_items.append(f"{business_names.get(item, item)} (+{income} GC/час)")
            else:
                # Декоративные предметы
                deco_names = {
                    "⚡энергетик": "⚡ Энергетик",
                    "👟подкрадули": "👟 Подкрадули",
                    "👑статус_олигарха": "👑 Статус олигарха"
                }
                decorative_items.append(deco_names.get(item, item))

    # Формируем текст инвентаря
    inv_parts = []
    if business_items:
        inv_parts.append("🏢 <b>БИЗНЕСЫ:</b>\n" + "\n".join([f"  • {item}" for item in business_items]))
    if decorative_items:
        inv_parts.append("✨ <b>ПРЕДМЕТЫ:</b>\n" + "\n".join([f"  • {item}" for item in decorative_items]))
    
    inv_text = "\n\n".join(inv_parts) if inv_parts else "🎒 Пусто"
    
    name = u.get('name', 'Игрок').replace('<', '&lt;').replace('>', '&gt;')
    
    # Прогресс до следующего бизнеса (для мотивации)
    next_business = ""
    if u.get('coins', 0) < 5000:
        need = 5000 - u['coins']
        next_business = f"\n💡 До палатки: <code>{need} GC</code>"
    elif u.get('coins', 0) < 25000:
        need = 25000 - u['coins']
        next_business = f"\n💡 До пункта WB: <code>{need} GC</code>"

    text = (
        f"👤 <b>ПРОФИЛЬ: {name}</b>\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"💰 Баланс: <code>{u.get('coins', 0):,} GC</code>\n"
        f"📈 Пассивный доход: <code>{total_income:,} GC/час</code>\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"{inv_text}{next_business}\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"🆔 ID: <code>{target_id}</code>"
    ).replace(",", " ")

    await message.answer(text, parse_mode="HTML")

# --- КУПИТЬ ---
@dp.message(Command("купить", prefix="."))
async def buy_cmd(message: types.Message):
    u = get_u(message.from_user)
    args = message.text.split()
    
    if len(args) < 2: 
        return await message.reply("❌ Напиши, что хочешь купить!\nПример: <code>.купить энергетик</code>", parse_mode="HTML")
    
    target = args[1].lower()
    
    # Ищем подходящий предмет
    item_key = None
    for name in ITEMS:
        clean_name = name.replace("⚡", "").replace("👟", "").replace("⛺", "").replace("📦", "").replace("🏢", "").replace("🚀", "").replace("👑", "").lower()
        
        if target in clean_name or clean_name in target:
            item_key = name
            break
            
    if not item_key: 
        return await message.reply("❓ Такого товара нет в магазине. Проверь <code>.маркет</code>", parse_mode="HTML")
    
    price = ITEMS[item_key][0]
    description = ITEMS[item_key][2]
    
    if u["coins"] < price: 
        need = price - u["coins"]
        return await message.reply(f"❌ Недостаточно GC!\n💰 Нужно: <code>{price} GC</code>\n💸 Не хватает: <code>{need} GC</code>\n\n💡 Совет: используй <code>.работа</code> или выиграй в <code>.казино</code>", parse_mode="HTML")
    
    # Списываем деньги и добавляем в инвентарь
    u["coins"] -= price
    u["inventory"].append(item_key)
    save_db()
    
    # Красивое название для ответа
    display_names = {
        "⚡энергетик": "⚡ Энергетик",
        "👟подкрадули": "👟 Подкрадули",
        "⛺палатка": "⛺ Палатка",
        "📦пункт_wb": "📦 Пункт WB",
        "🏢майнинг_отель": "🏢 Майнинг-отель",
        "🚀стартап": "🚀 Стартап",
        "👑статус_олигарха": "👑 Статус олигарха"
    }
    nice_name = display_names.get(item_key, item_key)
    
    # Эффект покупки
    effect_text = ""
    if item_key == "⚡энергетик":
        effect_text = "\n✨ <i>Используй .пить чтобы активировать удачу!</i>"
    elif ITEMS[item_key][1] > 0:
        effect_text = f"\n📈 <i>Теперь ты получаешь +{ITEMS[item_key][1]} GC каждый час!</i>"
    elif item_key == "👑статус_олигарха":
        effect_text = "\n👑 <i>Теперь ты официально олигарх! Все в чате знают твой статус.</i>"
    
    await message.reply(
        f"✅ <b>ПОКУПКА УСПЕШНА!</b>\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"🎁 Приобретено: <b>{nice_name}</b>\n"
        f"💰 Цена: <code>{price} GC</code>\n"
        f"📝 Описание: {description}{effect_text}\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"💳 Остаток: <code>{u['coins']:,} GC</code>".replace(",", " "), 
        parse_mode="HTML"
    )

# --- ПИТЬ (ЭНЕРГЕТИК) ---
@dp.message(Command("пить", prefix="."))
async def drink_energy(message: types.Message):
    u = get_u(message.from_user)
    
    if "⚡энергетик" not in u["inventory"]:
        return await message.reply("🛒 Сначала купи энергетик в <code>.маркет</code>!", parse_mode="HTML")
    
    u["inventory"].remove("⚡энергетик")
    u["luck_until"] = time.time() + 180  # 3 минуты удачи
    
    global db_is_dirty
    db_is_dirty = True
    
    await message.reply("🥤 <b>Глитч-Раш выпит!</b>\n🍀 Твои чувства обострены. Удача в казино повышена на 3 минуты! 🔥", parse_mode="HTML")

# --- ИНФО ---
@dp.message(Command("инфо", "помощь", "help", prefix="."))
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
        "• <code>.казино [ставка]</code> — слоты (шанс x7 и x1.5)\n"
        "• <code>.топ</code> — список богачей чата\n\n"
        "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        "🤖 <i>Версия: 1.2.0 Visual Edition</i>"
    )
    await message.answer(text, parse_mode="HTML")

# --- УДАЛИТЬ АККАУНТ ---
@dp.message(Command("удалить_аккаунт", prefix="."))
async def delete_my_profile(message: types.Message):
    global db_is_dirty
    uid = str(message.from_user.id)
    args = message.text.split()
    
    if uid not in users:
        return await message.reply("❌ У тебя и так нет профиля в базе.")

    if len(args) < 2 or args[1].upper() != "ДА":
        return await message.reply(
            "⚠️ <b>ВНИМАНИЕ!</b>\n"
            "Это удалит твой баланс, инвентарь и все достижения навсегда.\n\n"
            "Чтобы подтвердить, напиши: <code>.удалить_аккаунт ДА</code>", 
            parse_mode="HTML"
        )
    
    del users[uid]
    db_is_dirty = True
    
    await message.answer("🗑 <b>Твой профиль был полностью удален.</b>\nДо встречи!", parse_mode="HTML")

# --- РАБОТА ---
@dp.message(Command("работа", prefix="."))
async def work_cmd(message: types.Message):
    u = get_u(message.from_user)
    now = time.time()
    
    if now - u.get("last_work", 0) < 1800:
        rem = int((1800 - (now - u["last_work"])) / 60)
        return await message.reply(f"⏳ Жди! Работать можно раз в 30 минут. Осталось {rem} мин.")
    
    salary = random.randint(200, 600)
    u["coins"] += salary
    u["last_work"] = now
    save_db()
    
    jobs = [
        "📦 разгрузил WB-заказы",
        "🛠 настроил роутер соседке",
        "💾 продал конфиг в Майне",
        "🪙 вложился в крипту",
        "💦 поработал(а) на трассе",
        "🍔 поел бургеры",
        "💸 батя дал на додеп"
    ]
    job = random.choice(jobs)
    await message.reply(f"⚒ Ты {job} и получил `{salary} GC`!", parse_mode="Markdown")

# --- КАЗИНО ---
@dp.message(Command("казино", "слоты", prefix="."))
async def casino_visual(message: types.Message):
    u = get_u(message.from_user)
    now = time.time()
    args = message.text.split()

    # Проверка КД (10 секунд)
    last_slots = u.get("last_slots", 0)
    if now - last_slots < 10:
        rem = int(10 - (now - last_slots))
        return await message.reply(f"⏳ <b>Тормози!</b> Барабаны еще остывают. Жди {rem} сек.", parse_mode="HTML")
    
    # Проверка ставки
    if len(args) < 2 or not args[1].isdigit(): 
        return await message.reply("🎰 Введи ставку! Пример: <code>.слоты 100</code>", parse_mode="HTML")

    bet = int(args[1])
    max_bet = 50000
    
    if bet > max_bet: 
        return await message.reply(f"⚠️ Максимальная ставка: <code>{max_bet} GC</code>", parse_mode="HTML")
    if bet > u["coins"] or bet <= 0: 
        return await message.reply("❌ Недостаточно GC на балансе!")

    # Логика удачи (энергетик)
    is_lucky = now < u.get("luck_until", 0)
    
    if is_lucky:
        slots_icons = ["💎", "🎰", "🍋", "🍒", "🔔", "⭐"]
    else:
        slots_icons = ["💎", "🎰", "🍋", "🍒", "💩", "⚙️", "🔔"]

    u["last_slots"] = now
    u["coins"] -= bet
    
    # Визуал
    msg = await message.answer("🎰 <b>[ 🎰 | 🎰 | 🎰 ]</b>\n<i>Крутим барабаны...</i>", parse_mode="HTML")
    
    for _ in range(2):
        await asyncio.sleep(0.7)
        fake_res = [random.choice(slots_icons) for _ in range(3)]
        await msg.edit_text(f"🎰 <b>[ {' | '.join(fake_res)} ]</b>\n<i>Барабаны вращаются...</i>", parse_mode="HTML")

    # Финальный результат
    res = [random.choice(slots_icons) for _ in range(3)]
    
    win = 0
    if res[0] == res[1] == res[2]:
        win = bet * 7
        win_text = f"🔥 <b>ДЖЕКПОТ! x7</b>\nВыигрыш: <code>+{win} GC</code>"
    elif res[0] == res[1] or res[1] == res[2] or res[0] == res[2]:
        win = int(bet * 1.5)
        win_text = f"✅ <b>Победа! x1.5</b>\nВыигрыш: <code>+{win} GC</code>"
    else:
        win_text = f"❌ <b>Проигрыш!</b>\nПотеряно: <code>-{bet} GC</code>"

    u["coins"] += win
    
    global db_is_dirty
    db_is_dirty = True
    
    luck_status = "\n\n🍀 <i>Эффект удачи помог!</i>" if is_lucky else ""
    
    await asyncio.sleep(0.5)
    await msg.edit_text(f"🎰 <b>[ {' | '.join(res)} ]</b>\n\n{win_text}{luck_status}", parse_mode="HTML")

# --- ТОП ---
@dp.message(Command("топ", prefix="."))
async def top_players(message: types.Message):
    load_db()
    
    sorted_users = sorted(users.items(), key=lambda x: x[1].get("coins", 0), reverse=True)[:5]
    
    if not sorted_users:
        return await message.reply("📈 В списке пока пусто!")

    text = "👑 <b>ТОП МАЖОРОВ ЧАТА</b>\n"
    text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"
    
    for i, (uid, data) in enumerate(sorted_users, 1):
        name = data.get("name", "Аноним")
        coins = data.get("coins", 0)
        
        icon = "🥇" if i == 1 else f"{i}."
        text += f"{icon} <b>{name}</b> — <code>{coins:,} GC</code>\n".replace(",", " ")

    text += "\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"
    await message.answer(text, parse_mode="HTML")

# --- ПЕРЕВОД ---
@dp.message(Command("передать", "дать", prefix="."))
async def transfer_coins_visual(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("⚠️ Ответь на сообщение получателя!")

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

    tax = int(amount * 0.3)
    final_amount = amount - tax
    
    sender["coins"] -= amount
    receiver["coins"] += final_amount
    save_db()

    final_text = (f"✅ <b>ПЕРЕВОД ВЫПОЛНЕН</b>\n"
                  f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                  f"💸 Отправитель: <code>{message.from_user.first_name}</code>\n"
                  f"💸 Получатель: <code>{message.reply_to_message.from_user.first_name}</code>\n"
                  f"💰 Сумма: <code>{amount} GC</code>\n"
                  f"💸 Налог (30%): <code>{tax} GC</code>\n"
                  f"✨ Получено: <code>{final_amount} GC</code>")
    
    await message.reply(final_text, parse_mode="HTML")

# --- ЗАЧИСЛИТЬ (АДМИН) ---
@dp.message(Command("зачислить", prefix="."))
async def set_balance(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("❌ Ты не админ.")

    args = message.text.split()
    if len(args) < 2:
        return await message.reply("Пример: `.зачислить 999999` (реплаем на юзера)")

    amount = int(args[1])
    target_user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    
    u = get_u(target_user)
    u["coins"] = amount
    save_db()
    await message.reply(f"👑 Баланс <code>{target_user.first_name}</code> изменен на <code>{amount} GC</code>", parse_mode="HTML")

# --- ФОНОВЫЙ ДОХОД ---
async def passive_income():
    while True:
        await asyncio.sleep(3600)
        load_db()
        for uid in users:
            for item in users[uid].get("inventory", []):
                if item in ITEMS:
                    users[uid]["coins"] += ITEMS[item][1]
        save_db()
        print("💸 Доход начислен!")

async def main():
    load_db()
    asyncio.create_task(passive_income())
    print("--- Glitch Visual Tycoon Ready ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
