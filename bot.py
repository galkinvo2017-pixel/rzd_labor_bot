# bot.py
import os
import logging
import asyncio
import sys
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from knowledge_base import KNOWLEDGE_BASE

# === Настройка логирования ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    force=True  # Перезаписывает настройки, если уже были
)

logger = logging.getLogger(__name__)

# === Загрузка токена ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Ошибка: BOT_TOKEN не найден. Убедитесь, что он задан в переменных окружения.")

# === Поиск ответа по ключевым словам ===
def find_answer(question: str) -> dict | None:
    q = question.lower()
    for item in KNOWLEDGE_BASE:
        if any(kw in q for kw in item["keywords"]):
            return item
    return None

# === Обработчики сообщений ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Я — бот по трудовому праву и коллективному договору ОАО «РЖД».\n\n"
        "📌 Задайте любой вопрос, например:\n"
        "• Какая индексация зарплаты на РЖД?\n"
        "• Что положено при рождении ребёнка?\n"
        "• Могут ли уволить обоих супругов?\n\n"
        "⚠️ Я не заменяю юриста. Для сложных ситуаций обратитесь к специалисту."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        return

    result = find_answer(text)
    if result:
        response = f"{result['answer']}\n\n📌 Источник: {result['source']}"
    else:
        response = (
            "К сожалению, я не нашёл точного ответа в своей базе.\n\n"
            "💡 Попробуйте:\n"
            "• Уточнить вопрос;\n"
            "• Использовать слова: «РЖД», «зарплата», «отпуск», «увольнение», «льготы»."
        )
    await update.message.reply_text(response)

# === Функция очистки webhook'а ===
async def clear_webhook():
    """Удаляет webhook, чтобы гарантировать режим polling."""
    app = Application.builder().token(BOT_TOKEN).build()
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook успешно удалён. Режим: long polling.")
    except Exception as e:
        logger.error(f"⚠️ Ошибка при удалении webhook'а: {e}")

# === Основная функция запуска ===
def main():
    logger.info("🚀 Запуск бота...")

    # Шаг 1: Очистка webhook'а
    asyncio.run(clear_webhook())

    # Шаг 2: Создание приложения
    app = Application.builder().token(BOT_TOKEN).build()

    # Шаг 3: Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("✅ Бот готов к работе. Начинаю опрос...")

    # Шаг 4: Запуск с поддержкой Python 3.14+
    try:
        asyncio.run(app.run_polling())
    except RuntimeError as e:
        if "no current event loop" in str(e) or "отсутствует текущий цикл" in str(e):
            # Fallback для Python 3.14+
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(app.run_polling())
            finally:
                loop.close()
        else:
            raise

if __name__ == "__main__":
    main()
