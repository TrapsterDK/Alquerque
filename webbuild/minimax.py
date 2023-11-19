from board import (
    Board,
    legal_moves,
    is_game_over,
    copy,
    move,
    white,
    black,
    white_plays,
)
from move import Move


def evaluate(board: Board) -> float:
    """Evaluates the board."""
    if white(board) == 0:
        return -float("inf")
    if black(board) == 0:
        return float("inf")
    if is_game_over(board):
        return 0

    white_pieces = len(white(board))
    black_pieces = len(black(board))

    # Adjust values based on piece values and board control
    score = white_pieces - black_pieces
    return score


def negamax(board: Board, depth: int, alpha, beta, player) -> float:
    if depth == 0 or is_game_over(board):
        return evaluate(board)

    score = float("-inf")
    for m in legal_moves(board):
        new_board = copy(board)
        move(m, new_board)
        score = max(score, -negamax(new_board, depth - 1, -beta, -alpha, -player))
        alpha = max(alpha, score)
        if alpha >= beta:
            break

    print(f"Score: {score}")
    return score


def next_move(b: Board, depth: int = 5) -> Move:
    """Returns the best move for the given board and depth."""
    best_score = float("-inf")
    best_move = None
    for m in legal_moves(b):
        new_board = copy(b)
        move(m, new_board)
        score = -negamax(
            new_board,
            depth - 1,
            float("-inf"),
            float("inf"),
            1,
        )
        if score > best_score:
            best_score = score
            best_move = m

    print(f"Best move: {best_move} with score {best_score}")
    return best_move
