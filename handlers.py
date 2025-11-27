from telegram import Update
from telegram.ext import ContextTypes
import asyncio # needed for echo_handler, not telegram-bot functions.

# no need to import AsyncIO module since ApplicationBuilder is built on top of async  
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('System is online!\nAwaiting instructions...')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = '''
    Available commands:
    /start
    /help
    '''
    await update.message.reply_text(help_text)

async def echo_handler(update, context):
    # effective_message helper makes sure the code grabs the text object itself no matter if it's
    # a new message, and edit, or a channel post
    text = update.effective_message.text
    if "process" in text.lower():
        await asyncio.sleep(3)
        await update.effective_message.reply_text(f'Processed: {text}')
    else:
        await update.effective_message.reply_text(f'I heard: {text}')