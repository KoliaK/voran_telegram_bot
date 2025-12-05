import httpx # if using requests instead, the bot would handle one request at a time only
import asyncio # this is necessary for sleep, wait, and gather tools
import os
from telegram import Update
from telegram.ext import ContextTypes

# scripts
import db

# no need to import AsyncIO module since ApplicationBuilder is built on top of async  
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    db.add_user(user.id, user.username)
    await update.message.reply_text('System is online!\nAwaiting instructions...')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = '''
    Available commands:
    /start
    /help
    /crypto
    /broadcast (Admin Only)
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
        # prints the chat ID in the terminal
        print(f"Your Chat ID is: {update.effective_chat.id}")

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

async def crypto_alert(context: ContextTypes.DEFAULT_TYPE) -> None:
    # no need to import dotenv and call load_dotenv() again here because it's already done in main.py
    chat_id = os.getenv('MY_CHAT_ID')
    bot_name = os.getenv('BOT_NAME')
    await context.bot.send_message(chat_id=chat_id, text=f'🔔 {bot_name} Alert: Checking systems...')

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # get update.effective_user.id and compare to MY_CHAT_ID from .env
    # if they don't match, reply "⛔ Access Denied." and return
    # check if they typed a message with len(context.args) > 0

    admin_id = int(os.getenv('MY_CHAT_ID'))
    sender_id = update.effective_user.id
    
    # security check
    if sender_id != admin_id:
        await update.message.reply_text('⛔ Access Denied.')
        return
    
    # validation to check if the message is empty
    if len(context.args) == 0:
        await update.message.reply_text('Usage: /broadcast <message>')
        return
    
    message = ' '.join(context.args)
    all_users = db.get_all_users()

    await update.message.reply_text(f'📢 Broadcasting to {len(all_users)} users...')

    for user_id in all_users:
        try:
            # sends message to each user_id from the db
            await context.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            # if a user blocked the bot, this prevents the loop from breaking
            print(f'Failed to send to {user_id}: {e}')

    await update.message.reply_text('✅ Broadcast complete.')
    