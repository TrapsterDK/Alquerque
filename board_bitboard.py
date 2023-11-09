from dataclasses import dataclass
from move import Move, make_move, source, target  # noqa: F401


BLACK_START = 0x1FFE
WHITE_START = 0x3FFC000
NO_PIECES = 0x0

VALID_MOVE_BB = 0x3FFFFFE
VALID_MOVE_LEFT_1_BB = 0x1EF7BDE
VALID_MOVE_RIGHT_1_BB = 0x3DEF7BC

BOARD_SIZE_X = 5
BOARD_SIZE_Y = 5
BOARD_SIZE = BOARD_SIZE_X * BOARD_SIZE_Y
BOARD_START_INDEX = 1
BOARD_END_INDEX = BOARD_SIZE + BOARD_SIZE

# Directions
MOVE_VERTICALLY = 5
MOVE_LEFT_1 = 0x1
MOVE_RIGHT_1 = 0x1

BITWISE_AND_MODULUS_2 = 0x1
CAN_MOVE_DIAGONALLY = 0x1  # 1 for odd indices, 0 for even indices


@dataclass
class Board:
    """A board for the game of alquerque."""

    white_bb: int
    black_bb: int
    is_white_turn: bool


def _get_bit(bb: int, i: int) -> int:
    """Return the bit at index i in the bitboard bb."""
    return (bb >> i) & 1


def _set_bit(bb: int, i: int) -> int:
    """Return the bitboard bb with the bit at index i set to 1."""
    return bb | (1 << i)


def _clear_bit(bb: int, i: int) -> int:
    """Return the bitboard bb with the bit at index i set to 0."""
    return bb & ~(1 << i)


def _pieces(bb: int) -> list[int]:
    """Return a list of the indices of the pieces in the bitboard bb."""
    return [i for i in range(BOARD_START_INDEX, BOARD_END_INDEX) if _get_bit(bb, i)]


def _win(b: Board) -> bool:
    """Return True if the game is won on board b, otherwise False."""
    return b.white_bb == NO_PIECES or b.black_bb == NO_PIECES


def _tie(b: Board) -> bool:
    """Return True if the game is tied on board b, otherwise False.
    Precondition: not _win(b)"""
    return False  # TODO


def _index_can_move_diagonally(index: int) -> bool:
    """Return True if the index can move diagonally, otherwise False."""
    return index & BITWISE_AND_MODULUS_2 == CAN_MOVE_DIAGONALLY


def _is_player_move_direction_up(is_white: bool) -> bool:
    """Return True if the player move direction is up, otherwise False."""
    return is_white


def make_board() -> Board:
    """Create a new board, with pieces in their starting positions."""
    return Board(WHITE_START, BLACK_START, True)


def white_plays(b: Board) -> bool:
    """Return True if it is white's turn to play, otherwise False."""
    return b.is_white_turn


def white(b: Board) -> list[int]:
    """Return a list of the white pieces indices on the board."""
    return _pieces(b.white_bb)


def black(b: Board) -> list[int]:
    """Return a list of the black pieces indices on the board."""
    return _pieces(b.black_bb)


def is_legal(m: Move, b: Board) -> bool:
    """Return True if move m is legal on board b, otherwise False."""
    is_white = white_plays(b)
    ally_bb = b.white_bb if is_white else b.black_bb
    enemy_bb = b.black_bb if is_white else b.white_bb
    source_index = source(m)

    # Check if the source piece is empty
    if not _get_bit(ally_bb, source_index):
        return False

    common_bb = ally_bb | enemy_bb
    target_index = target(m)

    # Check if the target piece is occupied
    if _get_bit(common_bb, target_index):
        return False

    source_bb = _set_bit(NO_PIECES, source_index)
    target_bb = _set_bit(NO_PIECES, target_index)

    foward_bb = (
        source_bb >> MOVE_VERTICALLY
        if _is_player_move_direction_up(is_white)
        else source_bb << MOVE_VERTICALLY
    )

    if _index_can_move_diagonally(source_index):
        forward_left_bb = (foward_bb >> MOVE_LEFT_1) & VALID_MOVE_LEFT_1_BB
        forward_right_bb = (foward_bb << MOVE_RIGHT_1) & VALID_MOVE_RIGHT_1_BB

        # Check target move is a diagonal move by one
        if (forward_left_bb | forward_right_bb) & target_bb:
            return True

    # Check target move is a move forward by one
    if foward_bb & target_bb:
        return True

    # Check if the target move is a jump move
    target_source_difference = abs(target_index - source_index)

    # Check if the target move is a jump move by two
    if target_source_difference not in [10, 2] + (
        [12, 8] if _index_can_move_diagonally(source_index) else []
    ):
        return False

    target_source_mid_index = target_source_difference >> 1
    target_source_mid_bb = _set_bit(NO_PIECES, target_source_mid_index)

    # Check if there is an enemy piece in between the source and target
    # if not, then the move is not a jump move and is illegal
    if not (target_source_mid_bb & enemy_bb):
        return False

    source_x_coordinate = source_index % BOARD_SIZE_X
    match (source_x_coordinate):
        case 0:
            return target_bb & 0x39CE738
        case 1:
            return target_bb & 0xE739CE
        case 2:
            return target_bb & 0x1EF7BDE
        case 3:
            return target_bb & 0x3FFFFFE
        case 4:
            return target_bb & 0x3DEF7BC
        case _:
            # This should never happen
            return False


