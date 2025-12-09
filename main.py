import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

#scripts
from handlers import start, help, temp_mail, check_inbox, read_mail, dispose, broadcast, unknown_command_handler
import keep_alive


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
    application.add_handler(CommandHandler('tempmail', temp_mail))
    application.add_handler(CommandHandler('checkinbox', check_inbox))
    application.add_handler(CommandHandler('read', read_mail))
    application.add_handler(CommandHandler('dispose', dispose))
    application.add_handler(CommandHandler('broadcast', broadcast))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command_handler))
    
    # <-- schedule and run a repeating alert -->
    # <-- run pip install "python-telegram-bot[job-queue]" because this is not in the base lib -->
    # job_queue = application.job_queue
    # job_queue.run_repeating(some_function_from_handlers.py, interval=10, first=5) # first=5 means wait 5 seconds before the first exec
    
    # runs the fake website so the cloud service doesn't terminate the script
    keep_alive.keep_alive()

    # runs the bot
    print('Bot is polling...')
    application.run_polling() #for large-scale projects, use .run_webhook() instead of run_polling()