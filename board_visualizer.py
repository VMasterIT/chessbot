"""
Модуль для візуалізації шахової дошки в консолі та графічно
"""
import chess
import chess.svg
from colorama import init, Fore, Back, Style
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
import config
from io import BytesIO
from typing import Optional
import subprocess
import platform

try:
    import cairosvg
    from PIL import Image
    GRAPHICS_AVAILABLE = True
except ImportError:
    GRAPHICS_AVAILABLE = False

# Ініціалізація colorama
init(autoreset=True)

# Ініціалізація Rich console
console = Console()


class BoardVisualizer:
    """Клас для відображення шахової дошки"""

    def __init__(self):
        self.last_move = None

    def display(self, board: chess.Board, player_color: chess.Color = chess.WHITE,
                last_move: chess.Move = None):
        """
        Відображає шахову дошку в консолі (покращена версія з Rich)

        Args:
            board: Об'єкт шахової дошки
            player_color: Колір гравця (WHITE або BLACK) для орієнтації дошки
            last_move: Останній зроблений хід для підсвітки
        """
        self.last_move = last_move

        # Створюємо таблицю для дошки
        table = Table(show_header=False, show_edge=True, box=box.DOUBLE_EDGE, padding=(0, 1))

        # Додаємо колонки (для координат ліворуч та праворуч)
        table.add_column("", justify="center", width=3)  # Ліві цифри
        for _ in range(8):
            table.add_column("", justify="center", width=5)
        table.add_column("", justify="center", width=3)  # Праві цифри

        # Визначаємо порядок рядків залежно від кольору гравця
        if player_color == chess.WHITE:
            ranks = range(7, -1, -1)  # 8-1
            files = range(8)  # a-h
            file_labels = "a b c d e f g h"
        else:
            ranks = range(8)  # 1-8
            files = range(7, -1, -1)  # h-a
            file_labels = "h g f e d c b a"

        # Додаємо рядок з координатами зверху
        table.add_row("", *file_labels.split(), "")

        # Додаємо рядки дошки
        for rank in ranks:
            row = [f"[bold cyan]{rank + 1}[/bold cyan]"]

            for file in files:
                square = chess.square(file, rank)
                piece = board.piece_at(square)

                # Визначаємо, чи потрібно підсвічувати клітинку
                is_highlighted = False
                if last_move and (square == last_move.from_square or square == last_move.to_square):
                    is_highlighted = True

                # Визначаємо колір клітинки
                is_light = (rank + file) % 2 == 1

                # Форматуємо клітинку з кращими кольорами
                if is_highlighted:
                    # Яскравий зелений фон для підсвіченого ходу
                    bg_color = "on green"
                    piece_color = "black"
                elif is_light:
                    # Світлі клітинки - білий фон
                    bg_color = "on white"
                    piece_color = "black"
                else:
                    # Темні клітинки - темно-сірий фон
                    bg_color = "on #8B7355"
                    piece_color = "white"

                # Додаємо фігуру з правильними кольорами
                if piece:
                    piece_symbol = config.PIECE_SYMBOLS.get(piece.symbol(), piece.symbol())
                    # Білі фігури - bold
                    if piece.color == chess.WHITE:
                        cell_text = Text(f" {piece_symbol} ", style=f"bold {piece_color} {bg_color}")
                    else:
                        cell_text = Text(f" {piece_symbol} ", style=f"{piece_color} {bg_color}")
                else:
                    cell_text = Text("   ", style=bg_color)

                row.append(cell_text)

            row.append(f"[bold cyan]{rank + 1}[/bold cyan]")
            table.add_row(*row)

        # Додаємо рядок з координатами знизу
        table.add_row("", *file_labels.split(), "")

        console.print()
        console.print(table, justify="center")
        console.print()


    def show_move(self, board: chess.Board, move: chess.Move = None, player_color: chess.Color = chess.WHITE,
                  move_san: str = None, show_hints: bool = False, best_moves: list = None):
        """
        Показує інформацію про хід та графічну візуалізацію

        Args:
            board: Об'єкт шахової дошки
            move: Хід для відображення (None для початкової позиції)
            player_color: Колір гравця
            move_san: Хід у SAN нотації
            show_hints: Показати підказки
            best_moves: Список кращих ходів для підказки
        """
        import os
        import tempfile

        console.print()

        # Створюємо красиву панель з інформацією
        info_lines = []

        if move_san:
            info_lines.append(f"[bold green]✓ Зроблено хід:[/bold green] [yellow]{move_san}[/yellow]")

        # Чий хід зараз
        current_turn = "Білих" if board.turn == chess.WHITE else "Чорних"
        info_lines.append(f"[bold cyan]► Хід:[/bold cyan] [yellow]{current_turn}[/yellow]")

        # Номер ходу
        move_number = board.fullmove_number
        info_lines.append(f"[bold cyan]► Хід №:[/bold cyan] [yellow]{move_number}[/yellow]")

        # FEN
        info_lines.append(f"[bold cyan]► FEN:[/bold cyan] [dim]{board.fen()}[/dim]")

        # Перевірка на шах/мат
        if board.is_checkmate():
            info_lines.append("")
            info_lines.append("[bold red on white] ♔ МАТ! ♚ [/bold red on white]")
        elif board.is_check():
            info_lines.append("")
            info_lines.append("[bold yellow]⚠ ШАХ![/bold yellow]")
        elif board.is_stalemate():
            info_lines.append("")
            info_lines.append("[bold yellow]⚠ ПАТ! Нічия.[/bold yellow]")

        # Показуємо підказки
        if show_hints and best_moves and len(best_moves) > 0:
            info_lines.append("")
            info_lines.append("[bold cyan]💡 Підказки (кращі ходи):[/bold cyan]")
            for i, hint_data in enumerate(best_moves[:3], 1):
                # Підтримка старого формату (просто рядок) та нового (словник)
                if isinstance(hint_data, dict):
                    hint_move = hint_data.get("move")
                    score = hint_data.get("score")
                    mate = hint_data.get("mate")
                else:
                    hint_move = hint_data
                    score = None
                    mate = None

                formatted_hint = self._format_move_with_description(board, hint_move)

                # Додаємо метрики та пояснення
                score_num, score_text, score_color = self._explain_score(score, mate)
                info_lines.append(
                    f"   {i}. [green]{formatted_hint}[/green] "
                    f"[dim]│[/dim] [{score_color}]{score_num}[/{score_color}] [dim]({score_text})[/dim]"
                )

        # Виводимо панель з інформацією
        info_panel = Panel(
            "\n".join(info_lines),
            border_style="cyan",
            title="[bold]📊 Інформація про гру[/bold]",
            title_align="left",
            width=80  # Обмежена ширина панелі
        )
        console.print(info_panel)

        # Генеруємо та показуємо PNG зображення
        if GRAPHICS_AVAILABLE:
            try:
                temp_dir = tempfile.gettempdir()
                board_file = os.path.join(temp_dir, 'chessbot_board.png')

                # Генеруємо PNG кожного разу (щоб оновити)
                if self.save_as_png(board, board_file, player_color, move, size=600):
                    # Спробуємо показати в терміналі через різні методи
                    image_shown = self._show_terminal_image(board_file)

                    if image_shown:
                        # Успішно показали в терміналі - виходимо
                        return
                    else:
                        # Якщо не вдалося показати в терміналі, відкриваємо в Preview
                        self._open_in_preview(board_file)
                        console.print("[dim]📷 PNG зображення відкрито в Preview (автооновлення)[/dim]\n")
                        return  # Не показуємо консольну дошку

            except Exception as e:
                pass

        # Fallback - показуємо консольну дошку
        console.print("[yellow]⚠ Не вдалося згенерувати PNG. Показуємо консольну візуалізацію.[/yellow]")
        self.display(board, player_color, move)

    def _open_in_preview(self, image_path: str):
        """Відкриває зображення в Preview (macOS) який автоматично оновлюється"""
        try:
            import subprocess
            system = platform.system()

            if system == 'Darwin':  # macOS
                # Використовуємо open з Preview - воно автоматично оновлює файл
                subprocess.Popen(['open', '-a', 'Preview', image_path],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            elif system == 'Linux':
                # Для Linux - пробуємо різні переглядачі
                for viewer in ['eog', 'feh', 'gwenview', 'xdg-open']:
                    try:
                        subprocess.Popen([viewer, image_path],
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)
                        break
                    except FileNotFoundError:
                        continue
            elif system == 'Windows':
                subprocess.Popen(['start', '', image_path], shell=True,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def _show_terminal_image(self, image_path: str) -> bool:
        """
        Показує PNG зображення прямо в терміналі

        Підтримка:
        - iTerm2 (macOS)
        - Kitty
        - Fallback: консольна візуалізація

        Returns:
            True якщо вдалося показати зображення
        """
        import base64
        import os

        try:
            # Спробуємо iTerm2
            if os.environ.get('TERM_PROGRAM') == 'iTerm.app':
                with open(image_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('ascii')
                print(f"\033]1337;File=inline=1;width=600px;preserveAspectRatio=1:{image_data}\a")
                print()  # Додаємо порожній рядок після зображення
                return True

            # Спробуємо Kitty
            if 'kitty' in os.environ.get('TERM', '').lower():
                # Kitty graphics protocol
                with open(image_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('ascii')
                # Kitty protocol: https://sw.kovidgoyal.net/kitty/graphics-protocol/
                print(f"\033_Gf=100,a=T,t=d;{image_data}\033\\")
                print()
                return True

        except Exception as e:
            pass

        return False


    def _get_piece_name(self, piece: chess.Piece) -> str:
        """Повертає українську назву фігури"""
        piece_names = {
            chess.PAWN: "Пішак",
            chess.KNIGHT: "Кінь",
            chess.BISHOP: "Слон",
            chess.ROOK: "Тура",
            chess.QUEEN: "Ферзь",
            chess.KING: "Король"
        }
        color = "Білий" if piece.color == chess.WHITE else "Чорний"
        return f"{color} {piece_names[piece.piece_type]}"

    def _get_piece_type_name(self, piece_type: int, case: str = "nominative") -> str:
        """
        Повертає українську назву типу фігури

        Args:
            piece_type: Тип фігури
            case: Відмінок - "nominative" (називний) або "genitive" (родовий)
        """
        if case == "genitive":
            # Родовий відмінок (кого? чого?) - для захоплених фігур
            piece_names = {
                chess.PAWN: "Пішака",
                chess.KNIGHT: "Коня",
                chess.BISHOP: "Слона",
                chess.ROOK: "Туру",
                chess.QUEEN: "Ферзя",
                chess.KING: "Короля"
            }
        else:
            # Називний відмінок (хто? що?) - за замовчуванням
            piece_names = {
                chess.PAWN: "Пішак",
                chess.KNIGHT: "Кінь",
                chess.BISHOP: "Слон",
                chess.ROOK: "Тура",
                chess.QUEEN: "Ферзь",
                chess.KING: "Король"
            }
        return piece_names.get(piece_type, "Фігуру" if case == "genitive" else "Фігура")

    def _explain_score(self, score: float = None, mate: int = None) -> tuple:
        """
        Пояснює оцінку позиції українською

        Args:
            score: Оцінка в пішаках (позитивне = перевага, негативне = відставання)
            mate: Кількість ходів до мату (позитивне = ми матуємо, негативне = нас матують)

        Returns:
            Кортеж (числова_метрика, текстове_пояснення, колір)
        """
        if mate is not None:
            if mate > 0:
                return f"М{mate}", f"мат через {mate} ход{'ів' if mate > 1 else ''}", "red bold"
            else:
                return f"М{abs(mate)}", f"мат через {abs(mate)} ход{'ів' if abs(mate) > 1 else ''}", "red bold"

        if score is None:
            return "?", "невідомо", "dim"

        # Форматуємо числове значення
        score_str = f"{score:+.1f}"

        # Визначаємо текстове пояснення та колір
        if score >= 3.0:
            return score_str, "велика перевага", "green bold"
        elif score >= 1.0:
            return score_str, "перевага", "green"
        elif score >= 0.3:
            return score_str, "невелика перевага", "cyan"
        elif score >= -0.3:
            return score_str, "рівна позиція", "white"
        elif score >= -1.0:
            return score_str, "невелике відставання", "yellow"
        elif score >= -3.0:
            return score_str, "відставання", "red"
        else:
            return score_str, "велике відставання", "red bold"

    def _format_move_with_description(self, board: chess.Board, move_san: str) -> str:
        """
        Форматує хід з людською назвою

        Args:
            board: Об'єкт шахової дошки
            move_san: Хід у SAN нотації

        Returns:
            Відформатований рядок типу "e4 (пішак на e4)"
        """
        try:
            # Парсимо SAN нотацію в Move об'єкт
            move = board.parse_san(move_san)

            # Отримуємо інформацію про хід
            from_square = chess.square_name(move.from_square)
            to_square = chess.square_name(move.to_square)
            piece = board.piece_at(move.from_square)

            if not piece:
                return move_san

            piece_name = self._get_piece_type_name(piece.piece_type).lower()

            # Спеціальні випадки
            if move_san == "O-O":
                return f"{move_san} (коротка рокіровка)"
            elif move_san == "O-O-O":
                return f"{move_san} (довга рокіровка)"

            # Перевіряємо чи це взяття
            is_capture = board.is_capture(move)

            if is_capture:
                captured_piece = board.piece_at(move.to_square)
                if captured_piece:
                    # Використовуємо родовий відмінок для захопленої фігури
                    captured_name = self._get_piece_type_name(captured_piece.piece_type, case="genitive").lower()
                    return f"{move_san} ({piece_name} б'є {captured_name} на {to_square})"
                else:
                    return f"{move_san} ({piece_name} б'є на {to_square})"
            else:
                return f"{move_san} ({piece_name} на {to_square})"

        except Exception:
            # Якщо не вдалося розпарсити, повертаємо як є
            return move_san

    def get_move_ukrainian_description(self, board: chess.Board, move: chess.Move) -> str:
        """
        Конвертує хід в українську анотацію

        Args:
            board: Об'єкт шахової дошки (до ходу!)
            move: Хід для опису

        Returns:
            Українська анотація типу "Кінь на g3, шах!"
        """
        try:
            # Отримуємо SAN нотацію
            move_san = board.san(move)

            # Отримуємо інформацію про фігуру
            piece = board.piece_at(move.from_square)
            if not piece:
                return move_san

            to_square = chess.square_name(move.to_square)
            piece_name = self._get_piece_type_name(piece.piece_type)

            # Спеціальні випадки - рокіровка
            if move_san == "O-O":
                return "Коротка рокіровка"
            elif move_san == "O-O-O":
                return "Довга рокіровка"

            # Перевіряємо чи це взяття
            is_capture = board.is_capture(move)

            # Формуємо основну частину опису
            if is_capture:
                captured_piece = board.piece_at(move.to_square)
                if captured_piece:
                    captured_name = self._get_piece_type_name(captured_piece.piece_type, case="genitive")
                    description = f"{piece_name} б'є {captured_name} на {to_square}"
                else:
                    description = f"{piece_name} б'є на {to_square}"
            else:
                description = f"{piece_name} на {to_square}"

            # Додаємо шах або мат
            if '#' in move_san:
                description += ", мат!"
            elif '+' in move_san:
                description += ", шах!"

            return description

        except Exception:
            return move_san

    def generate_svg(self, board: chess.Board, player_color: chess.Color = chess.WHITE,
                     last_move: chess.Move = None, size: int = 400) -> str:
        """
        Генерує SVG зображення дошки

        Args:
            board: Об'єкт шахової дошки
            player_color: Колір гравця для орієнтації дошки
            last_move: Останній зроблений хід для підсвітки
            size: Розмір зображення в пікселях

        Returns:
            SVG зображення у вигляді рядка
        """
        return chess.svg.board(
            board=board,
            orientation=player_color,
            lastmove=last_move,
            size=size
        )

    def save_as_png(self, board: chess.Board, filename: str,
                    player_color: chess.Color = chess.WHITE,
                    last_move: chess.Move = None, size: int = 400) -> bool:
        """
        Зберігає дошку як PNG файл

        Args:
            board: Об'єкт шахової дошки
            filename: Шлях до файлу для збереження
            player_color: Колір гравця для орієнтації дошки
            last_move: Останній зроблений хід для підсвітки
            size: Розмір зображення в пікселях

        Returns:
            True якщо успішно, False якщо графіка недоступна
        """
        if not GRAPHICS_AVAILABLE:
            print(f"{Fore.YELLOW}⚠ Графічна бібліотека недоступна. Встановіть: pip install cairosvg Pillow{Style.RESET_ALL}")
            return False

        try:
            # Генерація SVG
            svg_data = self.generate_svg(board, player_color, last_move, size)

            # Конвертація SVG → PNG
            png_data = cairosvg.svg2png(bytestring=svg_data.encode('utf-8'))

            # Збереження у файл
            with open(filename, 'wb') as f:
                f.write(png_data)

            return True

        except Exception as e:
            print(f"{Fore.RED}✗ Помилка збереження PNG: {e}{Style.RESET_ALL}")
            return False

    def get_png_bytes(self, board: chess.Board, player_color: chess.Color = chess.WHITE,
                      last_move: chess.Move = None, size: int = 400) -> Optional[bytes]:
        """
        Повертає PNG зображення дошки як байти (для Discord або інших API)

        Args:
            board: Об'єкт шахової дошки
            player_color: Колір гравця для орієнтації дошки
            last_move: Останній зроблений хід для підсвітки
            size: Розмір зображення в пікселях

        Returns:
            PNG дані як байти або None при помилці
        """
        if not GRAPHICS_AVAILABLE:
            return None

        try:
            # Генерація SVG
            svg_data = self.generate_svg(board, player_color, last_move, size)

            # Конвертація SVG → PNG
            png_data = cairosvg.svg2png(bytestring=svg_data.encode('utf-8'))

            return png_data

        except Exception as e:
            print(f"{Fore.RED}✗ Помилка генерації PNG: {e}{Style.RESET_ALL}")
            return None

    def save_svg(self, board: chess.Board, filename: str,
                 player_color: chess.Color = chess.WHITE,
                 last_move: chess.Move = None, size: int = 400) -> bool:
        """
        Зберігає дошку як SVG файл

        Args:
            board: Об'єкт шахової дошки
            filename: Шлях до файлу для збереження
            player_color: Колір гравця для орієнтації дошки
            last_move: Останній зроблений хід для підсвітки
            size: Розмір зображення в пікселях

        Returns:
            True якщо успішно, False при помилці
        """
        try:
            svg_data = self.generate_svg(board, player_color, last_move, size)

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(svg_data)

            return True

        except Exception as e:
            print(f"{Fore.RED}✗ Помилка збереження SVG: {e}{Style.RESET_ALL}")
            return False
