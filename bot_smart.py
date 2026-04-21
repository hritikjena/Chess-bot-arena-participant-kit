import chess

piece_value = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

# ---------------- EVALUATION ---------------- #

def evaluate(board):

    # checkmate = highest priority
    if board.is_checkmate():
        return -10000 if board.turn else 10000

    # draw situations
    if (board.is_stalemate() or 
        board.is_insufficient_material() or 
        board.can_claim_fifty_moves()):
        return 0

    # discourage repetition
    if board.can_claim_threefold_repetition():
        return -100

    score = 0

    # material
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_value[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value

    # check pressure (fixed logic)
    if board.is_check():
        if board.turn == chess.WHITE:
            score -= 2
        else:
            score += 2

    return score


# ---------------- MINIMAX ---------------- #

def minimax(board, depth, maximizing):

    if depth == 0 or board.is_game_over():
        return evaluate(board)

    if maximizing:
        max_eval = -9999

        for move in board.legal_moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, False)
            board.pop()
            max_eval = max(max_eval, eval_score)

        return max_eval

    else:
        min_eval = 9999

        for move in board.legal_moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, True)
            board.pop()
            min_eval = min(min_eval, eval_score)

        return min_eval


# ---------------- MAIN MOVE ---------------- #

def next_move(fen):
    board = chess.Board(fen)

    best_move = None
    best_score = -9999 if board.turn == chess.WHITE else 9999

    for move in board.legal_moves:
        board.push(move)

        # minimax depth 2
        score = minimax(board, 2, board.turn == chess.BLACK)

        # mobility (optimized)
        mobility = board.legal_moves.count()
        score += mobility * 0.05

        board.pop()

        if board.turn == chess.WHITE:
            if score > best_score:
                best_score = score
                best_move = move
        else:
            if score < best_score:
                best_score = score
                best_move = move

    return str(best_move)