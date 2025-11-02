"""
Модуль для парсингу ходів у людській мові
"""
import chess
import re
import config
from typing import Optional, List


class MoveParser:
    """Клас для розпізнавання ходів у різних форматах"""

    def __init__(self):
        self.piece_names = config.PIECE_NAMES_UK
        # Мапінг українських літер до англійських (для координат дошки)
        self.cyrillic_to_latin = {
            'а': 'a', 'А': 'A',
            'б': 'b', 'Б': 'B',
            'с': 'c', 'С': 'C',
            'д': 'd', 'Д': 'D',
            'е': 'e', 'Е': 'E',
            'ф': 'f', 'Ф': 'F',
            'г': 'g', 'Г': 'G',
            'х': 'h', 'Х': 'H'
        }

    def _convert_cyrillic_to_latin(self, text: str) -> str:
        """
        Конвертує схожі кириличні літери в латинські для координат

        Args:
            text: Текст з можливими кириличними літерами

        Returns:
            Текст з латинськими літерами
        """
        result = text
        for cyr, lat in self.cyrillic_to_latin.items():
            result = result.replace(cyr, lat)
        return result

    def parse_move(self, move_text: str, board: chess.Board) -> Optional[chess.Move]:
        """
        Розпізнає хід з тексту в різних форматах

        Args:
            move_text: Текст ходу (e4, e2-e4, пішак на e4, тощо)
            board: Поточний стан дошки

        Returns:
            Об'єкт ходу або None, якщо не вдалося розпізнати
        """
        move_text = move_text.strip()

        # Конвертуємо українські літери в англійські для координат
        move_text = self._convert_cyrillic_to_latin(move_text)

        # Спроба 0: Рокіровка українською
        move = self._try_castling_ukrainian(move_text, board)
        if move:
            return move

        # Спроба 1: Стандартна шахова нотація (e4, Nf3, O-O) - до lower()
        move = self._try_standard_notation(move_text, board)
        if move:
            return move

        # Тепер конвертуємо в нижній регістр для решти спроб
        move_text = move_text.lower()

        # Спроба 2: UCI формат (e2e4, e7e5)
        move = self._try_uci_notation(move_text, board)
        if move:
            return move

        # Спроба 3: Людська мова ("пішак на e4", "кінь на f3")
        move = self._try_human_language(move_text, board)
        if move:
            return move

        # Спроба 4: Формат з дефісом (e2-e4, g1-f3)
        move = self._try_dash_notation(move_text, board)
        if move:
            return move

        return None

    def _try_castling_ukrainian(self, move_text: str, board: chess.Board) -> Optional[chess.Move]:
        """Спроба розпізнати рокіровку українською"""
        move_text_lower = move_text.lower()

        # Словник українських назв рокіровок
        castling_names = {
            'коротка рокіровка': 'O-O',
            'рокіровка коротка': 'O-O',
            'мала рокіровка': 'O-O',
            'рокіровка': 'O-O',  # За замовчуванням коротка
            'довга рокіровка': 'O-O-O',
            'рокіровка довга': 'O-O-O',
            'велика рокіровка': 'O-O-O',
        }

        for uk_name, san_notation in castling_names.items():
            if uk_name in move_text_lower:
                try:
                    return board.parse_san(san_notation)
                except:
                    pass

        return None

    def _try_standard_notation(self, move_text: str, board: chess.Board) -> Optional[chess.Move]:
        """Спроба розпізнати стандартну шахову нотацію (SAN)"""
        # Пробуємо різні варіанти капіталізації
        variants = [
            move_text,  # Як є
            move_text.capitalize(),  # Перша буква велика
            move_text.upper(),  # Все великими (для O-O)
        ]

        for variant in variants:
            try:
                move = board.parse_san(variant)
                if move:
                    return move
            except:
                continue

        return None

    def _try_uci_notation(self, move_text: str, board: chess.Board) -> Optional[chess.Move]:
        """Спроба розпізнати UCI нотацію (e2e4)"""
        try:
            move = chess.Move.from_uci(move_text)
            if move in board.legal_moves:
                return move
        except:
            pass
        return None

    def _try_dash_notation(self, move_text: str, board: chess.Board) -> Optional[chess.Move]:
        """Спроба розпізнати нотацію з дефісом (e2-e4)"""
        if '-' in move_text:
            parts = move_text.split('-')
            if len(parts) == 2:
                from_square = parts[0].strip()
                to_square = parts[1].strip()
                try:
                    move = chess.Move.from_uci(from_square + to_square)
                    if move in board.legal_moves:
                        return move
                except:
                    pass
        return None

    def _try_human_language(self, move_text: str, board: chess.Board) -> Optional[chess.Move]:
        """
        Спроба розпізнати людську мову
        Формати: "пішак на e4", "кінь з g1 на f3", "e4", "кінь f3", "кінь з b на c3"
        """
        original_text = move_text

        # Шукаємо назву фігури
        piece_type = None
        for name, symbol in self.piece_names.items():
            if name in move_text:
                piece_type = symbol
                move_text = move_text.replace(name, '').strip()
                break

        # Якщо не знайшли фігуру, припускаємо що це пішак
        if piece_type is None:
            piece_type = 'P'

        # Видаляємо слова "на", "з", "в"
        move_text = move_text.replace('на', ' ').replace('з', ' ').replace('в', ' ').strip()

        # Шукаємо клітинки (літера + цифра)
        squares = re.findall(r'[a-h][1-8]', move_text)

        if len(squares) == 1:
            # Маємо лише цільову клітинку
            to_square = squares[0]
            return self._find_move_by_piece_and_target(board, piece_type, to_square)

        elif len(squares) == 2:
            # Маємо обидві клітинки: з якої на яку
            from_square = squares[0]
            to_square = squares[1]
            try:
                move = chess.Move.from_uci(from_square + to_square)
                if move in board.legal_moves:
                    return move
            except:
                pass

        return None

    def _find_move_by_piece_and_target(self, board: chess.Board,
                                        piece_symbol: str, to_square_name: str) -> Optional[chess.Move]:
        """
        Знаходить хід за типом фігури та цільовою клітинкою

        Args:
            board: Дошка
            piece_symbol: Символ фігури (P, N, B, R, Q, K)
            to_square_name: Назва цільової клітинки (e4, f3, тощо)

        Returns:
            Хід або None (якщо неоднозначність - повертає None і виводить помилку)
        """
        # Конвертуємо символ у тип фігури
        piece_map = {
            'P': chess.PAWN,
            'N': chess.KNIGHT,
            'B': chess.BISHOP,
            'R': chess.ROOK,
            'Q': chess.QUEEN,
            'K': chess.KING
        }

        piece_type = piece_map.get(piece_symbol.upper())
        if piece_type is None:
            return None

        try:
            to_square = chess.parse_square(to_square_name)
        except:
            return None

        # Знаходимо всі можливі ходи цієї фігури на цільову клітинку
        possible_moves = []
        for move in board.legal_moves:
            if move.to_square == to_square:
                piece = board.piece_at(move.from_square)
                if piece and piece.piece_type == piece_type and piece.color == board.turn:
                    possible_moves.append(move)

        # Якщо знайдено рівно один хід - повертаємо його
        if len(possible_moves) == 1:
            return possible_moves[0]

        # Якщо знайдено декілька ходів - неоднозначність
        if len(possible_moves) > 1:
            from colorama import Fore, Style
            print(f"{Fore.YELLOW}⚠ Неоднозначний хід! Вкажіть точніше:{Style.RESET_ALL}")
            for move in possible_moves:
                san = board.san(move)
                from_sq = chess.square_name(move.from_square)
                print(f"   • {Fore.GREEN}{san}{Style.RESET_ALL} (з {from_sq})")
            print(f"{Fore.CYAN}💡 Підказка: Введіть '{board.san(possible_moves[0])}' або '{chess.square_name(possible_moves[0].from_square)}-{to_square_name}'{Style.RESET_ALL}")
            return None

        return None

    def get_move_suggestions(self, board: chess.Board, partial_text: str = "") -> List[str]:
        """
        Отримує список можливих ходів для підказок

        Args:
            board: Поточний стан дошки
            partial_text: Частина введеного тексту

        Returns:
            Список можливих ходів у форматі SAN
        """
        legal_moves = []
        for move in board.legal_moves:
            san = board.san(move)
            uci = move.uci()
            legal_moves.append(f"{san} ({uci})")

        return sorted(legal_moves)

    def validate_and_format_move(self, move: chess.Move, board: chess.Board) -> str:
        """
        Форматує хід для відображення

        Args:
            move: Хід
            board: Дошка

        Returns:
            Відформатований рядок ходу
        """
        return board.san(move)
