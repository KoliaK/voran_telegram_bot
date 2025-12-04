import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

#scripts
from handlers import start, help, echo_handler, get_crypto_price, crypto_alert, broadcast


# gets credentials from .env file
load_dotenv()
bot_api_token = os.getenv('TELEGRAM_TOKEN')
# bot_name = os.getenv('BOT_NAME')

# prints logs to the terminal
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

if __name__ == '__main__':
    from db import init_db
    init_db()
    # build the app
    application = ApplicationBuilder().token(bot_api_token).build()

    # COMMAND HANDLERS
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('crypto', get_crypto_price))
    application.add_handler(CommandHandler('broadcast', broadcast))
    # this one filters TEXT and ensures COMMAND is not filtered by using ~
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo_handler))
    
    # <-- schedule and run an alert -->
    # <-- run pip install "python-telegram-bot[job-queue]" because this is not in the base lib -->
    # job_queue = application.job_queue
    # job_queue.run_repeating(crypto_alert, interval=10, first=5) # first=5 means wait 5 seconds before the first exec
    
    print('Bot is polling...')
    application.run_polling() #for large-scale projects, use .run_webhook() instead