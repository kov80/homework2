"""Модуль запуск игры"""

import logging

try:
    import pydevd
except ImportError:
    logging.basicConfig(filename='lotto.log', filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S', level=logging.DEBUG)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    from lotto.models import Lotto

    lotto = Lotto()
    try:
        lotto.read_config()

        while lotto.init_round():
            lotto.deal_cards()
            lotto.show_cards()
            while lotto.check_barrel():
                lotto.show_cards()
            lotto.show_winners_cards()
    except BaseException as e:
        logger.exception(f'{e}')
        lotto.show_exit(e)
