import chess
import importlib

BOT1 = "my_bot"
BOT2 = "bot_random"

def load_bot(name):
    return importlib.import_module(name)

def get_move(bot, fen):
    try:
        return bot.next_move(fen)
    except:
        return None

def main():
    board = chess.Board()
    turn = 0

    bot1 = load_bot(BOT1)
    bot2 = load_bot(BOT2)

    print(f"\nMatch: {BOT1} vs {BOT2}\n")

    while not board.is_game_over():
        fen = board.fen()

        current_bot = bot1 if turn == 0 else bot2
        name = BOT1 if turn == 0 else BOT2

        move = get_move(current_bot, fen)

        print(f"{name} played:", move)

        if move is None:
            print(f"{name} failed.")
            break

        try:
            move_obj = chess.Move.from_uci(move)
        except:
            print("Invalid move:", move)
            break

        if move_obj not in board.legal_moves:
            print("Illegal move:", move)
            break

        board.push(move_obj)
        print(board, "\n")

        turn = 1 - turn

    print("Game Over:", board.result())

if __name__ == "__main__":
    main()
