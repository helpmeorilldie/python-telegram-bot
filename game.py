from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def create_board():
    """Create an empty 3x3 board."""
    return [["⬜" for _ in range(3)] for _ in range(3)]


def board_keyboard(board):
    """Convert the board into an inline keyboard."""
    keyboard = []

    for i in range(3):
        row = []
        for j in range(3):
            row.append(
                InlineKeyboardButton(
                    board[i][j],
                    callback_data=f"{i},{j}"
                )
            )
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


def check_winner(board):
    """Return ❌ or ⭕ if there's a winner, otherwise None."""

    # Rows
    for row in board:
        if row[0] != "⬜" and row[0] == row[1] == row[2]:
            return row[0]

    # Columns
    for col in range(3):
        if (
            board[0][col] != "⬜"
            and board[0][col] == board[1][col] == board[2][col]
        ):
            return board[0][col]

    # Main diagonal
    if (
        board[0][0] != "⬜"
        and board[0][0] == board[1][1] == board[2][2]
    ):
        return board[0][0]

    # Anti-diagonal
    if (
        board[0][2] != "⬜"
        and board[0][2] == board[1][1] == board[2][0]
    ):
        return board[0][2]

    return None


def board_full(board):
    """Return True if no empty cells remain."""
    for row in board:
        if "⬜" in row:
            return False
    return True
