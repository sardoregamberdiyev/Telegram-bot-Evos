from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

TOKEN = "YOUR-BOT-TOKEN"

user_cart = {}
user_address = {}
waiting_for_address = {}
waiting_for_feedback_contact = {}
user_language = {}

TEXTS = {
    "start": {
        "uz": "Quyidagilardan birini tanlang:",
        "ru": "Выберите одно из следующего:",
        "en": "Please select one of the following:"
    },
    "settings_language": {
        "uz": "Tilni tanlang:",
        "ru": "Выберите язык:",
        "en": "Choose a language:"
    },
    "order_empty": {
        "uz": "Siz hech narsa buyurtma bermagansiz 🤷‍♂️",
        "ru": "Вы ещё ничего не заказали 🤷‍♂️",
        "en": "You haven't ordered anything 🤷‍♂️"
    },
    "address_saved": {
        "uz": "✅ Manzilingiz saqlandi: {}",
        "ru": "✅ Ваш адрес сохранен: {}",
        "en": "✅ Your address has been saved: {}"
    },
    "feedback_received": {
        "uz": "✅ Qabul qilindi, rahmat! 😊",
        "ru": "✅ Получено, спасибо! 😊",
        "en": "✅ Received, thank you! 😊"
    }
}

MENU_BUTTONS = {
    "uz": ["🍴 Menyu", "🛍 Mening buyurtmalarim", "📍 Manzilni sozlash", "✍️ Fikir bildirish", "⚙️ Sozlamalar"],
    "ru": ["🍴 Меню", "🛍 Мои заказы", "📍 Настроить адрес", "✍️ Оставить отзыв", "⚙️ Настройки"],
    "en": ["🍴 Menu", "🛍 My Orders", "📍 Set Address", "✍️ Feedback", "⚙️ Settings"]
}

LANG_BUTTONS = {
    "uz": [("🇺🇿 O'zbekcha", "lang_uz"), ("🇷🇺 Русский", "lang_ru"), ("🇬🇧 English", "lang_en")],
    "ru": [("🇺🇿 Узбекский", "lang_uz"), ("🇷🇺 Русский", "lang_ru"), ("🇬🇧 Английский", "lang_en")],
    "en": [("🇺🇿 Uzbek", "lang_uz"), ("🇷🇺 Russian", "lang_ru"), ("🇬🇧 English", "lang_en")]
}

def get_text(chat_id, key):
    lang = user_language.get(chat_id, "uz")
    return TEXTS[key][lang]

