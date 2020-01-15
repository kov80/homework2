"""Модуль интерфейсов ввода/вывода игры."""

import logging

from .constants import *

logger = logging.getLogger(__name__)


class LottoInterfaceMixin(object):
    """Класс интерфейса ввода/вывода игры."""
    def read_config(self):
        """Ввод настроек игры."""
        try:
            self.players = input('Введите от 2 до 5 неповторяющихся имен игроков через запятую '
                                 '(за игрока будет играть компьютер, если имя содержит Компьютер):\n')
            self.cards_num = int(input('Введите количество карточек на игрока (от 1 до 3, по умолчанию - 1):').strip()
                                  or '1')
            self.win_rule = int(input('Введите праввила победы (1 - заполнена строка (по умолчанию), '
                                      '2 - карточка, 3 - все карточки):').strip() or '1')
        except Exception as e:
            raise Exception(f'Ошибка конфигурации: {e}')

    def request_round(self):
        """Запрос продолжения игры"""
        print(f'\nРаунд {self.round}')
        if self.round > 1:
            if input('Продолжить? (y/n):') != 'n':
                return True
            else:
                self.show_exit()
                return False
        return True

    def show_barrel(self):
        """Показать выбранный боченок"""
        print(f'Боченок: {self.cur_barrel}')

    def show_winners(self):
        """Показать победителей в раунде и общий счет игры"""
        if self.winners:
            sw = ', '.join(['{}' for w in self.winners])
            print(f'В раунде {self.round} победили: ' + sw.format(*self.winners))
        self.show_score()

    def show_score(self):
        """Показать общий счет игры"""
        sp = ', '.join(['{{{i}}}: {{{i}.win_count}}'.format(i=i) for i in range(len(self.players))])
        print('Общий счет: ' + sp.format(*self.players))

    def show_exit(self, error=''):
        """Показать сообщение об завершении игры"""
        print(f'\nИгра окончена. {error}')
        self.show_score()


class CardInterfaceMixin:
    """Класс интерфейса вывода карточки."""
    def show(self, filled):
        """Выводит карточку в консоль.

        :param filled: вывести указатель заполненных в карточке строк
        """
        for row in self._rows:
            row_10 = [''] * TENS
            for d in row:
                row_10[min(abs(d) // 10, TENS - 1)] = d
            s = ''.join(['{:>3}|' for d in row_10])
            print(('>>' if filled and self.filled_row(row) else '  ') + s.format(*row_10))
        print(' ')


class PlayerInterfaceMixin:
    """Класс интерфейса ввода/вывода игрока."""
    def request_barrel_found(self, i):
        """Запрашивает игрока найти чисор на карточке.

        :param i: номер карточки
        """
        return input(f'{self}, зачеркнуть цифру на карточке № {i+1}? (y/n):').lower() != 'n'

    def show_name(self):
        """Вывод имени игрока"""
        print(f'Игрок: {self}')

    def show_looser(self):
        """Вывод сообщения о проигрыше"""
        print('\nЦифра зачеркнута неверно! Вы проиграли!\n')

