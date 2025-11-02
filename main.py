#!/usr/bin/env python3
"""
Шаховий бот з рушієм Stockfish
Гра в шахи на професійному рівні з підтримкою людської мови
"""
import chess
import sys
from colorama import Fore, Style, init
from chess_engine import ChessEngine
from board_visualizer import BoardVisualizer
from move_parser import MoveParser

# Ініціалізація colorama
init(autoreset=True)


class ChessBot:
    """Головний клас шахматного бота"""

    def __init__(self):
        self.board = chess.Board()
        self.engine = None
        self.visualizer = BoardVisualizer()
        self.parser = MoveParser()
        self.player_color = chess.WHITE
        self.game_over = False
        self.hints_enabled = True  # Показувати підказки за замовчуванням
        self.difficulty = 'grandmaster'  # За замовчуванням максимальний рівень

    def print_header(self, difficulty_level: str = None):
        """Відображає заголовок гри"""
        import config
        if difficulty_level:
            level_name = config.DIFFICULTY_LEVELS[difficulty_level]['name'].upper()
            title = f"♔ ШАХОВИЙ БОТ - РІВЕНЬ: {level_name} ♚"
        else:
            title = "♔ ШАХОВИЙ БОТ ♚"

        print("\n" + "=" * 60)
        print(f"{Fore.CYAN}{title}{Style.RESET_ALL}".center(70))
        print("=" * 60)
        print()

    def choose_difficulty(self) -> str:
        """Дає гравцю вибрати рівень складності"""
        import config

        print(f"\n{Fore.YELLOW}Оберіть рівень складності:{Style.RESET_ALL}")
        print(f"  1. {config.DIFFICULTY_LEVELS['child']['name']} - {config.DIFFICULTY_LEVELS['child']['description']}")
        print(f"  2. {config.DIFFICULTY_LEVELS['easy']['name']} - {config.DIFFICULTY_LEVELS['easy']['description']}")
        print(f"  3. {config.DIFFICULTY_LEVELS['medium']['name']} - {config.DIFFICULTY_LEVELS['medium']['description']}")
        print(f"  4. {config.DIFFICULTY_LEVELS['hard']['name']} - {config.DIFFICULTY_LEVELS['hard']['description']}")
        print(f"  5. {config.DIFFICULTY_LEVELS['grandmaster']['name']} - {config.DIFFICULTY_LEVELS['grandmaster']['description']}")

        difficulty_map = {
            '1': 'child',
            '2': 'easy',
            '3': 'medium',
            '4': 'hard',
            '5': 'grandmaster'
        }

        while True:
            choice = input(f"\n{Fore.GREEN}Ваш вибір (1-5): {Style.RESET_ALL}").strip()
            if choice in difficulty_map:
                difficulty = difficulty_map[choice]
                difficulty_name = config.DIFFICULTY_LEVELS[difficulty]['name']
                print(f"\n{Fore.CYAN}Обрано рівень: {difficulty_name}!{Style.RESET_ALL}")
                return difficulty
            else:
                print(f"{Fore.RED}Невірний вибір. Введіть число від 1 до 5.{Style.RESET_ALL}")

    def choose_color(self) -> chess.Color:
        """Дає гравцю вибрати колір фігур"""
        print(f"\n{Fore.YELLOW}Оберіть колір фігур:{Style.RESET_ALL}")
        print("  1. Білі (ходите першим)")
        print("  2. Чорні (ходите другим)")

        while True:
            choice = input(f"\n{Fore.GREEN}Ваш вибір (1 або 2): {Style.RESET_ALL}").strip()
            if choice == '1':
                print(f"\n{Fore.CYAN}Ви граєте білими фігурами!{Style.RESET_ALL}")
                return chess.WHITE
            elif choice == '2':
                print(f"\n{Fore.CYAN}Ви граєте чорними фігурами!{Style.RESET_ALL}")
                return chess.BLACK
            else:
                print(f"{Fore.RED}Невірний вибір. Введіть 1 або 2.{Style.RESET_ALL}")

    def setup_position(self) -> bool:
        """Налаштування початкової позиції (нова гра або FEN)"""
        print(f"\n{Fore.YELLOW}Налаштування гри:{Style.RESET_ALL}")
        print("  1. Нова гра (стандартна позиція)")
        print("  2. Продовжити з FEN позиції")

        while True:
            choice = input(f"\n{Fore.GREEN}Ваш вибір (1 або 2): {Style.RESET_ALL}").strip()

            if choice == '1':
                self.board = chess.Board()
                return True
            elif choice == '2':
                fen = input(f"\n{Fore.GREEN}Введіть FEN: {Style.RESET_ALL}").strip()
                try:
                    self.board = chess.Board(fen)
                    print(f"{Fore.CYAN}✓ FEN позицію завантажено успішно!{Style.RESET_ALL}")
                    return True
                except ValueError as e:
                    print(f"{Fore.RED}✗ Невірний FEN: {e}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Спробуйте ще раз або оберіть нову гру.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Невірний вибір. Введіть 1 або 2.{Style.RESET_ALL}")

    def show_help(self):
        """Показує довідку про формати введення ходів"""
        print(f"\n{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}ФОРМАТИ ВВЕДЕННЯ ХОДІВ:{Style.RESET_ALL}\n")
        print(f"{Fore.WHITE}1. Стандартна нотація:{Style.RESET_ALL} e4, Nf3, O-O, Qxd5")
        print(f"   {Fore.CYAN}💡 Можна українськими літерами:{Style.RESET_ALL} е4, Кf3")
        print(f"{Fore.WHITE}2. UCI формат:{Style.RESET_ALL} e2e4, g1f3")
        print(f"{Fore.WHITE}3. З дефісом:{Style.RESET_ALL} e2-e4, g1-f3")
        print(f"{Fore.WHITE}4. Людська мова:{Style.RESET_ALL}")
        print(f"   • пішак на e4 (або е4)")
        print(f"   • кінь на f3 (або ф3)")
        print(f"   • тура з a1 на a8")
        print(f"   • ферзь на d5")
        print(f"\n{Fore.WHITE}КОМАНДИ:{Style.RESET_ALL}")
        print(f"   • {Fore.GREEN}help{Style.RESET_ALL} - показати цю довідку")
        print(f"   • {Fore.GREEN}ходи{Style.RESET_ALL} або {Fore.GREEN}moves{Style.RESET_ALL} - показати всі можливі ходи")
        print(f"   • {Fore.GREEN}підказки{Style.RESET_ALL} або {Fore.GREEN}hints{Style.RESET_ALL} - увімкнути/вимкнути підказки")
        print(f"   • {Fore.GREEN}fen{Style.RESET_ALL} - показати FEN позиції")
        print(f"   • {Fore.GREEN}аналіз{Style.RESET_ALL} або {Fore.GREEN}analyze{Style.RESET_ALL} - аналіз позиції")
        print(f"   • {Fore.GREEN}зберегти{Style.RESET_ALL} або {Fore.GREEN}save{Style.RESET_ALL} - зберегти дошку як PNG/SVG")
        print(f"   • {Fore.GREEN}партія{Style.RESET_ALL} або {Fore.GREEN}savegame{Style.RESET_ALL} - зберегти партію в PGN")
        print(f"   • {Fore.GREEN}здатися{Style.RESET_ALL} або {Fore.GREEN}resign{Style.RESET_ALL} - здатися")
        print(f"   • {Fore.GREEN}вийти{Style.RESET_ALL} або {Fore.GREEN}quit{Style.RESET_ALL} - вийти з гри")
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}\n")

    def show_legal_moves(self):
        """Показує всі легальні ходи"""
        moves = self.parser.get_move_suggestions(self.board)
        print(f"\n{Fore.CYAN}Можливі ходи ({len(moves)}):{Style.RESET_ALL}")
        for i, move in enumerate(moves, 1):
            print(f"  {i}. {move}")
        print()

    def show_analysis(self):
        """Показує аналіз поточної позиції"""
        if not self.engine:
            print(f"{Fore.RED}Рушій не підключено{Style.RESET_ALL}")
            return

        print(f"\n{Fore.YELLOW}Аналізую позицію...{Style.RESET_ALL}")
        analysis = self.engine.analyze_position(self.board)

        print(f"\n{Fore.CYAN}{'─' * 40}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Оцінка позиції:{Style.RESET_ALL} {analysis['evaluation']}")
        if analysis['best_move']:
            best_move_san = self.board.san(analysis['best_move'])
            print(f"{Fore.WHITE}Найкращий хід:{Style.RESET_ALL} {best_move_san} ({analysis['best_move'].uci()})")
        print(f"{Fore.WHITE}Глибина аналізу:{Style.RESET_ALL} {analysis['depth']}")
        print(f"{Fore.CYAN}{'─' * 40}{Style.RESET_ALL}\n")

    def save_board(self):
        """Зберігає поточну позицію дошки як зображення"""
        import os
        from datetime import datetime

        # Створюємо папку для зображень, якщо її немає
        os.makedirs('saved_boards', exist_ok=True)

        # Генеруємо ім'я файлу з часовою міткою
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        print(f"\n{Fore.CYAN}Оберіть формат:{Style.RESET_ALL}")
        print("  1. PNG (графічний файл)")
        print("  2. SVG (векторне зображення)")
        print("  3. Обидва формати")

        choice = input(f"\n{Fore.GREEN}Ваш вибір (1-3): {Style.RESET_ALL}").strip()

        success = False

        if choice in ['1', '3']:
            # Зберігаємо PNG
            png_filename = f"saved_boards/board_{timestamp}.png"
            if self.visualizer.save_as_png(self.board, png_filename, self.player_color, self.visualizer.last_move):
                print(f"{Fore.GREEN}✓ PNG збережено: {png_filename}{Style.RESET_ALL}")
                success = True
            else:
                print(f"{Fore.YELLOW}⚠ PNG не вдалось зберегти (можливо відсутні бібліотеки){Style.RESET_ALL}")

        if choice in ['2', '3']:
            # Зберігаємо SVG
            svg_filename = f"saved_boards/board_{timestamp}.svg"
            if self.visualizer.save_svg(self.board, svg_filename, self.player_color, self.visualizer.last_move):
                print(f"{Fore.GREEN}✓ SVG збережено: {svg_filename}{Style.RESET_ALL}")
                success = True

        if choice not in ['1', '2', '3']:
            print(f"{Fore.RED}✗ Невірний вибір{Style.RESET_ALL}")
        elif success:
            print(f"\n{Fore.CYAN}💾 Позицію успішно збережено!{Style.RESET_ALL}\n")

    def save_game(self):
        """Зберігає партію в PGN форматі"""
        import os
        from datetime import datetime
        import chess.pgn

        # Створюємо папку для партій, якщо її немає
        os.makedirs('saved_games', exist_ok=True)

        # Генеруємо ім'я файлу з часовою міткою
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"saved_games/game_{timestamp}.pgn"

        try:
            # Створюємо PGN гру
            game = chess.pgn.Game()

            # Додаємо заголовки
            game.headers["Event"] = "Гра з Chess Bot"
            game.headers["Site"] = "Local"
            game.headers["Date"] = datetime.now().strftime('%Y.%m.%d')
            game.headers["White"] = "Гравець" if self.player_color == chess.WHITE else "Chess Bot"
            game.headers["Black"] = "Chess Bot" if self.player_color == chess.WHITE else "Гравець"

            # Додаємо рівень складності
            import config
            difficulty_name = config.DIFFICULTY_LEVELS[self.difficulty]['name']
            game.headers["BlackElo"] = f"Bot ({difficulty_name})" if self.player_color == chess.WHITE else "?"
            game.headers["WhiteElo"] = "?" if self.player_color == chess.WHITE else f"Bot ({difficulty_name})"

            # Визначаємо результат
            if self.board.is_checkmate():
                result = "1-0" if self.board.turn == chess.BLACK else "0-1"
            elif self.board.is_stalemate() or self.board.is_insufficient_material() or \
                 self.board.can_claim_fifty_moves() or self.board.can_claim_threefold_repetition():
                result = "1/2-1/2"
            else:
                result = "*"  # Гра не завершена
            game.headers["Result"] = result

            # Додаємо ходи
            node = game
            temp_board = chess.Board()
            for move in self.board.move_stack:
                node = node.add_variation(move)
                temp_board.push(move)

            # Зберігаємо в файл
            with open(filename, 'w', encoding='utf-8') as f:
                exporter = chess.pgn.FileExporter(f)
                game.accept(exporter)

            print(f"\n{Fore.GREEN}✓ Партію збережено: {filename}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}💾 PGN файл можна використати для аналізу в Chess.com, Lichess тощо{Style.RESET_ALL}\n")
            return True

        except Exception as e:
            print(f"{Fore.RED}✗ Помилка збереження партії: {e}{Style.RESET_ALL}")
            return False

    def get_player_move(self) -> chess.Move:
        """Отримує хід від гравця"""
        while True:
            move_text = input(f"{Fore.GREEN}Ваш хід: {Style.RESET_ALL}").strip()

            # Перевірка команд
            if move_text.lower() in ['help', 'довідка', 'допомога']:
                self.show_help()
                continue
            elif move_text.lower() in ['moves', 'ходи']:
                self.show_legal_moves()
                continue
            elif move_text.lower() in ['hints', 'підказки', 'підказка']:
                self.hints_enabled = not self.hints_enabled
                status = "увімкнено" if self.hints_enabled else "вимкнено"
                print(f"\n{Fore.CYAN}💡 Підказки {status}{Style.RESET_ALL}\n")
                continue
            elif move_text.lower() == 'fen':
                print(f"\n{Fore.CYAN}FEN: {self.board.fen()}{Style.RESET_ALL}\n")
                continue
            elif move_text.lower() in ['analyze', 'аналіз', 'аналізувати']:
                self.show_analysis()
                continue
            elif move_text.lower() in ['save', 'зберегти', 'зберегти позицію']:
                self.save_board()
                continue
            elif move_text.lower() in ['savegame', 'партія', 'зберегти партію', 'зберегти гру']:
                self.save_game()
                continue
            elif move_text.lower() in ['resign', 'здатися', 'здаюсь']:
                return None
            elif move_text.lower() in ['quit', 'exit', 'вийти', 'вихід']:
                sys.exit(0)

            # Парсинг ходу
            move = self.parser.parse_move(move_text, self.board)

            if move and move in self.board.legal_moves:
                return move
            else:
                print(f"{Fore.RED}✗ Невірний хід. Спробуйте ще раз або введіть 'help' для довідки.{Style.RESET_ALL}")

    def make_engine_move(self):
        """Робить хід за рушій"""
        if not self.engine:
            print(f"{Fore.RED}Рушій не підключено{Style.RESET_ALL}")
            return

        print(f"\n{Fore.YELLOW}🤖 Бот думає...{Style.RESET_ALL}")
        move = self.engine.get_best_move(self.board)

        # Зберігаємо SAN і українську анотацію перед тим як зробити хід
        move_san = self.board.san(move)
        move_uk = self.visualizer.get_move_ukrainian_description(self.board, move)
        self.board.push(move)

        color_name = "Білий" if self.board.turn == chess.BLACK else "Чорний"
        print(f"{Fore.CYAN}Зроблено хід: {move_san} ({move_uk}){Style.RESET_ALL}")

        # Отримуємо підказки для гравця якщо гра не закінчена
        hints = []
        if self.hints_enabled and not self.board.is_game_over():
            try:
                hints = self.engine.get_hints(self.board, num_hints=3, depth=10)
            except Exception:
                pass

        self.visualizer.show_move(self.board, move, self.player_color, move_san=move_san,
                                 show_hints=self.hints_enabled, best_moves=hints)

    def check_game_over(self) -> bool:
        """Перевіряє, чи гра закінчена"""
        if self.board.is_checkmate():
            winner = "Ви" if self.board.turn != self.player_color else "Бот"
            print(f"\n{Fore.GREEN}{'=' * 50}")
            print(f"{Fore.GREEN}МАТ! {winner} переміг/перемогла!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{'=' * 50}\n")
            return True
        elif self.board.is_stalemate():
            print(f"\n{Fore.YELLOW}ПАТ! Нічия.{Style.RESET_ALL}\n")
            return True
        elif self.board.is_insufficient_material():
            print(f"\n{Fore.YELLOW}Нічия через недостатність матеріалу.{Style.RESET_ALL}\n")
            return True
        elif self.board.can_claim_fifty_moves():
            print(f"\n{Fore.YELLOW}Нічия за правилом 50 ходів.{Style.RESET_ALL}\n")
            return True
        elif self.board.can_claim_threefold_repetition():
            print(f"\n{Fore.YELLOW}Нічия через триразове повторення позиції.{Style.RESET_ALL}\n")
            return True

        return False

    def play(self):
        """Головний ігровий цикл"""
        try:
            # Ініціалізація
            self.print_header()

            # Вибір рівня складності
            self.difficulty = self.choose_difficulty()

            # Оновлюємо заголовок з обраним рівнем
            self.print_header(self.difficulty)

            # Підключення рушія з відповідним рівнем
            try:
                import config
                difficulty_settings = config.DIFFICULTY_LEVELS[self.difficulty]
                self.engine = ChessEngine(
                    skill_level=difficulty_settings['skill_level'],
                    depth=difficulty_settings['depth'],
                    time_limit=difficulty_settings['time']
                )
            except Exception as e:
                print(f"{Fore.RED}Не вдалося запустити рушій: {e}{Style.RESET_ALL}")
                return

            # Налаштування гри
            if not self.setup_position():
                return

            self.player_color = self.choose_color()

            # Показуємо довідку
            self.show_help()

            # Показуємо початкову позицію
            from rich.console import Console
            from rich.panel import Panel

            console = Console()
            console.print()

            # Перевіряємо термінал
            import os
            terminal_name = os.environ.get('TERM_PROGRAM', os.environ.get('TERM', 'Unknown'))

            if os.environ.get('TERM_PROGRAM') == 'iTerm.app':
                viz_status = "[green]✓ iTerm2 - PNG зображення показуються прямо в терміналі![/green]"
            elif 'kitty' in terminal_name.lower():
                viz_status = "[green]✓ Kitty - PNG зображення показуються прямо в терміналі![/green]"
            else:
                viz_status = (
                    "[yellow]ℹ  PNG відкриється в Preview (автооновлення)[/yellow]\n"
                    "[dim]   Для PNG в терміналі: brew install --cask iterm2[/dim]"
                )

            import config
            difficulty_name = config.DIFFICULTY_LEVELS[self.difficulty]['name']

            welcome_panel = Panel(
                "[bold cyan]🎮 Гра розпочинається![/bold cyan]\n\n"
                f"[yellow]Рівень складності:[/yellow] [bold]{difficulty_name}[/bold]\n"
                f"{viz_status}\n"
                "[green]✓[/green] Високоякісні PNG зображення (600x600px)\n"
                "[green]✓[/green] Автоматичне оновлення після кожного ходу\n"
                "[green]✓[/green] Підказки після ходу бота\n",
                border_style="cyan bold",
                title=f"[bold]Шаховий Бот - {difficulty_name}[/bold]",
                title_align="center"
            )
            console.print(welcome_panel, justify="center")
            console.print()

            # Показуємо початкову дошку
            print(f"{Fore.CYAN}Початкова позиція:{Style.RESET_ALL}")
            self.visualizer.show_move(self.board, None, self.player_color)

            # Якщо гравець грає чорними, бот ходить першим
            if self.player_color == chess.BLACK:
                self.make_engine_move()

            # Основний ігровий цикл
            while not self.game_over:
                # Перевірка на закінчення гри
                if self.check_game_over():
                    break

                # Хід гравця
                if self.board.turn == self.player_color:
                    move = self.get_player_move()

                    if move is None:  # Гравець здався
                        print(f"\n{Fore.YELLOW}Ви здалися. Бот переміг!{Style.RESET_ALL}\n")
                        break

                    # Зберігаємо SAN перед тим як зробити хід
                    move_san = self.board.san(move)
                    self.board.push(move)

                    # Показуємо дошку без підказок (підказки будуть після ходу бота)
                    self.visualizer.show_move(self.board, move, self.player_color, move_san=move_san)

                    # Перевірка на закінчення гри після ходу гравця
                    if self.check_game_over():
                        break

                # Хід бота
                if self.board.turn != self.player_color:
                    self.make_engine_move()

            # Показуємо фінальну позицію
            print(f"\n{Fore.CYAN}Фінальна позиція:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}FEN: {self.board.fen()}{Style.RESET_ALL}\n")

            # Пропозиція збереження партії
            if len(self.board.move_stack) > 0:  # Якщо були зроблені ходи
                save_choice = input(f"{Fore.YELLOW}Зберегти партію для аналізу? (так/ні): {Style.RESET_ALL}").strip().lower()
                if save_choice in ['так', 'yes', 'y', 'т']:
                    self.save_game()

            # Пропозиція нової гри
            play_again = input(f"{Fore.GREEN}Зіграти ще раз? (так/ні): {Style.RESET_ALL}").strip().lower()
            if play_again in ['так', 'yes', 'y', 'т']:
                self.game_over = False
                self.board = chess.Board()
                self.play()

        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Гру перервано користувачем.{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}Помилка: {e}{Style.RESET_ALL}")
        finally:
            if self.engine:
                self.engine.close()
                print(f"\n{Fore.CYAN}Дякую за гру! До побачення!{Style.RESET_ALL}\n")


def main():
    """Головна функція"""
    bot = ChessBot()
    bot.play()


if __name__ == "__main__":
    main()
