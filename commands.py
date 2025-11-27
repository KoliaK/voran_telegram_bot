from telegram import Update
from telegram.ext import ContextTypes

# no need to import AsyncIO module since ApplicationBuilder is built on top of async  
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'System is online. Awaiting instructions.')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = '''
    Available commands:
    /start
    /help
    '''
    await update.message.reply_text(help_text)