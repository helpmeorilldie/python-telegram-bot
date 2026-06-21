import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from game import (
    create_board,
    board_keyboard,
    check_winner,
    board_full,
)

TOKEN = os.getenv("BOT_TOKEN")

games = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 New Game", callback_data="new")]
    ]

    await update.message.reply_text(
        "🎮 Tic Tac Toe\n\nPress New Game!",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user.id

    if query.data == "new":
        board = create_board()

        games[user] = {
            "board": board,
            "turn": "❌",
        }

        await query.edit_message_text(
            "Turn: ❌",
            reply_markup=board_keyboard(board),
        )
        return

    game = games.get(user)

    if game is None:
        await query.answer("Start a new game!", show_alert=True)
        return

    row, col = map(int, query.data.split(","))

    board = game["board"]

    if board[row][col] != "⬜":
        return

    board[row][col] = game["turn"]

    winner = check_winner(board)

    if winner:
        await query.edit_message_text(
            f"🏆 {winner} Wins!",
            reply_markup=board_keyboard(board),
        )
        del games[user]
        return

    if board_full(board):
        await query.edit_message_text(
            "🤝 Draw!",
            reply_markup=board_keyboard(board),
        )
        del games[user]
        return

    game["turn"] = "⭕" if game["turn"] == "❌" else "❌"

    await query.edit_message_text(
        f"Turn: {game['turn']}",
        reply_markup=board_keyboard(board),
    )


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable is not set.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    print("Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
