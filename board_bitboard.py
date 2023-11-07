from dataclasses import dataclass
from move import Move, make_move, source, target  # noqa: F401

BLACK_START = 0x1ffe
WHITE_START = 0x3ffc000

@dataclass
class Board:
    """A board for the game of alquerque."""
    white_pieces: int
    black_pieces: int
    is_white_turn: bool

def make_board() -> Board:
    """Create a new board, with pieces in their starting positions."""
    return Board(WHITE_START, BLACK_START, True)

def white_plays(b: Board) -> bool:
    """Return True if it is white's turn to play, otherwise False."""
    return b.is_white_turn

def white(b: Board) -> list[int]:
    """Return a list of the white pieces indices on the board."""
    raise NotImplementedError

def black(b: Board) -> list[int]:
    """Return a list of the black pieces indices on the board."""
    raise NotImplementedError

def is_legal(m: Move, b: Board) -> bool:
    """Return True if move m is legal on board b, otherwise False."""
    raise NotImplementedError

def legal_moves(b: Board) -> list[Move]:
    """Return a list of legal moves on board b for the player whose turn it is to play."""
    raise NotImplementedError

def move(m: Move, b: Board) -> None:
    """Make move m on board b."""
    raise NotImplementedError

def is_game_over(b: Board) -> bool:
    """Return True if the game is over on board b, otherwise False."""
    raise NotImplementedError

def copy(b: Board) -> Board:
    """Return a copy of board b."""
    raise NotImplementedError