def legal_moves(b: Board) -> list[Move]:
    """Return a list of legal moves on board b for the player whose turn it is to play."""
    moves = []
    common_bb = b.white_bb | b.black_bb
    enemy_bb = b.black_bb if white_plays(b) else b.white_bb
    is_white = white_plays(b)
    pieces_indices = white(b) if is_white else black(b)
    is_player_move_direction_up = _is_player_move_direction_up(is_white)
    move_direction_multiplier = -1 if is_player_move_direction_up else 1

    for source_index in pieces_indices:
        source_bb = _set_bit(NO_PIECES, source_index)
        forward_bb = (
            source_bb >> MOVE_VERTICALLY
            if is_player_move_direction_up
            else source_bb << MOVE_VERTICALLY
        )

        if forward_bb and not forward_bb & common_bb:
            moves.append(
                make_move(
                    source_index,
                    source_index + (MOVE_VERTICALLY * move_direction_multiplier),
                )
            )

        if _index_can_move_diagonally(source_index):
            forward_left_bb = (forward_bb >> MOVE_LEFT_1) & VALID_MOVE_LEFT_1_BB
            forward_right_bb = (forward_bb << MOVE_RIGHT_1) & VALID_MOVE_RIGHT_1_BB

            if forward_left_bb and not forward_left_bb & common_bb:
                moves.append(
                    make_move(
                        source_index,
                        source_index
                        + (MOVE_VERTICALLY * move_direction_multiplier)
                        - 1,
                    )
                )
            if forward_right_bb and not forward_right_bb & common_bb:
                moves.append(
                    make_move(
                        source_index,
                        source_index
                        + (MOVE_VERTICALLY * move_direction_multiplier)
                        + 1,
                    )
                )

        for i in [12, 10, 8, 2]:
            target_index = source_index + i
            target_bb = _set_bit(NO_PIECES, target_index)

            if target_bb & VALID_MOVE_BB and not target_bb & common_bb:
                target_source_mid_bb = _set_bit(NO_PIECES, source_index + (i >> 1))

                if target_source_mid_bb & enemy_bb:
                    moves.append(make_move(source_index, target_index))

            negative_target_index = source_index - i
            negative_target_bb = _set_bit(NO_PIECES, source_index << i)
            if (
                negative_target_bb & VALID_MOVE_BB
                and not negative_target_bb & common_bb
            ):
                target_source_mid_bb = _set_bit(NO_PIECES, source_index - (i >> 1))
                if target_source_mid_bb & enemy_bb:
                    moves.append(make_move(source_index, negative_target_index))

    return moves


def move(m: Move, b: Board) -> None:
    """Make move m on board b.
    Precondition: is_legal(m, b)"""
    is_white = white_plays(b)
    source_index = source(m)
    target_index = target(m)
    ally_bb = b.white_bb if is_white else b.black_bb
    enemy_bb = b.black_bb if is_white else b.white_bb

    # Remove the source piece from the board
    ally_bb = _clear_bit(ally_bb, source_index)

    # Add the target piece to the board
    ally_bb = _set_bit(ally_bb, target_index)

    target_source_difference = abs(target_index - source_index)

    if not 4 <= target_source_difference <= 6:
        # Jump move
        target_source_mid_index = source_index + (target_source_difference >> 1)
        enemy_bb = _clear_bit(enemy_bb, target_source_mid_index)

    if is_white:
        b.white_bb = ally_bb
        b.black_bb = enemy_bb
    else:
        b.white_bb = enemy_bb
        b.black_bb = ally_bb

    b.is_white_turn = not is_white


def is_game_over(b: Board) -> bool:
    """Return True if the game is over on board b, otherwise False."""
    return _win(b) or _tie(b)


def copy(b: Board) -> Board:
    """Return a copy of board b."""
    return Board(b.white_bb, b.black_bb, b.is_white_turn)
