import httpx
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
    /crypto
    '''
    await update.message.reply_text(help_text)

async def echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # effective_message helper makes sure the code grabs the text object itself no matter if it's
    # a new message, and edit, or a channel post
    text = update.effective_message.text
    if "process" in text.lower():
        await asyncio.sleep(3)
        await update.effective_message.reply_text(f'Processed: {text}')
    else:
        await update.effective_message.reply_text(f'I heard: {text}')

async def get_crypto_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # validate if user types a valid crypto currency name
    if len(context.args) == 0:
        await update.effective_message.reply_text('Please provide a crypto name. Usage: /crypto <coin_name>')
        return
    
    coin = context.args[0].lower()  
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
        if coin in data:
            price = data[coin]['usd']
            await update.effective_message.reply_text(f'💰 {coin.upper()}: ${price}')
        else:
            await update.effective_message.reply_text(f'❌ Could not find coin: {coin}')
    except Exception as e:
        print(f'ERROR: {e}')
        await update.effective_message.reply_text('⚠️ Error fetching data.')