# REMEMBER TO ADD ANY NEW COMMAND TO THE LIST INSIDE:
# post_init() in main.py

#TODO
# multilingual

import sqlite3
import html
import os
import re
from telegram import Update
from telegram.ext import ContextTypes

# scripts
import db
import service

## <-- NOTIFIES THE USER WHEN THEIR EMAIL IS EXPIRED/ABOUT TO EXPIRE --> ##
async def sixty_minutes_left(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.send_message(
        chat_id=job.chat_id,
        text="⏳ <b>Time Check:</b> Your temporary email will expire in <i><b>60 minutes.</b></i>",
        parse_mode='HTML'
    )

async def five_minutes_left(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.send_message(
        chat_id=job.chat_id,
        text="⏳ <b>Time Check:</b> Your temporary email will expire in <i><b>5 minutes.</b></i>",
        parse_mode='HTML'
    )

async def zero_minutes_left(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.send_message(
        chat_id = job.chat_id,
        text="🗑️ <b>Session Expired:</b> This temporary email address has been automatically disposed. Create another one with /tempmail.",
        parse_mode='HTML'
    )

## <-- STARTS THE BOT --> ##
# no need to import AsyncIO module since ApplicationBuilder is built on top of async
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    # adds user to db
    db.add_user(user.id, user.username)

    await update.effective_message.reply_text('🌐 <b>System is online!\n<i>Awaiting instructions...</i>\nType /help for a list of commands.</b>', parse_mode='HTML')

## <-- LISTS COMMANDS --> ##
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = '''
    🟢 <b>Available Commands:</b>

    /start
        └── 🚀 <i>starts the bot</i>

    /help
        └── ⌨️ <i>lists available commands</i>

    /tempmail
        └── 🛡️ <i>creates temporary email</i>

    /check
        └── 📬 <i>checks inbox</i>

    /read [message_id]
        └── 📜 <i>reads the chosen message by id</i>

    /dispose
        └── 🗑️ <i>deletes current identity</i>

    /broadcast [message]
        └── 📢 <i>Admin Only</i> 🔐
    
    /finduser [username]
        └── 🔎 <i>Admin Only</i> 🔐
    '''
    await update.effective_message.reply_text(help_text, parse_mode='HTML')

## <-- CREATES TEMP EMAIL --> ##
async def temp_mail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    identity = await service.create_email_identity()

    if not identity:
        await update.effective_message.reply_text('⚠️ API Error. Could not generate email')
        return

    # this are dict keys from create_email_identity()
    email_address = identity['email']
    sid_token = identity['sid_token']

    # save session ID (necessary for GuerrillaMail)
    context.user_data['temp_email'] = email_address
    context.user_data['sid_token'] = sid_token

    # scheduling the alarms
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # first alarm
    context.job_queue.run_once(
        sixty_minutes_left, 
        1, 
        chat_id=chat_id,
        name=f"{user_id}_first_warning" # Unique Name
    )

    # second alarm
    context.job_queue.run_once(
        five_minutes_left, 
        3300, 
        chat_id=chat_id,
        name=f"{user_id}_second_warning" # Unique Name
    )

    # third alarm
    context.job_queue.run_once(
        zero_minutes_left, 
        3600, 
        chat_id=chat_id,
        name=f"{user_id}_expired" # Unique Name
    )

    # session Log
    print(
        f'''
        ==DEBUG==
        🛡️ New Session created at:
        📧 Address: {email_address}
        🔑 Session ID: {sid_token}
        '''
    )

    await update.effective_message.reply_text(
        f'🛡️ <b>Privacy Shield Active (GuerrillaMail)</b>\n\n'
        f'📧 Address: <code>{email_address}</code>\n'
        '                               └── Click here to copy the email address!\n'
        f'<i>To see your inbox, type /check.</i>',
        parse_mode='HTML' # <code> allows copy-paste by clicking
    )


## <-- CHECKS INBOX --> ##
async def check_inbox(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # retrieve session id
    sid_token = context.user_data.get('sid_token')
    email_address = context.user_data.get('temp_email')

    if not sid_token:
        await update.effective_message.reply_text("❌ No active session. Type /tempmail first.")
        return

    messages = await service.fetch_inbox(sid_token)
    
    # guerrillamail usually sends a welcome email
            # so list is rarely empty
            # check if empty anyway just to make sure
    if not messages or len(messages) == 0:
        await update.effective_message.reply_text(f'📭 Inbox empty for {email_address}')
        return

    reply_text = f"📬 <b>Inbox for</b> {email_address}\n"
    # loop through messages
    # limit to 5 emails to avoid spamming chat
    for msg in messages[:5]: 
        msg_id = msg['mail_id']
        sender = msg['mail_from']
        subject = msg['mail_subject']
        reply_text += f'''
------------------------------------
🆔 Message ID: <code>{msg_id}</code>
👤 From: <code>{sender}</code>
📝 Subject: <b>{subject}</b>'''
                
    reply_text += '''
------------------------------------
<i>To read a message content, type /read [message_id]
e.g. /read 120931290</i>'''

    await update.effective_message.reply_text(reply_text, parse_mode='HTML') # <code> allows copy-paste by clicking


## <-- READS MESSAGE BODY --> ##
async def read_mail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # check if the user typed an id
    if len(context.args) == 0:
        await update.effective_message.reply_text('Usage: /read [message_id]')
        return

    mail_id = context.args[0]

    # check if the session is active
    sid_token = context.user_data.get('sid_token')
    if not sid_token:
        await update.effective_message.reply_text("❌ No active session. Type /tempmail first.")
        return
    
    data = await service.fetch_email_content(mail_id, sid_token)

    if not data:
        await update.effective_message.reply_text('⚠️ Error reading message. Check the Message ID.')
        return

    # extract the mail body
    email_body = data.get('mail_body', 'No content.')
    email_subject = data.get('mail_subject', 'No subject')
    mail_from = data.get('mail_from', 'No address')
    
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
    final_message = f'📤 Opening message from: <code>{mail_from}</code>\n\n📝 Subject: <b>{safe_subject}</b>\n\n<pre>{safe_body[:4000]}</pre>'

    await update.effective_message.reply_text(
        # safe to use raw HTML parsing here because the bad HTML tags were cleaned with regex, otherwise it'd return an error in some cases since Telegram cannot correctly process some tags such as <br>, <h1>, <span>, etc. Without regex, just use parse_mode=None
        final_message,
        parse_mode='HTML'
    )

## <-- DELETES TEMPORARY EMAIL ADDRESS --> ##
async def dispose(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # get current data
    sid_token = context.user_data.get('sid_token')
    email_address = context.user_data.get('temp_email')

    if not sid_token:
        await update.effective_message.reply_text("❌ You don't have an active session to dispose.")
        return

    success = await service.destroy_identity(sid_token, email_address)

    if success:
        # --- KILL THE TIMERS TO AVOID PHANTOM NOTIFICATIONS ---
        user_id = str(update.effective_user.id)

        # cancel jobs
        jobs_to_cancel = (
            context.job_queue.get_jobs_by_name(f'{user_id}_first_warning') +
            context.job_queue.get_jobs_by_name(f'{user_id}_second_warning') +
            context.job_queue.get_jobs_by_name(f'{user_id}_expired')
        )
        
        for job in jobs_to_cancel:
            job.schedule_removal() # Stop the countdown

        # CLEAR LOCAL MEMORY
        # This wipes the data for this user
        context.user_data.clear()
        
        await update.effective_message.reply_text(
            f'🗑️ <b>Identity Destroyed!</b>\n'
            f'The address <code>{email_address}</code> has been disposed.\n'
            f'<i>Type /tempmail to generate a fresh identity.</i>',
            parse_mode='HTML'
        )

    else:
        await update.effective_message.reply_text("⚠️ Error disposing email. API might be down")

## <-- SENDS MESSAGE TO ALL USERS (Admin Only) --> ##
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
    
    # check if the message is empty
    if len(context.args) == 0:
        await update.effective_message.reply_text('Usage: /broadcast [message]')
        return
    
    message = ' '.join(context.args)
    all_users = db.get_all_users()

    await update.effective_message.reply_text(f'📢 <b>Broadcasting to {len(all_users)} users...</b>', parse_mode='HTML')

    for user_id in all_users:
        try:
            # sends message to each user_id from the db
            await context.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            # if a user blocked the bot, this prevents the loop from breaking
            print(f'Failed to send to {user_id}: {e}')

    await update.effective_message.reply_text('✅ <i>Broadcast complete.</i>', parse_mode='HTML')

## <-- FETCHES USER_ID BY TELEGRAM USERNAME (Admin Only) --> ##
async def find_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # pretty much what check_db.py does but as a command

    admin_id = int(os.getenv('MY_CHAT_ID'))
    sender_id = update.effective_user.id
    
    # security check
    if sender_id != admin_id:
        await update.effective_message.reply_text('⛔ Access Denied.')
        return
    
    # check if the message is empty
    if len(context.args) == 0:
        await update.effective_message.reply_text('Usage: /find_user [username]')
        return
    
    # first thing written after /finduser will be taken as username
    target_username = context.args[0]
    
    with sqlite3.connect('bot.db') as conn:
        cursor = conn.cursor()
        # SQL 'LIKE' operator with % wildcards
        # %john% means 'it doesn't matter what comes' 
        # before or after 'john', return it anyway
        # searching for 'john' will find 'john_doe', 'big_john', etc. 
        cursor.execute(
            '''
                SELECT * FROM users
                WHERE username LIKE ?
            ''',
        (f'%{target_username}%',)) 
        # this comma means it's a tuple with one item
        # ('target_username',) <= tuple
        # ('target_username') <= string inside parentheses
        # so it plugs '?' to target_username as a whole word
        # instead of treating every letter as a separate parameter

        rows = cursor.fetchall()

    if not rows:
        await update.effective_message.reply_text(f"❌ No users found matching '<i>{target_username}</i>'", parse_mode='HTML')
        return

    # format output
    reply_text = f'<b>🔎 Found {len(rows)} match(es):</b>\n\n'

    for row in rows:
        # read the init_db() from db.py to check the columns
        user_id = row[0]
        username = row[1]

        reply_text += f'🆔 <code>{user_id}</code> | 👤 @{username}\n'
 
    await update.effective_message.reply_text(reply_text, parse_mode='HTML')

## <-- HANDLES INVALID COMMANDS --> ##
async def unknown_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # effective_message helper makes sure the code grabs the text object itself no matter if it's
    # a new message, and edit, or a channel post
    bad_command = update.effective_message.text
    await update.effective_message.reply_text(f'❌"{bad_command}" is not a valid command.\nType /help for a list of available commands')
    # prints the chat ID in the terminal for dev purposes (use /foo or anything that is not a valid command)
    print(f"🔵 Unknown command attempted by Chat ID: {update.effective_chat.id}")