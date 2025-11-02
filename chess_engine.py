"""
Модуль для роботи з шаховим рушієм Stockfish
"""
import chess
import chess.engine
import config
from typing import Optional


class ChessEngine:
    """Клас для роботи з рушієм Stockfish"""

    def __init__(self, stockfish_path: str = None, skill_level: int = None,
                 depth: int = None, time_limit: float = None):
        """
        Ініціалізація рушія

        Args:
            stockfish_path: Шлях до виконуваного файлу Stockfish
            skill_level: Рівень майстерності (0-20)
            depth: Глибина аналізу
            time_limit: Час на хід
        """
        self.path = stockfish_path or config.STOCKFISH_PATH
        self.skill_level = skill_level or config.STOCKFISH_SKILL_LEVEL
        self.depth = depth or config.STOCKFISH_DEPTH
        self.time_limit = time_limit or config.STOCKFISH_TIME
        self.engine = None
        self._connect()

    def _connect(self):
        """Підключення до рушія Stockfish"""
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.path)
            # Налаштування рівня гри
            self.engine.configure({"Skill Level": self.skill_level})
            print(f"✓ Stockfish підключено успішно!")
        except FileNotFoundError:
            print(f"✗ Помилка: Stockfish не знайдено за шляхом '{self.path}'")
            print("\nБудь ласка, встановіть Stockfish:")
            print("  macOS: brew install stockfish")
            print("  Ubuntu/Debian: sudo apt-get install stockfish")
            print("  Windows: завантажте з https://stockfishchess.org/download/")
            print("\nАбо вкажіть правильний шлях у config.py")
            raise

    def set_difficulty(self, skill_level: int, depth: int, time_limit: float):
        """
        Встановлює рівень складності

        Args:
            skill_level: Рівень майстерності (0-20)
            depth: Глибина аналізу
            time_limit: Час на хід
        """
        self.skill_level = skill_level
        self.depth = depth
        self.time_limit = time_limit
        if self.engine:
            self.engine.configure({"Skill Level": skill_level})

    def get_best_move(self, board: chess.Board, time_limit: float = None) -> chess.Move:
        """
        Отримати найкращий хід від рушія

        Args:
            board: Поточний стан дошки
            time_limit: Ліміт часу на обдумування (секунди)

        Returns:
            Найкращий хід
        """
        if not self.engine:
            raise RuntimeError("Рушій не підключено")

        time = time_limit or self.time_limit

        # Отримуємо найкращий хід
        result = self.engine.play(
            board,
            chess.engine.Limit(time=time, depth=self.depth)
        )

        return result.move

    def analyze_position(self, board: chess.Board, depth: int = 15) -> dict:
        """
        Аналіз позиції

        Args:
            board: Поточний стан дошки
            depth: Глибина аналізу

        Returns:
            Словник з інформацією про позицію
        """
        if not self.engine:
            raise RuntimeError("Рушій не підключено")

        info = self.engine.analyse(board, chess.engine.Limit(depth=depth))

        # Отримуємо оцінку позиції
        score = info.get("score")
        if score:
            # Конвертуємо в пішаки
            if score.is_mate():
                evaluation = f"Мат у {abs(score.relative.moves)} ходів"
            else:
                centipawns = score.relative.score()
                pawns = centipawns / 100 if centipawns else 0
                evaluation = f"{pawns:+.2f}"
        else:
            evaluation = "Невідомо"

        return {
            "evaluation": evaluation,
            "best_move": info.get("pv", [None])[0] if "pv" in info else None,
            "depth": info.get("depth", 0)
        }

    def get_hints(self, board: chess.Board, num_hints: int = 3, depth: int = 10) -> list:
        """
        Отримати підказки - топ кращих ходів з оцінками

        Args:
            board: Поточний стан дошки
            num_hints: Кількість підказок
            depth: Глибина аналізу

        Returns:
            Список словників з ходами та оцінками:
            [{"move": "e5", "score": 0.3, "mate": None}, ...]
        """
        if not self.engine:
            raise RuntimeError("Рушій не підключено")

        try:
            # Аналізуємо позицію з multipv для отримання декількох варіантів
            info = self.engine.analyse(
                board,
                chess.engine.Limit(depth=depth),
                multipv=num_hints
            )

            hints = []
            for analysis in info:
                if "pv" in analysis and len(analysis["pv"]) > 0:
                    move = analysis["pv"][0]
                    move_san = board.san(move)

                    # Отримуємо оцінку позиції
                    score_info = analysis.get("score")
                    score_value = None
                    mate_in = None

                    if score_info:
                        if score_info.is_mate():
                            mate_in = score_info.relative.moves
                        else:
                            centipawns = score_info.relative.score()
                            if centipawns is not None:
                                score_value = centipawns / 100.0  # Конвертуємо в пішаки

                    hints.append({
                        "move": move_san,
                        "score": score_value,
                        "mate": mate_in
                    })

            return hints
        except Exception:
            # Якщо multipv не підтримується, повертаємо тільки один хід
            result = self.engine.analyse(board, chess.engine.Limit(depth=depth))
            if "pv" in result and len(result["pv"]) > 0:
                move_san = board.san(result["pv"][0])

                score_info = result.get("score")
                score_value = None
                mate_in = None

                if score_info:
                    if score_info.is_mate():
                        mate_in = score_info.relative.moves
                    else:
                        centipawns = score_info.relative.score()
                        if centipawns is not None:
                            score_value = centipawns / 100.0

                return [{
                    "move": move_san,
                    "score": score_value,
                    "mate": mate_in
                }]
            return []

    def close(self):
        """Закрити з'єднання з рушієм"""
        if self.engine:
            self.engine.quit()
            self.engine = None

    def __del__(self):
        """Деструктор - закриває рушій при видаленні об'єкта"""
        self.close()
