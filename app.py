import os
import random
from typing import Iterable, List, Optional, Tuple

from flask import Flask, jsonify, request

BOARD_SIZE = 15
EMPTY = 0
BLACK = 1
WHITE = 2
DEBUG = True

app = Flask(__name__)

def choose_move(board: List[List[int]]) -> Tuple[int, int]:
    # TODO: Make your own AI
    if DEBUG:
        row, col = map(int, input().split())
        return row, col
    else:
        pass

def validate_board(board: object) -> List[List[int]]:
    if not isinstance(board, list) or len(board) != BOARD_SIZE:
        raise ValueError("board must be a 15x15 list")
    normalized = []
    for row in board:
        if not isinstance(row, list) or len(row) != BOARD_SIZE:
            raise ValueError("board must be a 15x15 list")
        normalized_row = []
        for cell in row:
            if cell not in (EMPTY, BLACK, WHITE):
                raise ValueError("board cells must be 0, 1, or 2")
            normalized_row.append(cell)
        normalized.append(normalized_row)
    return normalized


@app.post("/api/turn")
def turn():
    payload = request.get_json(silent=True) or {}
    try:
        board = validate_board(payload.get("board"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    row, col = choose_move(board)
    return jsonify({"data": {"row": row, "col": col}})


@app.get("/healthz")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
