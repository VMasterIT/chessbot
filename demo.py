#!/usr/bin/env python3
"""
Демонстраційний скрипт для показу можливостей шахматного бота
Автоматично виконує кілька ходів та демонструє функції
"""
import chess
from chess_engine import ChessEngine
from board_visualizer import BoardVisualizer
from move_parser import MoveParser
from colorama import Fore, Style, init
import time

init(autoreset=True)


def print_header(text):
    """Друкує заголовок"""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{text.center(60)}")
    print(f"{'=' * 60}{Style.RESET_ALL}\n")


def demo_basic_visualization():
    """Демо базової візуалізації"""
    print_header("📺 ДЕМО: Базова візуалізація")

    board = chess.Board()
    visualizer = BoardVisualizer()

    print("Початкова позиція:")
    visualizer.display(board)

    print(f"\n{Fore.GREEN}✓ Консольна візуалізація працює!{Style.RESET_ALL}")
    time.sleep(2)


def demo_move_parsing():
    """Демо розпізнавання ходів"""
    print_header("🗣️ ДЕМО: Розпізнавання людської мови")

    board = chess.Board()
    parser = MoveParser()
    visualizer = BoardVisualizer()

    test_moves = [
        ("e4", "Стандартна нотація"),
        ("e7e5", "UCI формат"),
        ("g1-f3", "Формат з дефісом"),
        ("кінь на c6", "Людська мова")
    ]

    print("Тестуємо різні формати введення ходів:\n")

    for move_text, description in test_moves:
        move = parser.parse_move(move_text, board)
        if move:
            board.push(move)
            print(f"{Fore.GREEN}✓ {description}:{Style.RESET_ALL} '{move_text}' → {move}")
        else:
            print(f"{Fore.RED}✗ {description}:{Style.RESET_ALL} '{move_text}'")

    print(f"\n{Fore.CYAN}Позиція після ходів:{Style.RESET_ALL}")
    visualizer.display(board)

    time.sleep(2)


def demo_engine():
    """Демо рушія Stockfish"""
    print_header("🤖 ДЕМО: Рушій Stockfish")

    try:
        engine = ChessEngine()
        board = chess.Board()

        print("Запитуємо рушій про найкращий хід у початковій позиції...")
        move = engine.get_best_move(board)

        print(f"\n{Fore.GREEN}✓ Stockfish рекомендує: {move} ({board.san(move)}){Style.RESET_ALL}")

        # Аналіз
        print(f"\n{Fore.YELLOW}Проводимо аналіз позиції...{Style.RESET_ALL}")
        analysis = engine.analyze_position(board)

        print(f"\n{Fore.CYAN}Результати аналізу:{Style.RESET_ALL}")
        print(f"  • Оцінка: {analysis['evaluation']}")
        print(f"  • Найкращий хід: {analysis['best_move']}")
        print(f"  • Глибина: {analysis['depth']}")

        engine.close()

    except Exception as e:
        print(f"{Fore.RED}✗ Помилка рушія: {e}{Style.RESET_ALL}")

    time.sleep(2)


def demo_graphics():
    """Демо графічної візуалізації"""
    print_header("🎨 ДЕМО: Графічна візуалізація")

    board = chess.Board()
    # Зробимо красиву позицію
    moves = ["e4", "e5", "Nf3", "Nc6", "Bc4"]
    for move_text in moves:
        board.push_san(move_text)

    visualizer = BoardVisualizer()

    print("Генеруємо SVG зображення...")
    svg = visualizer.generate_svg(board)
    print(f"{Fore.GREEN}✓ SVG згенеровано ({len(svg)} символів){Style.RESET_ALL}")

    import os
    os.makedirs('demo_output', exist_ok=True)

    # Зберігаємо SVG
    print("\nЗберігаємо SVG файл...")
    if visualizer.save_svg(board, 'demo_output/demo_board.svg'):
        print(f"{Fore.GREEN}✓ Збережено: demo_output/demo_board.svg{Style.RESET_ALL}")

    # Зберігаємо PNG
    print("\nЗберігаємо PNG файл...")
    if visualizer.save_as_png(board, 'demo_output/demo_board.png'):
        print(f"{Fore.GREEN}✓ Збережено: demo_output/demo_board.png{Style.RESET_ALL}")

    # Тестуємо байти
    print("\nГенеруємо PNG як байти (для Discord/Telegram)...")
    png_bytes = visualizer.get_png_bytes(board)
    if png_bytes:
        print(f"{Fore.GREEN}✓ PNG байти готові ({len(png_bytes)} байт){Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}Позиція на дошці:{Style.RESET_ALL}")
    visualizer.display(board, last_move=board.peek())

    time.sleep(2)


