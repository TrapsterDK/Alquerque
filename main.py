import sys
import argparse

def main() -> None:
    parser = argparse.ArgumentParser(description='Run alquerque using a given board representation.')

    # must have a string argument for the board representation with either
    # bitboard, list, matrix, split, splitcord
    parser.add_argument('board_representation', type=str, choices=['bitboard', 'list', 'matrix', 'split', 'splitcord'],
                        help='the board representation to use')
    
    args = parser.parse_args()

    # import the board representation
    sys.modules['board'] = __import__("board_" + args.board_representation)

    # run the GUI
    import alquerqueGUI  # noqa: F401

if __name__ == '__main__':
    main()