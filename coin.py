# coin.py


class Coin:
    def __init__(self, initial_amount=0):
        self.amount = initial_amount

    def increase(self, value):
        self.amount += value

    def decrease(self, value):
        if value <= self.amount:
            self.amount -= value
        else:
            # 如果金幣不足，可以選擇引發錯誤或處理不足的情況
            print("金幣不足，無法扣除！")

    def get_amount(self):
        return self.amount
