
from lotto.models import Lotto

if __name__ == '__main__':
    lotto = Lotto()

    if not lotto.read_config():
        exit(0)

    while lotto.init_round():
        lotto.deal_cards()
        lotto.show_cards()
        while lotto.check_barrel():
            lotto.show_cards()
        lotto.show_winners_cards()


