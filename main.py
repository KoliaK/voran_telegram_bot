import os
import logging
from telegram import BotCommand
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

#scripts
from handlers import start, help, temp_mail, check_inbox, read_mail, dispose, broadcast, find_user, unknown_command_handler
import keep_alive


# get credentials from .env file
load_dotenv()
bot_api_token = os.getenv('TELEGRAM_TOKEN')
# bot_name = os.getenv('BOT_NAME')

# prints logs to the terminal
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# set the bot commands menu in Telegram
# displays command suggestions as the user types
async def post_init(application: Application) -> None:
    print('📝 Setting up bot commands...')

    # note: don't list admin-only commands (broadcast) 
    # or variable commands (read) in the public menu to keep it clean.
    COMMANDS = [
        BotCommand("start", "Starts the bot"),
        BotCommand("help", "Lists available commands"),
        BotCommand("tempmail", "Creates temporary email"),
        BotCommand("checkmail", "Checks inbox"),
        BotCommand("dispose", "Deletes current identity"),
    ]

    # await application.bot.set_my_commands(COMMANDS)
    await application.bot.set_my_commands(COMMANDS)
    print('✅ Commands set successfully.')

if __name__ == '__main__':
    from db import init_db
    init_db()
    # build the app
    application = ApplicationBuilder().token(bot_api_token).post_init(post_init).build()

    # COMMAND HANDLERS
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('tempmail', temp_mail))
    application.add_handler(CommandHandler('checkinbox', check_inbox))
    application.add_handler(CommandHandler('read', read_mail))
    application.add_handler(CommandHandler('dispose', dispose))
    application.add_handler(CommandHandler('finduser', find_user))
    application.add_handler(CommandHandler('broadcast', broadcast))
    # this one filters invalid /COMMANDS.
    application.add_handler(MessageHandler(filters.TEXT, unknown_command_handler))
    
    # runs the fake website so the cloud service doesn't terminate the script
    keep_alive.keep_alive()

    # runs the bot
    print('Bot is polling...')
    application.run_polling() #for large-scale projects, use .run_webhook() instead of .run_polling()