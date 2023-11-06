from dataclasses import dataclass

@dataclass
class Move:
    """A move on a board."""
    source: int
    target: int


def make_move(src: int, trg: int) -> Move:
    """Make Move object."""
    return Move(src, trg)

def source(m: Move) -> int:
    """Get source of move."""
    return m.source

def target(m: Move) -> int:
    """Get target of move."""
    return m.target