import logging
import os
from datetime import datetime

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("8603510237:AAFni5_cboiPIuZIR2RD6mm9RU5vsrRlCZA")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# -------------------------
# COMMANDS
# -------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Hello {update.effective_user.first_name}!\n"
        "Use /help to see commands."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
Available Commands

/start
/help
/ping
/id
/user
/chat
/time
/echo <text>
/about
/buttons
/photo
/typing
/dice
"""
    await update.message.reply_text(text)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong!")


async def user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user

    await update.message.reply_text(
        f"""
ID: {u.id}
Name: {u.full_name}
Username: @{u.username}
Language: {u.language_code}
"""
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = update.effective_chat

    await update.message.reply_text(
        f"""
Chat ID: {c.id}
Title: {c.title}
Type: {c.type}
"""
    )


async def user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(str(update.effective_user.id))


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        await update.message.reply_text(" ".join(context.args))
    else:
        await update.message.reply_text("Usage:\n/echo Hello")


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Python Telegram Bot Template\nVersion 1.0"
    )


async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(now)


async def typing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(
        update.effective_chat.id,
        ChatAction.TYPING
    )

    await update.message.reply_text("Done!")


async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_dice(update.effective_chat.id)


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        "https://picsum.photos/600/400",
        caption="Random Photo"
    )


# -------------------------
# INLINE BUTTONS
# -------------------------

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Google", url="https://google.com")
        ],
        [
            InlineKeyboardButton("Click Me", callback_data="clicked")
        ]
    ]

    await update.message.reply_text(
        "Buttons:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    await query.edit_message_text(
        "✅ Button clicked!"
    )


# -------------------------
# MESSAGE HANDLER
# -------------------------

async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"You said:\n{update.message.text}"
    )


# -------------------------
# UNKNOWN COMMAND
# -------------------------

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Unknown command.")


# -------------------------
# MAIN
# -------------------------

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("id", user_id))
    app.add_handler(CommandHandler("user", user))
    app.add_handler(CommandHandler("chat", chat))
    app.add_handler(CommandHandler("echo", echo))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("time", time))
    app.add_handler(CommandHandler("typing", typing))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("photo", photo))
    app.add_handler(CommandHandler("buttons", buttons))

    app.add_handler(CallbackQueryHandler(button_callback))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text)
    )

    app.add_handler(
        MessageHandler(filters.COMMAND, unknown)
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
