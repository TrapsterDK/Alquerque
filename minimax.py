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
    """Evaluates the board.

    Args:
        board (Board): Board object to evaluate.

    Returns:
        int: Score of the board.
    """

    # black wins
    if white(board) == 0:
        return -float("inf")
    # white wins
    if black(board) == 0:
        return float("inf")

    score = 0
    score += len(white(board)) - len(black(board))
    return score


def minimax_alpha_beta(
    board: Board, depth: int, alpha: int, beta: int, maximizing_player: bool
) -> int:
    """Minimax algorithm with alpha-beta pruning.

    Args:
        board (Board): Board object to evaluate.
        depth (int): Eepth of the search tree.
        alpha (int): Alpha value.
        beta (int): Beta value.
        maximizing_player (bool): True if maximizing player, False if minimizing player.

    Returns:
        int: Best score.
    """
    if depth == 0 or is_game_over(board):
        return evaluate(board)

    if maximizing_player:
        best_score = -float("inf")
        for m in legal_moves(board):
            board_copy = copy(board)
            move(m, board_copy)
            score = minimax_alpha_beta(board_copy, depth - 1, alpha, beta, False)
            best_score = max(best_score, score)
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        return best_score
    else:
        best_score = float("inf")
        for m in legal_moves(board):
            board_copy = copy(board)
            move(m, board_copy)
            score = minimax_alpha_beta(board_copy, depth - 1, alpha, beta, True)
            best_score = min(best_score, score)
            beta = min(beta, score)
            if alpha >= beta:
                break
        return best_score


def next_move(b: Board, n: int = 7) -> Move:
    """Returns the next move for the autoplayer."""
    return max(
        legal_moves(b),
        key=lambda m: minimax_alpha_beta(
            b, n, -float("inf"), float("inf"), white_plays(b)
        ),
    )