def demo_game():
    """Демо короткої гри"""
    print_header("♟️ ДЕМО: Коротка партія")

    try:
        board = chess.Board()
        engine = ChessEngine()
        visualizer = BoardVisualizer()

        print(f"{Fore.YELLOW}Гра проти Stockfish (3 ходи кожній стороні)...{Style.RESET_ALL}\n")

        # Італьянський початок
        player_moves = ["e4", "Nf3", "Bc4"]
        move_names = ["Королівський пішак вперед", "Кінь на f3", "Слон на c4"]

        for i, (move_text, name) in enumerate(zip(player_moves, move_names), 1):
            # Хід гравця
            print(f"\n{Fore.GREEN}Хід {i} (Білі - Гравець): {name} ({move_text}){Style.RESET_ALL}")
            move = board.parse_san(move_text)
            board.push(move)

            visualizer.display(board, last_move=move)
            time.sleep(1)

            # Хід бота
            if not board.is_game_over():
                print(f"\n{Fore.YELLOW}Stockfish думає...{Style.RESET_ALL}")
                bot_move = engine.get_best_move(board)
                board.push(bot_move)

                print(f"{Fore.CYAN}Хід {i} (Чорні - Stockfish): {board.san(bot_move)} ({bot_move}){Style.RESET_ALL}")
                visualizer.display(board, last_move=bot_move)
                time.sleep(1)

        print(f"\n{Fore.GREEN}✓ Демо партія завершена!{Style.RESET_ALL}")

        # Зберігаємо фінальну позицію
        import os
        os.makedirs('demo_output', exist_ok=True)
        visualizer.save_as_png(board, 'demo_output/demo_game.png', chess.WHITE, board.peek())
        print(f"{Fore.GREEN}✓ Позиція збережена: demo_output/demo_game.png{Style.RESET_ALL}")

        engine.close()

    except Exception as e:
        print(f"{Fore.RED}✗ Помилка: {e}{Style.RESET_ALL}")

    time.sleep(2)


def main():
    """Головна функція"""
    print("\n" + "=" * 60)
    print(f"{Fore.CYAN}♔ ДЕМОНСТРАЦІЯ ШАХМАТНОГО БОТА ♚{Style.RESET_ALL}".center(70))
    print("=" * 60)

    print(f"\n{Fore.YELLOW}Цей скрипт автоматично демонструє всі можливості бота.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Загальний час виконання: ~15-20 секунд{Style.RESET_ALL}\n")

    input(f"{Fore.GREEN}Натисніть Enter для початку... {Style.RESET_ALL}")

    demos = [
        ("Візуалізація", demo_basic_visualization),
        ("Розпізнавання мови", demo_move_parsing),
        ("Рушій Stockfish", demo_engine),
        ("Графіка", demo_graphics),
        ("Коротка партія", demo_game),
    ]

    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            demo_func()
        except Exception as e:
            print(f"\n{Fore.RED}✗ Помилка в демо '{name}': {e}{Style.RESET_ALL}\n")

    print_header("✅ ДЕМОНСТРАЦІЯ ЗАВЕРШЕНА")

    print(f"{Fore.GREEN}Усі основні функції працюють!{Style.RESET_ALL}\n")
    print("Згеноровані файли:")
    print("  📁 demo_output/demo_board.svg")
    print("  📁 demo_output/demo_board.png")
    print("  📁 demo_output/demo_game.png")

    print(f"\n{Fore.CYAN}Тепер ви можете запустити повноцінну гру:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}python main.py{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()
