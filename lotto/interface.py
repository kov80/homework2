from .constants import *


class LottoInterfaceMixin(object):
    def read_config(self):
        try:
            self.players = input('Введите от 2 до 5 неповторяющихся имен игроков через запятую '
                                 '(за игрока будет играть компьютер, если имя содержит Компьютер):\n')
            self._cards_num = int(input('Введите количество карточек на игрока (от 1 до 3, по умолчанию - 1):').strip()
                                  or '1')
            self.win_rule = int(input('Введите праввила победы (1 - заполнена строка (по умолчанию), '
                                      '2 - карточка, 3 - все карточки):').strip() or '1')
        except Exception as e:
            print(f'Ошибка конфигурации: {e}')
            return False
        return True

    @staticmethod
    def request_round(self):
        print(f'\nРаунд {self.round}')
        if self.round > 1:
            if input('Продолжить? (y):') != 'y':
                return False
        return True

    @staticmethod
    def show_barrel(self):
        print(f'Боченок: {self.cur_barrel}')

    def show_winners(self):
        sw = ', '.join(['{}' for w in self.winners])
        sp = ', '.join(['{{{i}}}: {{{i}.win_count}}'.format(i=i) for i in range(len(self.players))])
        print('Победили: ' + sw.format(*self.winners))
        print('Счет: ' + sp.format(*self.players))


class CardInterfaceMixin:
    def show(self, filled):
        for row in self._rows:
            row_10 = [''] * TENS
            for d in row:
                row_10[min(abs(d) // 10, TENS - 1)] = d
            s = ''.join(['{:>3}|' for d in row_10])
            print(('>>' if filled and self.filled_row(row) else '  ') + s.format(*row_10))
        print(' ')


class PlayerInterfaceMixin:
    def request_barrel_found(self, i):
        return input(f'{self}, зачеркнуть цифру на карточке № {i+1}? (y/n):').lower() == 'y'

    def show_name(self):
        print(f'Игрок: {self}')

    def show_looser(self):
        print('Цифра зачеркнута неверно! Вы проиграли!')

