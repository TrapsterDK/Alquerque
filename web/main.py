from typing import Any
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
from observablelist import ObservableList
from js import window, document, Peer  # type: ignore
from pyscript import when  # type: ignore
from pyodide.ffi import create_proxy  # type: ignore

# peer = Peer.new()
# peer.on("open", create_proxy(lambda id: print("My peer ID is: " + id)))


CIRCLE_RADIUS_PERCENTAGE = 0.42
BOARD_WIDTH = 5
CLASS_CELL = "cell"
CLASS_CELL_BLACK = "cell-black"
CLASS_CELL_WHITE = "cell-white"
CLASS_CELL_POSSIBLE = "cell-possible-moves"
CLASS_CELL_OLD = "cell-old-move"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"

result_element = document.getElementById("result")
result_text_element = document.getElementById("result-text")
control_undo_element = document.getElementById("control-undo")
menu_element = document.getElementById("menu")
game_element = document.getElementById("game")
board_svg_element = document.getElementById("board-svg")
board_cells_element = document.getElementById("board-cells")
board_cells_active_element = document.getElementById("board-cells-active")

popup_element = document.getElementById("popup")
popup_title_element = document.getElementById("popup-title")
popup_input_element = document.getElementById("popup-input")

popup_button_elements = document.getElementsByClassName("popup-button")
popup_button_menu_element = document.getElementById("popup-button-menu")
popup_button_restart_element = document.getElementById("popup-button-restart")
popup_button_join_element = document.getElementById("popup-button-join")


def history_length_changed(new_length: int) -> None:
    control_undo_element.disabled = new_length == 0


history: ObservableList[tuple[Board, Move]] = ObservableList(history_length_changed)
old_move: Move | None
board: Board
legal_moves_var: list[Move]
black_pieces: list[int]
white_pieces: list[int]
is_white: bool
clicked: int | None


def draw_line(fx: int, fy: int, tx: int, ty: int, spacing: float) -> None:
    line = document.createElementNS(SVG_NAMESPACE, "line")
    line.setAttribute("x1", f"{fx * spacing + spacing / 2}")
    line.setAttribute("y1", f"{fy * spacing + spacing / 2}")
    line.setAttribute("x2", f"{tx * spacing + spacing / 2}")
    line.setAttribute("y2", f"{ty * spacing + spacing / 2}")

    board_svg_element.appendChild(line)


def draw_circle(x: int, y: int, spacing: int, radius: int) -> None:
    circle = document.createElementNS(SVG_NAMESPACE, "circle")
    circle.setAttribute("cx", f"{int(x * spacing + spacing / 2)}")
    circle.setAttribute("cy", f"{int(y * spacing + spacing / 2)}")
    circle.setAttribute("r", f"{int(radius)}")

    board_svg_element.appendChild(circle)


def add_board_svg(*args) -> None:
    board_svg_element.innerHTML = ""
    board_size = board_svg_element.clientWidth
    circle_spacing = board_size / BOARD_WIDTH
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

    cell_active = document.createElement("div")
    cell_active.classList.add("cell-active")

    for i in range(1, 26):
        addpiece = piece.cloneNode(False)
        addpiece.id = f"cell-{str(i)}"
        board_cells_element.appendChild(addpiece)

        addactive = cell_active.cloneNode(False)
        addactive.id = f"cell-active-{str(i)}"
        board_cells_active_element.appendChild(addactive)


add_board_svg()
add_board_cells()


def display_result_popup(text: str) -> None:
    display_popup(text, [popup_button_menu_element, popup_button_restart_element])


def display_join_popup() -> None:
    display_popup(
        "Join game", [popup_button_menu_element, popup_button_join_element], True
    )


def display_create_popup() -> None:
    display_popup(
        "Waiting for player...",
        [popup_button_menu_element, popup_button_join_element],
        True,
    )


def display_popup(title: str, buttons: list[Any], input: bool = False) -> None:
    popup_title_element.textContent = title
    popup_input_element.style.display = "inline-block" if input else "none"

    for child in popup_button_elements:
        child.style.display = "none"

    for button in buttons:
        button.style.display = "inline-block"

    popup_element.style.visibility = "visible"


def hide_popup() -> None:
    popup_element.style.visibility = "hidden"
    popup_input_element.value = ""


def display_menu() -> None:
    hide_popup()
    menu_element.style.visibility = "visible"
    game_element.style.visibility = "hidden"


def display_game() -> None:
    hide_popup()
    menu_element.style.visibility = "hidden"
    game_element.style.visibility = "visible"


def cell_set(id: int, class_type: str) -> None:
    document.getElementById(f"cell-{str(id)}").className = "cell " + class_type


def cell_active_set(id: int, class_type: str) -> None:
    document.getElementById(f"cell-active-{str(id)}").className = (
        "cell-active " + class_type
    )


def possible_moves(legal_moves_var: list[Move], clicked: int) -> list[Move]:
    if clicked is None:
        return []

    return [m for m in legal_moves_var if source(m) == clicked]


def draw_board(
    white: list[int], black: list[int], clicked: int, possible_moves: list[Move]
) -> None:
    for i in range(1, 26):
        cell_set(i, "")
        cell_active_set(i, "")

    for i in white:
        cell_set(i, CLASS_CELL_WHITE)
    for i in black:
        cell_set(i, CLASS_CELL_BLACK)

    if old_move:
        cell_active_set(source(old_move), CLASS_CELL_OLD)
        cell_active_set(target(old_move), CLASS_CELL_OLD)

    for m in possible_moves:
        cell_active_set(target(m), CLASS_CELL_POSSIBLE)

    if clicked:
        cell_set(clicked, CLASS_CELL_POSSIBLE)


def reload_board() -> None:
    global old_move, legal_moves_var, black_pieces, white_pieces, is_white, clicked
    legal_moves_var = legal_moves(board)
    black_pieces = black(board)
    white_pieces = white(board)
    is_white = white_plays(board)
    clicked = None
    draw_board(white_pieces, black_pieces, clicked, [])


@when("click", "#play-offline, .button-restart")  # #play-ai,
def setup_offline() -> None:
    global history, board, old_move

    old_move = None
    history.clear()
    board = make_board()
    reload_board()
    display_game()


@when("click", ".button-menu")
def click_button_menu(event):
    display_menu()


@when("click", "#play-join")
def click_button_join(event):
    display_join_popup()


@when("click", "#play-create")
def click_button_create(event):
    display_create_popup()


@when("click", ".button-undo")
def click_button_undo(event) -> None:
    global history, board, old_move
    board, old_move = history.pop()
    reload_board()


@when("click", ".cell")
def click_cell(event) -> None:
    global old_move, history, clicked, board, legal_moves_var, black_pieces, white_pieces, is_white
    id: int = int("".join(filter(str.isdigit, event.srcElement.id)))
    if clicked and is_legal(Move(clicked, id), board):
        history.append((copy(board), old_move))
        old_move = Move(clicked, id)
        move(Move(clicked, id), board)
        reload_board()

        if is_game_over(board):
            if not black_pieces:
                display_result_popup("White wins!")
            elif not white_pieces:
                display_result_popup("Black wins!")
            else:
                display_result_popup("Draw!")

        return

    elif (is_white and id in white_pieces) or (not is_white and id in black_pieces):
        clicked = id
    else:
        clicked = None

    draw_board(
        white_pieces, black_pieces, clicked, possible_moves(legal_moves_var, clicked)
    )


window.addEventListener("resize", create_proxy(add_board_svg))
