import chess
import importlib
import multiprocessing

BOT1 = "my_bot"
BOT2 = "bot_random"

MAX_MOVES = 100
TIME_LIMIT = 4


def worker(bot_name, fen, queue):
    try:
        module = importlib.import_module(bot_name)
        move = module.next_move(fen)
        queue.put(move)
    except:
        queue.put(None)


def get_safe_move(bot_name, fen):
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=worker, args=(bot_name, fen, queue))

    p.start()
    p.join(TIME_LIMIT)

    if p.is_alive():
        p.terminate()
        p.join()
        return None, "timeout"

    if not queue.empty():
        return queue.get(), None

    return None, "error"


def main():
    board = chess.Board()
    turn = 0
    move_count = 0

    print(f"\nMatch: {BOT1} vs {BOT2}\n")

    reason = "Unknown"

    while not board.is_game_over():

        fen = board.fen()
        current_bot = BOT1 if turn == 0 else BOT2
        name = current_bot

        move, error = get_safe_move(current_bot, fen)

        print(f"{name} played:", move)

        if move is None:
            reason = f"{name} failed ({error})"
            break

        try:
            move_obj = chess.Move.from_uci(move)
        except:
            reason = "Invalid move format"
            break

        if move_obj not in board.legal_moves:
            reason = "Illegal move"
            break

        board.push(move_obj)

        move_count += 1
        print(f"Move {move_count}")
        print(board, "\n")

        if move_count >= MAX_MOVES:
            reason = "Move limit"
            break

        turn = 1 - turn

    print("\nGame Over")

    if board.is_checkmate():
        print("Result:", board.result())
        print("Reason: Checkmate")

    elif board.is_stalemate():
        print("Result: 1/2-1/2")
        print("Reason: Stalemate")

    elif board.is_insufficient_material():
        print("Result: 1/2-1/2")
        print("Reason: Insufficient Material")

    elif board.can_claim_threefold_repetition():
        print("Result: 1/2-1/2")
        print("Reason: Threefold Repetition")

    elif board.can_claim_fifty_moves():
        print("Result: 1/2-1/2")
        print("Reason: 50-Move Rule")

    elif reason == "Move limit":
        print("Result: 1/2-1/2")
        print("Reason: Move Limit Reached")

    else:
        print("Result: *")
        print("Reason:", reason)


if __name__ == "__main__":
    main()
