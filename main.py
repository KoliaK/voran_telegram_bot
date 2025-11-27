import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

#scripts
from handlers import start, help, echo_handler

# gets credentials from .env file
load_dotenv()
bot_api_token = os.getenv('TELEGRAM_TOKEN')
# bot_name = os.getenv('BOT_NAME')

# prints logs to the terminal
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

if __name__ == '__main__':
    # build the app
    application = ApplicationBuilder().token(bot_api_token).build()

    # add command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    # this one filters TEXT and ensures COMMAND is not filtered by using ~
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo_handler))
    
    print('Bot is polling...')
    application.run_polling() #for large-scale projects, use .run_webhook() instead