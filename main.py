from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Состояния для процесса аренды
CHOOSE_CONSOLE, CHOOSE_DATES, CONFIRM = range(3)

# Доступные приставки
consoles = {
    "PS5": {"price_per_day": 500, "available": True},
    "Xbox Series X": {"price_per_day": 450, "available": True},
    "Nintendo Switch": {"price_per_day": 300, "available": False}
}

# Хранение заказов
orders = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.first_name
    await update.message.reply_text(
        f"Привет, {user}! Я бот для аренды приставок.\n"
        "Используй команды:\n/catalog — посмотреть приставки\n/rent — арендовать\n/status — статус заказа\n/help — помощь"
    )

async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = "Доступные приставки:\n"
    for console, info in consoles.items():
        status = "в наличии" if info["available"] else "нет в наличии"
        response += f"{console}: {info['price_per_day']} руб/день ({status})\n"
    await update.message.reply_text(response)

async def rent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выбери приставку из списка:\n" + "\n".join(consoles.keys()))
    return CHOOSE_CONSOLE

async def choose_console(update: Update, context: ContextTypes.DEFAULT_TYPE):
    console = update.message.text
    if console in consoles and consoles[console]["available"]:
        context.user_data["console"] = console
        await update.message.reply_text("Укажи даты аренды (например, 01.03.2025 - 03.03.2025):")
        return CHOOSE_DATES
    else:
        await update.message.reply_text("Приставка не найдена или недоступна. Попробуй снова.")
        return CHOOSE_CONSOLE

async def choose_dates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dates = update.message.text
    context.user_data["dates"] = dates
    console = context.user_data["console"]
    price = consoles[console]["price_per_day"]
    await update.message.reply_text(
        f"Ты выбрал {console} на даты {dates}.\n"
        f"Цена за день: {price} руб.\nПодтвердить заказ? (да/нет)"
    )
    return CONFIRM

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() == "да":
        user_id = update.message.from_user.id
        orders[user_id] = {
            "console": context.user_data["console"],
            "dates": context.user_data["dates"],
            "status": "В обработке"
        }
        await update.message.reply_text("Заказ оформлен! Проверь статус с помощью /status")
    else:
        await update.message.reply_text("Заказ отменен.")
    return ConversationHandler.END

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in orders:
        order = orders[user_id]
        await update.message.reply_text(
            f"Твой заказ:\nПриставка: {order['console']}\nДаты: {order['dates']}\nСтатус: {order['status']}"
        )
    else:
        await update.message.reply_text("У тебя нет активных заказов.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("По вопросам пишите @SupportRentBot")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Процесс аренды отменен.")
    return ConversationHandler.END

def main():
    # Вставьте свой токен от BotFather
    application = Application.builder().token("7642600141:AAF2JWaXdHK7r3xe8KRFZodPNxBd_e7vnOs").build()

    # Регистрация команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("catalog", catalog))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("help", help_command))

    # Обработчик процесса аренды
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("rent", rent)],
        states={
            CHOOSE_CONSOLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_console)],
            CHOOSE_DATES: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_dates)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(conv_handler)

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()