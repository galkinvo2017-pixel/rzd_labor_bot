# bot.py
import os
import logging
import asyncio
import sys
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from knowledge_base import KNOWLEDGE_BASE

# === Настройка ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не задан в .env")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def find_answer(question: str) -> dict | None:
    q = question.lower()
    for item in KNOWLEDGE_BASE:
        if any(kw in q for kw in item["keywords"]):
            return item
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Я — бот по трудовому праву и коллективному договору ОАО «РЖД».\n\n"
        "📌 Задайте любой вопрос, например:\n"
        "• Какая индексация зарплаты на РЖД?\n"
        "• Что положено при рождении ребёнка?\n"
        "• Могут ли уволить обоих супругов?"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        return
    result = find_answer(text)
    if result:
        response = f"{result['answer']}\n\n📌 Источник: {result['source']}"
    else:
        response = "Не нашёл ответа. Попробуйте уточнить вопрос."
    await update.message.reply_text(response)

# === Главная функция ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("✅ Бот запущен. Начинаю опрос...")

    # Универсальный запуск для Python 3.7–3.14+
    try:
        # Попытка стандартного запуска
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
