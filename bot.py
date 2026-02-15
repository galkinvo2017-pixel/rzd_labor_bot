def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("✅ Бот запущен. Начинаю опрос...")

    import asyncio
    import sys

    # Явное создание event loop для Python 3.14+
    if sys.version_info >= (3, 14):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(app.run_polling())
        finally:
            loop.close()
    else:
        asyncio.run(app.run_polling())
