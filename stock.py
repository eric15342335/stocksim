"""
Stock Market Simulator
README: Please install prettytable before running this script:
        `pip install prettytable`

MIT License

Copyright (c) 2023 eric15342335

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import random

import prettytable

# year-month-day-VERSION
VERSION = "2024-01-24-1"
PRECISION = 1


def pseudo_norm():
    """Generate a value between 1-10000 in a normal distribution"""
    # https://stackoverflow.com/a/70780909
    count = 100
    values = sum([random.randint(1, 10000) for _ in range(count)])
    return round(values / count)


class Stock:
    """Stock class representing a real life stock with price, (player) inventory,
    and price history"""
    def __init__(self, order: int) -> None:
        """Set stock price, initialize inventory count, stock history"""
        self.price = round(random.uniform(10, 200), PRECISION)
        self.inventory = 0
        self.history = [self.price]
        self.name = order

    def purchase_test(self, amount: int, balance: float) -> bool:
        """Return True if player has enough money to buy {amount} stocks"""
        return balance - amount * self.price >= 0

    def purchase(self, amount: int, balance: float) -> float:
        """Deduct money and increase inventory, and return new balance value
        Warning! This assumes player has enough money to purchase!"""
        self.inventory += amount
        return balance - amount * self.price

    def next_day(self) -> None:
        """Generate new stock price base on current stock price"""
        self.price += round(self.price * (pseudo_norm() - 5000) / 10000, PRECISION)
        assert self.price > 0, "Stock price cannot be negative!"
        self.update_stock_history()

    def update_stock_history(self) -> list:
        """Insert current stock value into its history list"""
        self.history += [self.price]
        return self.history

    def get_average_price(self, days: int) -> float:
        """Return average stock value of the most recent {days} days"""
        if days > len(self.history):
            days = len(self.history)
        return round(sum(self.history[::-1][0:days]) / days, PRECISION)

    def get_price_change(self) -> tuple[float, float]:
        """Return change in price and percentage change in price"""
        if len(self.history) < 2:
            return 0, 0
        change = self.history[-1] - self.history[-2]
        percentage = change / self.history[-2]
        assert percentage < 1, "Percentage change cannot be greater than 1!"
        assert percentage > -1, "Percentage change cannot be less than -1!"
        return round(change, PRECISION), round(percentage * 100, PRECISION)


# Game settings
STOCK_COUNT = 3
money = 1000

# initialize stock
print()
print("Initializing game....")

stock_list = [Stock(count) for count in range(1, STOCK_COUNT + 1)]

print(f"Number of stocks: {STOCK_COUNT}")
print(f"Default money: {money}")

print()
print(f"Welcome to Stock Market Simulator {VERSION}!")
while True:
    print("Current stock price:")
    to_be_printed = prettytable.PrettyTable()
    to_be_printed.field_names = [
        "Stock name",
        "Stock price",
        "Inventory",
        "Change (%)",
        "Average price (5d)",
    ]
    for stocks in stock_list:
        to_be_printed.add_row(
            [
                stocks.name,
                round(stocks.price, PRECISION),
                stocks.inventory,
                f"{stocks.get_price_change()[0]} ({stocks.get_price_change()[1]}%)",
                stocks.get_average_price(5),
            ]
        )
    print(to_be_printed)
    print(f"Your current balance is {money}")
    while True:
        inputted_command = input(
            "Input command (BUY, SELL, INVENTORY, NEXT-DAY, HELP): "
        ).upper()
        match inputted_command:
            case "BUY":
                print("You have chosen to buy stock!")
                stock_to_buy = int(input("Input stock number to buy: "))
                amount_to_buy = int(input("Input amount of stock to buy: "))
                if stock_list[stock_to_buy - 1].purchase_test(amount_to_buy, money):
                    money = stock_list[stock_to_buy - 1].purchase(amount_to_buy, money)
                    print(f"Successfully bought {amount_to_buy} stock(s)!")
                else:
                    print("You do not have enough money to buy!")
            case "SELL":
                print("You have chosen to sell stock!")
                stock_to_sell = int(input("Input stock number to sell: "))
                amount_to_sell = int(input("Input amount of stock to sell: "))
                if amount_to_sell > stock_list[stock_to_sell - 1].inventory:
                    print("You do not have enough stock to sell!")
                else:
                    money += stock_list[stock_to_sell - 1].price * amount_to_sell
                    stock_list[stock_to_sell - 1].inventory -= amount_to_sell
                    print(f"Successfully sold {amount_to_sell} stock(s)!")
            case "INVENTORY":
                print("You have chosen to view inventory!")
                print(f"Your current balance is {money}")
                print("Your current inventory is:")
                to_be_printed = prettytable.PrettyTable()
                to_be_printed.field_names = ["Stock name", "Inventory"]
                for stocks in stock_list:
                    to_be_printed.add_row([stocks.name, stocks.inventory])
                print(to_be_printed)
            case "NEXT-DAY":
                print("You have chosen to go to next day!")
                for stocks in stock_list:
                    stocks.next_day()
                break
            case "HELP":
                print("You have chosen to view help!")
                print("BUY: Buy stock")
                print("SELL: Sell stock")
                print("INVENTORY: View inventory")
                print("HELP: View help")
                print("NEXT-DAY: Go to next day")
            case _:
                print("Invalid command!")
