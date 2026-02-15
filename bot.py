# bot.py
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from knowledge_base import KNOWLEDGE_BASE

# === Настройка логирования ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# === Загрузка токена ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Ошибка: BOT_TOKEN не найден в .env")

# === Поиск ответа ===
def find_answer(question: str) -> dict | None:
    q = question.lower()
    for item in KNOWLEDGE_BASE:
        if any(kw in q for kw in item["keywords"]):
            return item
    return None

# === Обработчики ===
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
    user_question = update.message.text.strip()
    if not user_question:
        return

    result = find_answer(user_question)
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

# === Точка входа ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("✅ Бот запущен. Начинаю опрос...")
    
    # КРИТИЧЕСКИ ВАЖНО: запуск через asyncio.run() — только так работает на Render!
    import asyncio
    try:
        asyncio.run(app.run_polling())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем.")
    except Exception as e:
        logging.error(f"Ошибка запуска: {e}")
        raise

if __name__ == "__main__":
    main()
