import sys
import argparse
import tempfile
import http.server
import socketserver
from pathlib import Path
import threading
import signal

HOST = "127.0.0.1"
PORT = 8000
MOVE_FILE = Path("move.py")
ALQUERQUE_HTML = Path("alquerque.html")
WEB_HTML = Path("web.html")
MOVE = "move.py"
BOARD = "board.py"


class ReloadableTCPServer(socketserver.TCPServer):
    def serve_forever(self, poll_interval=0.5):
        self.reload = False
        while not self.reload:
            self.handle_request()
        self.server_close()


def files_refresh(dir, board_name):
    (dir / MOVE).open("w").write(MOVE_FILE.read_text())
    (dir / BOARD).open("w").write(Path(f"board_{board_name}.py").read_text())
    (dir / WEB_HTML).open("w").write(ALQUERQUE_HTML.read_text())


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
        with tempfile.TemporaryDirectory() as temp_dir:
            path_temp_dir = Path(temp_dir)

            files_refresh(path_temp_dir, args.board_representation)

            class CustomHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=temp_dir, **kwargs)

            server = socketserver.TCPServer((HOST, PORT), CustomHandler)
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.start()

            print(f"Serving on http://{HOST}:{PORT}/web.html")
            print("Press Ctrl+C to stop the server")
            print("Press r to restart the server")

            while True:
                try:
                    key = input()
                    if key == "r":
                        files_refresh(path_temp_dir, args.board_representation)
                        server.reload = True
                    elif key == "q":
                        raise KeyboardInterrupt
                    else:
                        print("Press r to restart the server or q to quit")
                except KeyboardInterrupt:
                    server.shutdown()
                    server.server_close()
                    break

    else:
        # import the board representation
        sys.modules["board"] = __import__("board_" + args.board_representation)

        # run the GUI
        import alquerqueGUI  # noqa: F401


if __name__ == "__main__":
    main()
