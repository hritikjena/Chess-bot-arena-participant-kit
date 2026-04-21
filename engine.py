#scores
import chess  

piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 100
}


import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import multiprocessing
import requests

API_URL = "https://chess-contest-api.tanubhavj.workers.dev/matches"

#SAFE BOT EXECUTION

def worker(bot_name, fen, queue):
    try:
        module = __import__(bot_name, fromlist=[''])
        move = module.next_move(fen)
        queue.put(move)
    except Exception as e:
        print(f"[ERROR in {bot_name}]:", e)
        queue.put(None)


def get_safe_move(bot_name, fen):
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=worker, args=(bot_name, fen, queue))

    p.start()
    p.join(4)

    if p.is_alive():
        print(f"{bot_name} timed out.")
        p.terminate()
        return None

    if not queue.empty():
        return queue.get()

    return None


# SEND TO API FUNCTION

def send_match_to_server(data):
    try:
        response = requests.post(API_URL, json=data)
        print("Server Response:", response.status_code, response.text)
    except Exception as e:
        print("Failed to send data:", e)


# MAIN GAME LOOP

def main():
    move_count = 0
    MAX_MOVES = 80

    board = chess.Board()
    turn = 0

    bot1 = "bot_random"
    bot2 = "bot_smart"

    print(f"\nMatch: {bot1} vs {bot2}\n")

    moves_data = []
    move_number = 1

    score_p1 = 0   
    score_p2 = 0   

    while not board.is_game_over():

        fen_before = board.fen()

        current_bot = bot1 if turn == 0 else bot2
        move = get_safe_move(f"Bots.{current_bot}", fen_before)

        print(f"{current_bot} played:", move)

        if move is None:
            print(f"{current_bot} failed to move.")
            break

        try:
            move_obj = chess.Move.from_uci(move)
        except:
            print("Invalid format:", move)
            break

        if move_obj not in board.legal_moves:
            print("Illegal move:", move)
            break
        
        # capture detection
        captured_piece = board.piece_at(move_obj.to_square)
        points = 0

        if captured_piece:
            points = piece_values[captured_piece.piece_type]

        if board.is_en_passant(move_obj):  
            points = piece_values[chess.PAWN]

        san = board.san(move_obj)

        board.push(move_obj)

        # update scores
        if turn == 0:
            score_p1 += points
        else:
            score_p2 += points

        moves_data.append({
            "moveNumber": move_number,
            "player": "white" if turn == 0 else "black",
            "san": san,
            "fen": board.fen(),
            "pointsEarned": points   # fixed (was always 1)
        })

        print(f"Move {move_count + 1}: {san} (+{points})\n")

        if turn == 1:
            move_number += 1

        move_count += 1

        if move_count >= MAX_MOVES:
            print("Move limit reached → Draw")
            break

        turn = 1 - turn

    #RESULT

    print("\nGame Over")
    result = board.result()
    print("Result:", result)

    if result == "1-0":
        winner = bot1
    elif result == "0-1":
        winner = bot2
    else:
        winner = "Draw"

    #if move limit reached, determine winner by score
    if move_count >= MAX_MOVES:
        if score_p1 > score_p2:
            winner = bot1
        elif score_p2 > score_p1:
            winner = bot2
        else:
            winner = "Draw"

    #SEND DATA

    match_payload = {
        "player1": bot1,
        "player2": bot2,
        "winner": winner,
        "finalPointsP1": score_p1,
        "finalPointsP2": score_p2,
        "round": "Test",
        "moves": moves_data
    }

    print("\nSending match to server...")
    send_match_to_server(match_payload)

# ENTRY 

if __name__ == "__main__":
    main()