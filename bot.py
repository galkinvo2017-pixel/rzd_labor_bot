# bot.py
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from knowledge_base import KNOWLEDGE_BASE

# Загрузка токена
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ Ошибка: токен не найден! Убедитесь, что в файле .env есть строка BOT_TOKEN=ваш_токен")

# Логирование
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

def main():
    # Создаём приложение
    app = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Бот запущен и ожидает сообщений...")
    
    # ЗАПУСК В АСИНХРОННОМ РЕЖИМЕ
    import asyncio
    asyncio.run(app.run_polling())

if __name__ == "__main__":
    main()
