"""Модуль классов игры."""

import random
import logging

from .interface import LottoInterfaceMixin, PlayerInterfaceMixin, CardInterfaceMixin
from .constants import *

logger = logging.getLogger(__name__)


class Lotto(LottoInterfaceMixin):
    """Основной класс игры Лото, реализующий правила"""
    def __init__(self):
        self.cards_num = 1
        self.win_rule = 0
        self._players = {}

        self.round = 0
        self.barrels = []
        self.cur_barrel = None

    @property
    def players(self):
        """Возвращает игроков"""
        return self._players

    @players.setter
    def players(self, names):
        """Создает игроков из имен введенных при настройках игры"""
        assert not self._players, 'Игроки уже созданы'
        assert ',' in names, 'Необходим список имён игроков, разделенный запятой'

        names_list = names.split(',')
        assert len(set(names_list)) == len(names_list), 'Имена игроков не должны повторяться'

        self._players = [Player(name.strip(), 'компьютер' in name.strip().lower()) for name in names_list]

    @property
    def active_players(self):
        """Возвращает активных (не выбывших) игроков в раунде"""
        return [p for p in self._players if p.winner is not False]

    @property
    def winners(self):
        """Возвращает победивших игроков в раунде"""
        return [p for p in self._players if p.winner]

    def init_round(self):
        """Инициализация нового раунда"""
        self.barrels = list(range(1, TOTAL_NUMS + 1))  # перемешиваем боченки
        self.round += 1

        return self.request_round()

    def deal_cards(self):
        """Раздача карточек игрокам"""
        cards = Card.generate(len(self.players) * self.cards_num)  # генерация
        for i, player in enumerate(self.players):
            player.winner = None  # сброс статуса игрока
            player.cards = cards[i * self.cards_num:(i + 1) * self.cards_num]

    def select_barrel(self):
        """Выбор произвольного боченка"""
        self.cur_barrel = self.barrels.pop(random.randint(0, len(self.barrels)-1))
        self.show_barrel()

    def check_barrel(self):
        """Выбор боченка и его поиск на карточках игроков

        :return: False - если определился победитель, иначе - True
        """
        next_barrel = True
        self.select_barrel()

        # Ищем боченок у активных игроков в соответствие с правилами победы
        for player in self.active_players:
            if player.find_barrel(self.cur_barrel):
                win = False
                for i, card in enumerate(player.cards):
                    if self.win_rule == 1 and any(card.filled_rows):
                        win = True
                        break
                    elif self.win_rule > 1:
                        filled = all(card.filled_rows)
                        if filled:
                            win = True
                            if self.win_rule == 2:
                                break
                        elif self.win_rule == 3:
                            win = False
                            break
                if win:
                    player.winner = True
                    next_barrel = False

        # Если остался один игрок, досрочно завершаем раунд
        if len(self.active_players) == 1:
            self.active_players[0].winner = True
            next_barrel = False

        return next_barrel

    def show_cards(self, filled=False):
        """Показать карточки игроков"""
        for i, player in enumerate(self.active_players):
            player.show_name()
            for card in player.cards:
                card.show(filled)

    def show_winners_cards(self):
        """Показать карточки победителей раунда"""
        self.show_cards(filled=True)
        self.show_winners()


class Card(CardInterfaceMixin):
    """Класс карточки"""
    @classmethod
    def generate(cls, cards_len):
        """Генерация массива карточек

        :arg cards_len: длина массива
        """
        cards = []
        while len(cards) < cards_len:
            rows, decs = [], []
            nums = [list(range(int(i == 0), 10 + int(i == TENS - 1))) for i in range(0, TENS)]

            for j in range(ROWS_CNT):
                r = [i for i in range(0, TENS)]
                if j == 1:
                    r.remove(decs[0][0])
                elif j == 2:
                    r = [d for d in r if d not in set(decs[0]).intersection(decs[1])]
                decs.append(random.sample(r, min(ROW_NUMS, len(r))))
                rows.append(sorted([10 * dd + nums[dd].pop(random.randint(0, len(nums[dd]) - 1)) for dd in decs[j]]))

            card = Card(rows)
            if card not in cards:
                cards.append(Card(rows))

        return cards

    def __init__(self, rows):
        assert len(rows) == ROWS_CNT, f'{ROWS_CNT} rows required'
        self._rows = rows

    def __eq__(self, other):
        return self._rows == other._rows

    @staticmethod
    def filled_row(row):
        """Проверяет, что вся строка вычеркнута"""
        return all(d < 0 for d in row)

    @property
    def filled_rows(self):
        """Возвращает массив признаков полностью зачеркнутых строк"""
        result = [False] * ROWS_CNT
        for i, row in enumerate(self._rows):
            result[i] = self.filled_row(row)
        return result

    def find_barrel(self, barrel):
        """Ищет число на карточке и зачеркивает его

        :return: True - если баченок найден
        """
        for row in self._rows:
            try:
                i = row.index(barrel)
                row[i] = -row[i]
                return True
            except ValueError:
                continue
        return False


class Player(PlayerInterfaceMixin):
    """Класс игрока"""
    def __init__(self, name, computer=False):
        self.cards = []

        self.__winner = None

        self.name = name
        self.win_count = 0
        self.computer = computer

    def __str__(self):
        return self.name

    @property
    def winner(self):
        """Признак победителя в раунде

        None - неопределен
        False - проиграл, тк выбыл досрочно
        True - победил
        """
        return self.__winner

    @winner.setter
    def winner(self, win):
        """Устанавливает признак победителя в раунде с увеличение счетчика побед"""
        self.__winner = win
        if win:
            self.win_count += 1

    def find_barrel(self, barrel):
        """Поиск боченка у игрока"""
        res = False
        for i, card in enumerate(self.cards):
            found = card.find_barrel(barrel)

            # если не компьютер, то запрашиваем у игрока
            if not self.computer:
                if found != self.request_barrel_found(i):
                    self.winner = False
                    self.show_looser()
                    return False
            res = found or res
        return res
