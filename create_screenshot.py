#!/usr/bin/env python3
"""
Створення скріншоту для README
"""
import chess
from board_visualizer import BoardVisualizer

# Створюємо дошку з кількома ходами
board = chess.Board()

# Грамо кілька ходів для демонстрації
moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6"]
last_move = None

for move_str in moves:
    move = chess.Move.from_uci(move_str)
    board.push(move)
    last_move = move

# Створюємо візуалізатор і зберігаємо PNG
visualizer = BoardVisualizer()
success = visualizer.save_as_png(
    board, 
    'screenshots/gameplay.png',
    player_color=chess.WHITE,
    last_move=last_move,
    size=600
)

if success:
    print("✓ Скріншот створено: screenshots/gameplay.png")
else:
    print("✗ Помилка створення скріншоту")
