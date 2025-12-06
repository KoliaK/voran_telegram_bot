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
    await update.message.reply_text('System is online!\nAwaiting instructions...\nType /help for a list of commands.')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = '''
    Available commands:
    /start
    /help
    /tempmail
    /checkmail
    /read <id>
    /broadcast <msg> (Admin Only)
    '''
    await update.message.reply_text(help_text)

async def tempmail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # GUERRILLA MAIL API ENDPOINT
    url = "https://api.guerrillamail.com/ajax.php?f=get_email_address"

    try:
        # httpx does not follow redirects by default
        # follow_redirects=True is necessary so it
        # doesn't stop after a 301 Redirect
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url)
            data = response.json()
            # check the raw data if needed:
            # print("🔍 RAW DATA:", data)

            email_address = data['email_addr']
            sid_token = data['sid_token']

            # save session ID (necessary for GuerrillaMail)
            context.user_data['temp_email'] = email_address
            context.user_data['sid_token'] = sid_token

            await update.effective_message.reply_text(
                f'🛡️ **Privacy Shield Active (GuerrillaMail)**\n\n'
                f'📧 Address: `{email_address}`\n'
                f'🔑 Session ID: `{sid_token[:10]}...`\n\n'
                f'Use this email. Type /checkmail to see your inbox.',
                parse_mode='Markdown'
            )
    except Exception as e:
        print(f'🔴 Error in /tempmail: {e}')
        # if any response exists, print the raw text to see if it's an HTML error page
        if 'response' in locals():
            print(f"🔴 Server Response: {response.text}")
        await update.effective_message.reply_text('⚠️ API Error. Try again.')

async def checkmail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # retrieve session id
    sid_token = context.user_data.get('sid_token')
    email_address = context.user_data.get('temp_email')

    if not sid_token:
        await update.effective_message.reply_text("❌ No active session. Type /tempmail first.")
        return

    # fetch inbox based on the session id token
    url = f"https://api.guerrillamail.com/ajax.php?f=get_email_list&offset=0&sid_token={sid_token}"

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url)
            data = response.json()
            # check the raw data if needed:
            # print("🔍 RAW DATA:", data)

            # guerrillamail returns a 'list' key
            messages = data.get('list', [])

            # guerrillamail usually sends a welcome email
            # so list is rarely empty
            # check if empty anyway just to make sure
            if not messages or len(messages) == 0:
                await update.effective_message.reply_text(f'📭 Inbox empty for {email_address}')
                return
            
            # loop through messages
            reply_text = f"📬 **Inbox for {email_address}**\n"
            # limit to 5 emails to avoid spamming chat
            for msg in messages[:5]: 
                msg_id = msg['mail_id']
                sender = msg['mail_from']
                subject = msg['mail_subject']
                reply_text += f'\n-------------------\n🆔 ID: {msg_id}\n👤 From: {sender}\n📝 Subject: {subject}'

            reply_text += "\n\nTo read a message content, type /read <id> command!"
            await update.effective_message.reply_text(reply_text, parse_mode='Markdown')
    
    except Exception as e:
        print(f'🔴 Error in /checkmail: {e}')
        await update.effective_message.reply_text('⚠️ Error fetching messages.')

async def read_mail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # check if the user typed an id
    if len(context.args) == 0:
        await update.effective_message.reply_text('Usage: /read <email_id>')

    mail_id = context.args[0]

    # check if the session is active
    sid_token = context.user_data.get('sid_token')
    if not sid_token:
        await update.effective_message.reply_text("❌ No active session.")
        return
    
    # fetch inbox based on the session id token
    url = f"https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id={mail_id}&sid_token={sid_token}"

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url)
            data = response.json()

            # check the raw data if needed:
            # print("🔍 RAW DATA:", data)

            # extract the mail body
            email_body = data.get('mail_body', 'No content.')
            email_subject = data.get('mail_subject', 'No subject')

            await update.effective_message.reply_text(
                f'📝 {email_subject}\n\n{email_body[:4000]}',
                parse_mode='HTML' # disable Markdown/HTML parsing because email HTML might break Telegram
            )
    except Exception as e:
        print(f'🔴 Error in /read: {e}')
        await update.effective_message.reply_text('⚠️ Error reading message.\nMake sure to include the message ID like this:\n/read <ID>!')


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

# Handles everything that is not a valid command
async def unknown_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # effective_message helper makes sure the code grabs the text object itself no matter if it's
    # a new message, and edit, or a channel post
    bad_command = update.effective_message.text
    await update.effective_message.reply_text(f'❌"{bad_command}" is not a valid command.\nType /help for a list of available commands')
    # prints the chat ID in the terminal for dev purposes
    print(f"🔵 Unknown command attempted by Chat ID: {update.effective_chat.id}")