def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    lang = user_language.get(chat_id, "uz")
    buttons = MENU_BUTTONS[lang]
    keyboard = [
        [KeyboardButton(buttons[0])],
        [KeyboardButton(buttons[1]), KeyboardButton(buttons[2])],
        [KeyboardButton(buttons[3]), KeyboardButton(buttons[4])]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(get_text(chat_id, "start"), reply_markup=reply_markup)


def show_language_keyboard(chat_id):
    buttons = LANG_BUTTONS.get(user_language.get(chat_id, "uz"))
    keyboard = [[InlineKeyboardButton(text, callback_data=data)] for text, data in buttons]
    return InlineKeyboardMarkup(keyboard)

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    chat_id = update.message.chat.id

    if waiting_for_address.get(chat_id):
        user_address[chat_id] = text
        waiting_for_address[chat_id] = False
        update.message.reply_text(get_text(chat_id, "address_saved").format(text))
        start(update, context)
        return

    lang = user_language.get(chat_id, "uz")
    buttons = MENU_BUTTONS[lang]

    if text == buttons[0]:
        keyboard = [
            [KeyboardButton("🍔 Burgerlar"), KeyboardButton("🌯 Lavashlar")],
            [KeyboardButton("🥙 Shaurma"), KeyboardButton("🌭 XotDog")],
            [KeyboardButton("⬅️ Ortga")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("Menyudan bo‘lim tanlang:", reply_markup=reply_markup)

    elif text == "⬅️ Ortga":
        start(update, context)

    elif text == buttons[1]:
        cart = user_cart.get(chat_id, [])
        if not cart:
            update.message.reply_text(get_text(chat_id, "order_empty"))
        else:
            msg = "🛍 Sizning savatingiz:\n\n"
            total = 0
            for item in cart:
                total += item['price'] * item['qty']
                msg += f"{item['name']} x{item['qty']} = {item['price']*item['qty']} so'm\n"
            msg += f"\n💰 Jami: {total} so'm"
            update.message.reply_text(msg)

    elif text == buttons[2]:
        old_address = user_address.get(chat_id, "Manzil hali kiritilmagan")
        keyboard = [
            [InlineKeyboardButton("✏️ O‘zgartirish", callback_data="change_address")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            f"📍 Sizning manzilingiz: {old_address}",
            reply_markup=reply_markup
        )

    elif text == buttons[3]:
        keyboard = [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        waiting_for_feedback_contact[chat_id] = True
        update.message.reply_text(
            "🧑‍🍳 Sizning har bir fikringiz biz uchun muhim va zarur!\n"
            "📞 Bog‘lanishimiz uchun iltimos, telefon raqamingizni yuboring:",
            reply_markup=reply_markup
        )
        return

    elif text == buttons[4]:
        reply_markup = show_language_keyboard(chat_id)
        update.message.reply_text(get_text(chat_id, "settings_language"), reply_markup=reply_markup)

    elif text == "🍔 Burgerlar":
        show_burgers(update, context)

    elif text == "🌯 Lavashlar":
        show_lavash(update, context)

    elif text == "🥙 Shaurma":
        show_shaurma(update, context)

    elif text == "🌭 XotDog":
        show_xotdog(update, context)


def show_burgers(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data="qty_1"),
            InlineKeyboardButton("2", callback_data="qty_2"),
            InlineKeyboardButton("3", callback_data="qty_3"),
            InlineKeyboardButton("4", callback_data="qty_4"),
            InlineKeyboardButton("5", callback_data="qty_5"),
        ],
        [InlineKeyboardButton("🛒 Savatga qo‘shish", callback_data="add_SirliBurger")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    with open("imageuz.png", "rb") as photo:
        update.message.reply_photo(
            photo=photo,
            caption="<b>🍔 Chizburger</b>\n\n"
                    "Yumshoq bulochkada grill sous ostida shirali kotlet, "
                    "Chedder pishlog‘i, pomidor, bodring, piyoz va aysberg salati.\n\n"
                    "<b>💰 Narxi: 25 000 so'm</b>",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

def show_lavash(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data="qty_1"),
            InlineKeyboardButton("2", callback_data="qty_2"),
            InlineKeyboardButton("3", callback_data="qty_3"),
            InlineKeyboardButton("4", callback_data="qty_4"),
            InlineKeyboardButton("5", callback_data="qty_5"),
        ],
        [InlineKeyboardButton("🛒 Savatga qo‘shish", callback_data="add_Lavash")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    with open("lavash.png", "rb") as photo:
        update.message.reply_photo(
            photo=photo,
            caption="<b>🌯 Lavashlar</b>\n\n"
                    "Yumshoq bulochkada grill sous ostida shirali kotlet, "
                    "Chedder pishlog‘i, pomidor, bodring, piyoz va aysberg salati.\n\n"
                    "<b>💰 Narxi: 25 000 so'm</b>",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

def show_shaurma(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data="qty_1"),
            InlineKeyboardButton("2", callback_data="qty_2"),
            InlineKeyboardButton("3", callback_data="qty_3"),
            InlineKeyboardButton("4", callback_data="qty_4"),
            InlineKeyboardButton("5", callback_data="qty_5"),
        ],
        [InlineKeyboardButton("🛒 Savatga qo‘shish", callback_data="add_Shaurma")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    with open("shourma.png", "rb") as photo:
        update.message.reply_photo(
            photo=photo,
            caption="<b>🥙 Shaurma</b>\n\n"
                    "Yumshoq bulochkada grill sous ostida shirali kotlet, "
                    "Chedder pishlog‘i, pomidor, bodring, piyoz va aysberg salati.\n\n"
                    "<b>💰 Narxi: 25 000 so'm</b>",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )


def show_xotdog(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data="qty_1"),
            InlineKeyboardButton("2", callback_data="qty_2"),
            InlineKeyboardButton("3", callback_data="qty_3"),
            InlineKeyboardButton("4", callback_data="qty_4"),
            InlineKeyboardButton("5", callback_data="qty_5"),
        ],
        [InlineKeyboardButton("🛒 Savatga qo‘shish", callback_data="add_XotDog")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    with open("xotdog.png", "rb") as photo:
        update.message.reply_photo(
            photo=photo,
            caption="<b>🌭 XotDog</b>\n\n"
                    "Yumshoq bulochkada grill sous ostida shirali kotlet, "
                    "Chedder pishlog‘i, pomidor, bodring, piyoz va aysberg salati.\n\n"
                    "<b>💰 Narxi: 25 000 so'm</b>",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

def handle_location(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    update.message.reply_text("📍 Iltimos, manzilingizni matn ko‘rinishida kiriting (masalan: Chilonzor, 17-kvartal).")
    waiting_for_address[chat_id] = True

def handle_contact(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    if waiting_for_feedback_contact.get(chat_id):
        waiting_for_feedback_contact[chat_id] = False
        update.message.reply_text(get_text(chat_id, "feedback_received"))
        start(update, context)

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat.id
    data = query.data

    query.answer()

    if data == "change_address":
        keyboard = [[KeyboardButton("📍 Yangi manzil yuborish", request_location=True)], [KeyboardButton("⬅️ Ortga")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        query.message.reply_text("📍 Yangi manzilni yuboring:", reply_markup=reply_markup)

    elif data.startswith("lang_"):
        lang = data.split("_")[1]
        user_language[chat_id] = lang
        query.message.reply_text(f"Til o'zgartirildi ✅ ({lang}) \n\nQayta /start bosing 😊")
        start(update, context)

    elif data.startswith("qty_"):
        qty = int(data.split("_")[1])
        context.user_data["selected_qty"] = qty
        query.message.reply_text(f"{qty} dona tanlandi ✅")

    elif data.startswith("add_"):
        product_key = data.split("_")[1]
        qty = context.user_data.get("selected_qty", 1)

        products = {
            "SirliBurger": {"name": "🍔 Chizburger", "price": 25000},
            "Lavash": {"name": "🌯 Lavash", "price": 22000},
            "Shaurma": {"name": "🥙 Shaurma", "price": 20000},
            "XotDog": {"name": "🌭 XotDog", "price": 15000},
        }

        product = products.get(product_key)
        if product:
            cart = user_cart.get(chat_id, [])
            cart.append({"name": product["name"], "price": product["price"], "qty": qty})
            user_cart[chat_id] = cart

            total_items = sum(item["qty"] for item in cart)

            keyboard = [
                [InlineKeyboardButton(f"🛍 Savatni ko‘rish ({total_items} ta mahsulot)", callback_data="view_cart")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            query.message.reply_text(
                f"{product['name']} x{qty} savatga qo‘shildi ✅",
                reply_markup=reply_markup
            )
        else:
            query.message.reply_text("❌ Mahsulot topilmadi")


    elif data == "view_cart":
        cart = user_cart.get(chat_id, [])
        if not cart:
            query.message.reply_text("🛍 Savatingiz bo‘sh 🤷‍♂️")
        else:
            msg = "🛍 Sizning savatingiz:\n\n"
            total = 0
            total_items = 0
            for item in cart:
                total += item["price"] * item["qty"]
                total_items += item["qty"]
                msg += f"{item['name']} x{item['qty']} = {item['price'] * item['qty']} so‘m\n"
            msg += f"\n📦 Umumiy: {total_items} ta mahsulot\n💰 Jami: {total} so‘m"
            query.message.reply_text(msg)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.location, handle_location))
    dp.add_handler(MessageHandler(Filters.contact, handle_contact))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CallbackQueryHandler(button_callback))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
