from move import Move, target, source
from board import (
    make_board,
    white,
    black,
    legal_moves,
    white_plays,
    move,
    is_game_over,
    copy,
    is_legal,
    Board,
)
from js import document  # type: ignore
from pyscript import when  # type: ignore
from js import Peer

history: list[Board]
board: Board
legal_moves_var: list[Move]
black_pieces: list[int]
white_pieces: list[int]
is_white: bool
clicked: int | None

result_element = document.getElementById("result")
result_text_element = document.getElementById("result-text")
undo_element = document.getElementById("control-undo")
menu_element = document.getElementById("menu")
game_element = document.getElementById("game")
overlay_element = document.getElementById("overlay")

CLASS_CELL = "cell"
CLASS_CELL_BLACK = "cell-black"
CLASS_CELL_WHITE = "cell-white"
CLASS_CELL_POSSIBLE = "cell-possible-moves"
CLASS_CELL_CLICKED = "cell-clicked"
CLASS_HIDDEN = "hidden"


def display_result() -> None:
    overlay_element.style.visibility = "visible"
    result_element.style.visibility = "visible"


def hide_result() -> None:
    overlay_element.style.visibility = "hidden"
    result_element.style.visibility = "hidden"


def display_menu() -> None:
    menu_element.style.visibility = "visible"
    game_element.style.visibility = "hidden"


def display_game() -> None:
    menu_element.style.visibility = "hidden"
    game_element.style.visibility = "visible"


def cell_set(id, class_type) -> None:
    document.getElementById(id).classList = f"{CLASS_CELL} {class_type}"


def draw_board(
    white: list[int], black: list[int], clicked: int, possible_moves: list[Move]
) -> None:
    for i in range(1, 26):
        cell_set(i, CLASS_HIDDEN)
    for i in white:
        cell_set(i, CLASS_CELL_WHITE)
    for i in black:
        cell_set(i, CLASS_CELL_BLACK)
    for m in possible_moves:
        cell_set(target(m), CLASS_CELL_POSSIBLE)
    if clicked is not None:
        cell_set(clicked, CLASS_CELL_CLICKED)


def possible_moves(legal_moves_var: list[Move], clicked: int) -> list[Move]:
    if clicked is None:
        return []
    else:
        return [m for m in legal_moves_var if source(m) == clicked]


@when("click", "#play-offline")  # button-restart
def setup_offline() -> None:
    global history, board, legal_moves_var, black_pieces, white_pieces, is_white, clicked

    history = []
    board = make_board()
    legal_moves_var = legal_moves(board)
    black_pieces = black(board)
    white_pieces = white(board)
    is_white = white_plays(board)
    clicked = None
    undo_element.disabled = True
    display_game()

    draw_board(white_pieces, black_pieces, clicked, [])


@when("click", ".undo")
def undo() -> None:
    global history, board, legal_moves_var, black_pieces, white_pieces, is_white, clicked
    if len(history) > 0:
        board = history.pop()
        legal_moves_var = legal_moves(board)
        black_pieces = black(board)
        white_pieces = white(board)
        is_white = white_plays(board)
        clicked = None
        draw_board(white_pieces, black_pieces, clicked, [])

    if len(history) == 0:
        undo_element.disabled = True
    else:
        undo_element.disabled = False


@when("click", ".cell")
def click_handler(event) -> None:
    global history, clicked, board, legal_moves_var, black_pieces, white_pieces, is_white
    id: int = int(event.srcElement.id)
    if clicked:
        m = Move(clicked, id)
        if is_legal(m, board):
            history.append(copy(board))
            undo_element.disabled = False
            move(m, board)

            legal_moves_var = legal_moves(board)
            black_pieces = black(board)
            white_pieces = white(board)
            is_white = white_plays(board)
            clicked = None

            if is_game_over(board):
                if not black_pieces:
                    result_text_element.textContent = "White wins!"
                elif not white_pieces:
                    result_text_element.textContent = "Black wins!"
                else:
                    result_text_element.textContent = "Draw!"
                display_result()

        elif (is_white and id in white_pieces) or (not is_white and id in black_pieces):
            clicked = id
        else:
            clicked = None
    elif (is_white and id in white_pieces) or (not is_white and id in black_pieces):
        clicked = id
    else:
        clicked = None

    draw_board(
        white_pieces, black_pieces, clicked, possible_moves(legal_moves_var, clicked)
    )
