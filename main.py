import sys
import argparse
import tempfile
import http.server
import socketserver
from pathlib import Path
import threading
import os

HOST = "127.0.0.1"
PORT = 8000
MOVE_FILE = Path("move.py")
WEB_DIR = Path("web/")
GUI_DIR = Path("gui/")
WEB_INDEX_FILE = "index.html"
TEMP_MOVE = "move.py"
TEMP_BOARD = "board.py"
TEMP_MINIMAX = "minimax.py"


class ReloadableTCPServer(socketserver.TCPServer):
    def serve_forever(self, poll_interval=0.5):
        self.reload = False
        while not self.reload:
            self.handle_request()
        self.server_close()


def files_refresh(dir, board_name, minimax_name):
    (dir / TEMP_MOVE).open("w").write(MOVE_FILE.read_text())
    (dir / TEMP_BOARD).open("w").write(Path(f"{board_name}.py").read_text())
    (dir / TEMP_MINIMAX).open("w").write(Path(f"{minimax_name}.py").read_text())
    for file in WEB_DIR.iterdir():
        (dir / file.name).open("w").write(file.read_text())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run alquerque using a given board representation."
    )

    parser.add_argument(
        "-b",
        "--board-representation",
        type=str,
        required=True,
        help="the python file containing the board representation without the .py extension",
    )

    parser.add_argument(
        "-m",
        "--minimax",
        type=str,
        required=True,
        help="the python file containing the minimax algorithm without the .py extension",
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

    # check if the board representation file exists
    if not Path(f"{args.board_representation}.py").exists():
        print(f"{args.board_representation}.py does not exist")
        sys.exit(1)

    # check if the minimax file exists
    if not Path(f"{args.minimax}.py").exists():
        print(f"{args.minimax}.py does not exist")
        sys.exit(1)

    if args.type == "web":
        with tempfile.TemporaryDirectory() as temp_dir:
            path_temp_dir = Path(temp_dir)

            files_refresh(path_temp_dir, args.board_representation, args.minimax)

            class CustomHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=temp_dir, **kwargs)

            server = socketserver.TCPServer((HOST, PORT), CustomHandler)
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.start()

            print(f"Serving on http://{HOST}:{PORT}/{WEB_INDEX_FILE}")
            print("Press Ctrl+C to stop the server")
            print("Press r to restart the server")

            while True:
                try:
                    key = input()
                    if key == "r":
                        files_refresh(
                            path_temp_dir, args.board_representation, args.minimax
                        )
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
        sys.modules["board"] = __import__(args.board_representation)
        sys.modules["minimax"] = __import__(args.minimax)

        os.chdir(GUI_DIR)

        # run the GUI
        import gui.alquerqueGUI  # noqa: F401


if __name__ == "__main__":
    main()
