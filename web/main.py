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
from minimax import next_move
from observablelist import ObservableList
import json
import asyncio
from js import window, document, Peer  # type: ignore
from pyscript import when  # type: ignore
from pyodide.ffi import create_proxy  # type: ignore


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
control_restart_element = document.getElementById("control-restart")
menu_element = document.getElementById("menu")
game_element = document.getElementById("game")
board_svg_element = document.getElementById("board-svg")
board_cells_element = document.getElementById("board-cells")
board_cells_active_element = document.getElementById("board-cells-active")

popup_element = document.getElementById("popup")
popup_title_element = document.getElementById("popup-title")
popup_input_element = document.getElementById("popup-input")
popup_play_as_element = document.getElementById("popup-play-as-buttons")

popup_button_elements = document.getElementsByClassName("popup-button")
popup_button_menu_element = document.getElementById("popup-button-menu")
popup_button_restart_element = document.getElementById("popup-button-restart")
popup_button_join_element = document.getElementById("popup-button-join")


def history_length_changed(new_length: int) -> None:
    control_undo_element.disabled = new_length == 0


history: ObservableList[tuple[Board, Move]] = ObservableList(history_length_changed)
is_ai: bool
player_is_white: bool
player_is_black: bool
old_move: Move | None
board: Board
legal_moves_var: list[Move]
black_pieces: list[int]
white_pieces: list[int]
is_white: bool
clicked: int | None = None
play_as_is_ai: bool
peer: Peer = Peer.new()
peer_id: str
conn: Any
is_online: bool = False


def conn_data_handler(data: str) -> None:
    d = json.loads(data)
    if "is_white" in d:
        global player_is_white, player_is_black, is_online
        is_online = True
        player_is_white = not d["is_white"]
        player_is_black = d["is_white"]
        control_undo_element.style.display = "none"
        control_restart_element.style.display = "none"
        setup_game()
    elif "move" in d:
        global old_move, history, board, legal_moves_var, black_pieces, white_pieces, is_white
        history.append((copy(board), old_move))
        old_move = Move(d["move"][0], d["move"][1])
        move(old_move, board)
        reload_board()

        if is_game_over(board):
            if not black_pieces:
                display_result_popup("White wins!")
            elif not white_pieces:
                display_result_popup("Black wins!")
            else:
                display_result_popup("Draw!")


def peer_open(id: str) -> None:
    global peer_id
    peer_id = id


def peer_connection(connection: Any) -> None:
    global conn
    conn = connection
    conn.on("data", create_proxy(conn_data_handler))
    conn.on(
        "open",
        create_proxy(lambda: conn.send(json.dumps({"is_white": player_is_white}))),
    )
    setup_game()


peer.on("open", create_proxy(peer_open))
peer.on("connection", create_proxy(peer_connection))


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


def display_play_as_popup() -> None:
    display_popup(
        "Play as", [popup_button_menu_element, popup_button_join_element], play_as=True
    )


def display_join_popup() -> None:
    display_popup(
        "Join game", [popup_button_menu_element, popup_button_join_element], input=True
    )


def display_waiting_player_popup() -> None:
    display_popup(
        "Waiting for player...",
        [popup_button_menu_element],
        input_str=peer_id,
        input=True,
    )


def display_popup(
    title: str,
    buttons: list[Any],
    play_as: bool = False,
    input: bool = False,
    input_str: str = "",
) -> None:
    popup_title_element.textContent = title
    popup_play_as_element.style.display = "flex" if play_as else "none"
    popup_input_element.style.display = "inline-block" if input else "none"

    popup_input_element.value = input_str
    if input_str:
        popup_input_element.readOnly = True
    else:
        popup_input_element.readOnly = False

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


@when("click", ".button-restart")
def setup_game() -> None:
    global history, board, old_move

    old_move = None
    history.clear()
    board = make_board()
    reload_board()
    display_game()

    if is_ai and not player_is_white:
        m = next_move(board)
        history.append((copy(board), m))
        old_move = m
        move(m, board)
        reload_board()


@when("click", ".button-menu")
def click_button_menu(event):
    display_menu()


@when("click", "#play-offline")
def click_button_play_offline(event):
    global player_is_white, player_is_black, is_ai, is_online
    control_undo_element.style.display = "inline-block"
    control_restart_element.style.display = "inline-block"
    is_online = False
    is_ai = False
    player_is_white = True
    player_is_black = True
    setup_game()


@when("click", "#play-ai")
def click_button_play_as(event):
    global play_as_is_ai, is_ai
    is_ai = True
    play_as_is_ai = True
    display_play_as_popup()


@when("click", "#play-join")
def click_button_play_join(event):
    global is_ai
    is_ai = False
    display_join_popup()


@when("click", "#play-create")
def click_button_create(event):
    global play_as_is_ai, is_ai
    is_ai = False
    play_as_is_ai = False
    display_play_as_popup()


def play_as_handler() -> None:
    global is_online
    if play_as_is_ai:
        control_restart_element.style.display = "inline-block"
        control_undo_element.style.display = "inline-block"
        is_online = False
        setup_game()
    else:
        control_restart_element.style.display = "none"
        control_undo_element.style.display = "none"
        is_online = True
        display_waiting_player_popup()


@when("click", "#popup-button-join")
def click_button_join(event):
    global conn
    conn = peer.connect(popup_input_element.value)
    conn.on("data", create_proxy(conn_data_handler))


@when("click", "#popup-play-as-white")
def click_button_play_as_white(event):
    global player_is_white, player_is_black
    player_is_white = True
    player_is_black = False
    play_as_handler()


@when("click", "#popup-play-as-black")
def click_button_play_as_black(event):
    global player_is_white, player_is_black
    player_is_white = False
    player_is_black = True
    play_as_handler()


@when("click", ".button-undo")
def click_button_undo(event) -> None:
    global history, board, old_move
    board, old_move = history.pop()
    if is_ai and (
        white_plays(board)
        and not player_is_white
        or not white_plays(board)
        and not player_is_black
    ):
        board, old_move = history.pop()
    reload_board()


async def ai_move():
    global old_move, history, board, legal_moves_var, black_pieces, white_pieces, is_white
    draw_board(
        white_pieces,
        black_pieces,
        clicked,
        possible_moves(legal_moves_var, clicked),
    )

    m = next_move(board)
    history.append((copy(board), old_move))
    old_move = m
    move(m, board)
    reload_board()

    if is_game_over(board):
        if not black_pieces:
            display_result_popup("White wins!")
        elif not white_pieces:
            display_result_popup("Black wins!")
        else:
            display_result_popup("Draw!")


@when("click", ".cell")
def click_cell(event) -> None:
    global old_move, history, clicked, board, legal_moves_var, black_pieces, white_pieces, is_white
    if is_white and not player_is_white or not is_white and not player_is_black:
        return

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
        elif is_ai:
            asyncio.ensure_future(ai_move())

        elif is_online:
            conn.send(json.dumps({"move": [source(old_move), target(old_move)]}))

        return

    elif (is_white and id in white_pieces) or (not is_white and id in black_pieces):
        clicked = id
    else:
        clicked = None

    draw_board(
        white_pieces, black_pieces, clicked, possible_moves(legal_moves_var, clicked)
    )


def on_click_window(event):
    global clicked
    if "cell-" in event.target.id:
        return
    if clicked:
        clicked = None
        draw_board(white_pieces, black_pieces, clicked, [])


window.addEventListener("click", create_proxy(on_click_window))
window.addEventListener("resize", create_proxy(add_board_svg))
