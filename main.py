import sys
import argparse
import webbrowser
import tempfile
import http.server
import socketserver


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run alquerque using a given board representation."
    )

    # must have a string argument for the board representation with either
    # bitboard, list, matrix, split, splitcord
    parser.add_argument(
        "board_representation",
        type=str,
        choices=["bitboard", "list", "matrix", "split", "splitcord"],
        help="the board representation to use",
    )

    parser.add_argument(
        "-t",
        "--type",
        type=str,
        choices=["web", "tkinter"],
        default="web",
        help="the version of the GUI to use",
    )

    args = parser.parse_args()

    if args.type == "web":
        # serve move.py and board_<representation>.py
        PORT = 8000
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("serving at port", PORT)
            httpd.serve_forever()

        """
        html = Path("alquerque.html").read_text()
        move_str = Path("move.py").read_text()
        board_str = Path("board_" + args.board_representation + ".py").read_text()

        board_move_import_start = board_str.find("from move")
        board_move_import_end = board_str.find("\n", board_move_import_start)

        board_str = (
            board_str[:board_move_import_start]
            + "\n"
            + move_str
            + "\n"
            + board_str[board_move_import_end:]
        )
        html = html.replace("{{python-inject}}", board_str)
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html") as f:
            url = "file://" + f.name
            f.write(html)
            webbrowser.open(url)
        """

    else:
        # import the board representation
        sys.modules["board"] = __import__("board_" + args.board_representation)

        # run the GUI
        import alquerqueGUI  # noqa: F401


if __name__ == "__main__":
    main()
