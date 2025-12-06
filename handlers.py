import html
import httpx # if using requests instead, the bot would handle one request at a time only
import asyncio # this is necessary for sleep, wait, and gather tools
import os
import re
from telegram import Update
from telegram.ext import ContextTypes

# scripts
import db

# disguise the request to the API
# this tells the server: "I am Chrome on Windows, trust me."
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

## == STARTS THE BOT == ##
# no need to import AsyncIO module since ApplicationBuilder is built on top of async  
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    db.add_user(user.id, user.username)
    await update.effective_message.reply_text('System is online!\nAwaiting instructions...\nType /help for a list of commands.')

## == LISTS COMMANDS == ##
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = '''
    Available commands:
    /start => starts the bot
    /help => lists commands
    /tempmail => creates temporary email
    /checkmail => checks temporary email inbox
    /read <id> => reads the temporary email
    /dispose => deletes the temporaty email
    /broadcast <msg> (Admin Only)
    '''
    await update.effective_message.reply_text(help_text)

## == CREATES TEMP EMAIL == ##
async def tempmail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # GUERRILLA MAIL API ENDPOINT
    url = "https://api.guerrillamail.com/ajax.php?f=get_email_address"

    try:
        # httpx does not follow redirects by default
        # follow_redirects=True is necessary so it
        # doesn't stop after a 301 Redirect
        async with httpx.AsyncClient(follow_redirects=True, headers=HEADERS) as client:
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


## == CHECKS INBOX == ##
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
        async with httpx.AsyncClient(follow_redirects=True, headers=HEADERS) as client:
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


## == READS MESSAGE BODY == ##
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
        async with httpx.AsyncClient(follow_redirects=True, headers=HEADERS) as client:
            response = await client.get(url)
            data = response.json()

            # check the raw data if needed:
            # print("🔍 RAW DATA:", data)

            # extract the mail body
            email_body = data.get('mail_body', 'No content.')
            email_subject = data.get('mail_subject', 'No subject')
            
            # THIS IS IMPORTANT TO FILTER DOWN HTML TAGS 
            # OTHERWISE THAT WOULD RETURN A READING ERROR

            # simple replace for some tags
            temp_body = email_body.replace('<br>', '\n').replace('<br/>', '\n').replace('</p>', '\n')

            # regex to strip ALL remaining HTML tags (<div..., <span..., etc.)
            clean_body = re.sub('<[^<]+?>', '', temp_body)

            # escape special characters (e.g. if email contains "x < y", Telegram breaks without this)
            safe_body = html.escape(clean_body)
            safe_subject = html.escape(email_subject)

            # wrap the email body in <pre> ... </pre> to get a pre-formatted text with a dark background look for the email body
            # :4000 makes sure the response does not surpass the Telegram's 4096 character limit per message
            final_message = f'<b>📝 {safe_subject}</b>\n\n<pre>{safe_body[:4000]}</pre>'

            await update.effective_message.reply_text(
                
                # safe to use raw HTML parsing here because the bad HTML tags were cleaned with regex, otherwise it'd return an error in some cases since Telegram cannot correctly process some tags such as <br>, <span>, etc. Without regex, just use parse_mode=None
                final_message,
                parse_mode='HTML'
            )
    except Exception as e:
        print(f'🔴 Error in /read: {e}')
        await update.effective_message.reply_text('⚠️ Error reading message.\nMake sure to include the message ID like this:\n/read <ID>!')

## == DELETES TEMP EMAIL == ##
async def dispose(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # get current data
    sid_token = context.user_data.get('sid_token')
    email_address = context.user_data.get('temp_email')

    if not sid_token:
        await update.effective_message.reply_text("❌ You don't have an active session to dispose.")
        return

    # call GuerrillaMail to destroy it on server
    url = f"https://api.guerrillamail.com/ajax.php?f=forget_me&email_addr={email_address}&sid_token={sid_token}"

    try:
        # use HEADERS just in case
        async with httpx.AsyncClient(follow_redirects=True, headers=HEADERS) as client:
            await client.get(url) # we don't really care about the response, just that we sent it.
            
            # CLEAR LOCAL MEMORY
            # This wipes the data for this user
            context.user_data.clear()
            
            await update.effective_message.reply_text(
                f"🗑️ **Identity Destroyed**\n"
                f"The address `{email_address}` has been disposed.\n"
                f"Type /tempmail to generate a fresh identity.",
                parse_mode='Markdown'
            )

    except Exception as e:
        print(f"🔴 Error in /dispose: {e}")
        await update.effective_message.reply_text("⚠️ Error disposing email.")

## == SENDS MESSAGE TO ALL USERS (Admin Only) == ##
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # get update.effective_user.id and compare to MY_CHAT_ID from .env
    # if they don't match, reply "⛔ Access Denied." and return
    # check if they typed a message with len(context.args) > 0

    admin_id = int(os.getenv('MY_CHAT_ID'))
    sender_id = update.effective_user.id
    
    # security check
    if sender_id != admin_id:
        await update.effective_message.reply_text('⛔ Access Denied.')
        return
    
    # validation to check if the message is empty
    if len(context.args) == 0:
        await update.effective_message.reply_text('Usage: /broadcast <message>')
        return
    
    message = ' '.join(context.args)
    all_users = db.get_all_users()

    await update.effective_message.reply_text(f'📢 Broadcasting to {len(all_users)} users...')

    for user_id in all_users:
        try:
            # sends message to each user_id from the db
            await context.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            # if a user blocked the bot, this prevents the loop from breaking
            print(f'Failed to send to {user_id}: {e}')

    await update.effective_message.reply_text('✅ Broadcast complete.')


## == HANDLES INVALID COMMANDS == ##
async def unknown_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # effective_message helper makes sure the code grabs the text object itself no matter if it's
    # a new message, and edit, or a channel post
    bad_command = update.effective_message.text
    await update.effective_message.reply_text(f'❌"{bad_command}" is not a valid command.\nType /help for a list of available commands')
    # prints the chat ID in the terminal for dev purposes
    print(f"🔵 Unknown command attempted by Chat ID: {update.effective_chat.id}")