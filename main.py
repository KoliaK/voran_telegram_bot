import os
from telegram.ext import ApplicationBuilder, CommandHandler
from dotenv import load_dotenv

# Gets credentials from .env file
load_dotenv()
bot_api_token = os.getenv('TELEGRAM_TOKEN')
bot_name = os.getenv('BOT_NAME')

application = ApplicationBuilder().token(bot_api_token).build()




async def start(update, context):
    await update.message.reply_text(f'{bot_name} is online. awaiting instructions.')



if __name__ == '__main__':
    application.add_handler(CommandHandler('start', start))
    application.run_polling() #for large-scale projects, use .run_webhook() instead
