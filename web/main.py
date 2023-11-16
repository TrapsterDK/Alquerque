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
from js import document, Peer  # type: ignore
from pyscript import when  # type: ignore

# from pyodide.ffi import create_proxy  # type: ignore

# peer = Peer.new()
# peer.on("open", create_proxy(lambda id: print("My peer ID is: " + id)))


CIRCLE_RADIUS_PERCENTAGE = 0.4
CLASS_CELL = "cell"
CLASS_CELL_BLACK = "cell-black"
CLASS_CELL_WHITE = "cell-white"
CLASS_CELL_POSSIBLE = "cell-possible-moves"
CLASS_CELL_CLICKED = "cell-clicked"
CLASS_HIDDEN = "hidden"

result_element = document.getElementById("result")
result_text_element = document.getElementById("result-text")
control_undo_element = document.getElementById("control-undo")
menu_element = document.getElementById("menu")
game_element = document.getElementById("game")
overlay_element = document.getElementById("overlay")
board_svg_element = document.getElementById("board-svg")
board_cells_element = document.getElementById("board-cells")

history: list[Board]
board: Board
legal_moves_var: list[Move]
black_pieces: list[int]
white_pieces: list[int]
is_white: bool
clicked: int | None


def draw_line(fx: int, fy: int, tx: int, ty: int, spacing: float) -> None:
    line = f"<line x1='{fx * spacing + spacing / 2}' y1='{fy * spacing + spacing / 2}' x2='{tx * spacing + spacing / 2}' y2='{ty * spacing + spacing / 2}' />"

    board_svg_element.innerHTML += line


def draw_circle(x: int, y: int, spacing: int, radius: int) -> None:
    circle = f"<circle cx='{x * spacing + spacing / 2}' cy='{y * spacing + spacing / 2}' r='{radius}' />"

    board_svg_element.innerHTML += circle


def add_board_svg() -> None:
    board_svg_element.innerHTML = ""
    board_size = board_svg_element.clientWidth
    circle_spacing = board_size / 5
    circle_radius = (circle_spacing / 2) * CIRCLE_RADIUS_PERCENTAGE

    # draw circles
    for x in range(5):
        for y in range(5):
            draw_circle(x, y, circle_spacing, circle_radius)

    # vertical
    draw_line(0, 0, 0, 4, circle_spacing)
    draw_line(1, 0, 1, 4, circle_spacing)
    draw_line(2, 0, 2, 4, circle_spacing)
    draw_line(3, 0, 3, 4, circle_spacing)
    draw_line(4, 0, 4, 4, circle_spacing)

    # horizontal
    draw_line(0, 0, 4, 0, circle_spacing)
    draw_line(0, 1, 4, 1, circle_spacing)
    draw_line(0, 2, 4, 2, circle_spacing)
    draw_line(0, 3, 4, 3, circle_spacing)
    draw_line(0, 4, 4, 4, circle_spacing)

    # diagonals
    draw_line(0, 0, 4, 4, circle_spacing)
    draw_line(0, 4, 4, 0, circle_spacing)

    # short diagonals
    draw_line(2, 0, 4, 2, circle_spacing)
    draw_line(0, 2, 2, 0, circle_spacing)
    draw_line(0, 2, 2, 4, circle_spacing)
    draw_line(2, 4, 4, 2, circle_spacing)


def add_board_cells() -> None:
    piece = document.createElement("div")
    piece.classList.add("cell")

    for i in range(1, 26):
        addpiece = piece.cloneNode(False)
        addpiece.id = i
        board_cells_element.appendChild(addpiece)


add_board_svg()
add_board_cells()


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


def cell_set(id: int, class_type: str) -> None:
    document.getElementById(id).classList = f"{CLASS_CELL} {class_type}"


def possible_moves(legal_moves_var: list[Move], clicked: int) -> list[Move]:
    if clicked is None:
        return []
    else:
        return [m for m in legal_moves_var if source(m) == clicked]


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
    control_undo_element.disabled = True
    display_game()

    draw_board(white_pieces, black_pieces, clicked, [])


@when("click", ".button-undo")
def click_button_undo(event) -> None:
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
        control_undo_element.disabled = True
    else:
        control_undo_element.disabled = False


@when("click", ".cell")
def click_cell(event) -> None:
    global history, clicked, board, legal_moves_var, black_pieces, white_pieces, is_white
    id: int = int(event.srcElement.id)
    if clicked and is_legal(Move(clicked, id), board):
        history.append(copy(board))
        control_undo_element.disabled = False
        move(Move(clicked, id), board)

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

    draw_board(
        white_pieces, black_pieces, clicked, possible_moves(legal_moves_var, clicked)
    )


@when("click", ".button-menu")
def click_button_menu(event):
    display_menu()


@when("resize", "window")
def resize_window(event):
    draw_board()
