"""
Stock Market Simulator
README:
    Please install prettytable before running this script:
    `pip install prettytable`

USAGE:
    python stock.py [number of stocks (default: 3)]

MIT License

Copyright (c) 2024 eric15342335

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
import sys

import prettytable

# year-month-day-version
VERSION = "2024.01.24-3"
PRECISION = 1


def pseudo_norm():
    """Generate a value between 1-10000 in a normal distribution"""
    # https://stackoverflow.com/a/70780909
    count = random.randint(10, 100)
    values = sum((random.randint(1, 10000) for _ in range(count)))
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
        return (
            balance - amount * self.price * (1 + STOCK_TRADE_FEE_PERCENTAGE / 100) >= 0
        )

    def purchase(
        self, amount: int, balance: float, trading_fees_percentage: float
    ) -> tuple[float, float]:
        """Deduct money and increase inventory, and return new balance value
        Warning! This assumes player has enough money to purchase!"""
        self.inventory += amount
        if amount > 0:
            trading_fees_percentage = 0 - trading_fees_percentage
        fee_deducted = amount * self.price * trading_fees_percentage / 100
        return (
            balance - amount * self.price * (1 + trading_fees_percentage / 100),
            fee_deducted,
        )

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
MONEY = 1000
STOCK_TRADE_FEE_PERCENTAGE = 0.1
if len(sys.argv) == 2:
    STOCK_COUNT = int(sys.argv[1])

# initialize stock
print()
print("Initializing game....")

stock_list = [Stock(count) for count in range(1, STOCK_COUNT + 1)]

print(f"Number of stocks: {STOCK_COUNT}")
print(f"Default money: {MONEY}")
print(f"Default precision: {PRECISION}")
print(f"Stock trading fees: {STOCK_TRADE_FEE_PERCENTAGE}%")

print()
print(f"Welcome to Stock Market Simulator {VERSION}!")


def display_stock_information_table(
    stock_list_variable: list[Stock], balance: float
) -> None:
    """Display stock information table"""
    print("Current stock price:")
    to_be_printed = prettytable.PrettyTable()
    to_be_printed.field_names = [
        "Stock name",
        "Stock price",
        "Inventory",
        "Change (%)",
        "Average price (5d)",
        "Affordable amount",
    ]
    for stock_objects in stock_list_variable:
        to_be_printed.add_row(
            [
                stock_objects.name,
                round(stock_objects.price, PRECISION),
                stock_objects.inventory,
                f"{stock_objects.get_price_change()[0]} ({stock_objects.get_price_change()[1]}%)",
                stock_objects.get_average_price(5),
                int(balance / stock_objects.price),
            ]
        )
    print(to_be_printed)
    print(f"Your current balance is {round(balance, PRECISION)}")


while True:
    display_stock_information_table(stock_list, MONEY)
    while True:
        inputted_command = input(
            "Input command (BUY, SELL, INVENTORY, NEXT-DAY, DISPLAY, HELP): "
        ).upper()
        match inputted_command:
            case "BUY":
                stock_to_buy = int(input("Input stock number to buy: "))
                amount_to_buy = int(input("Input amount of stock to buy: "))
                if stock_list[stock_to_buy - 1].purchase_test(amount_to_buy, MONEY):
                    MONEY = stock_list[stock_to_buy - 1].purchase(
                        amount_to_buy, MONEY, STOCK_TRADE_FEE_PERCENTAGE
                    )
                    print(f"Successfully bought {amount_to_buy} stock(s)!")
                else:
                    print("You do not have enough MONEY to buy!")
            case "SELL":
                stock_to_sell = int(input("Input stock number to sell: "))
                amount_to_sell = int(input("Input amount of stock to sell: "))
                if amount_to_sell > stock_list[stock_to_sell - 1].inventory:
                    print("You do not have enough stock to sell!")
                else:
                    MONEY += stock_list[stock_to_sell - 1].purchase(
                        0 - amount_to_sell, MONEY, STOCK_TRADE_FEE_PERCENTAGE
                    )
                    print(f"Successfully sold {amount_to_sell} stock(s)!")
            case "INVENTORY":
                print(f"Your current balance is {MONEY}")
                print("Your current inventory is:")
                inventory_table = prettytable.PrettyTable()
                inventory_table.field_names = ["Stock name", "Inventory"]
                for stocks in stock_list:
                    inventory_table.add_row([stocks.name, stocks.inventory])
                print(inventory_table)
            case "NEXT-DAY":
                print()
                for stocks in stock_list:
                    stocks.next_day()
                break
            case "DISPLAY":
                display_stock_information_table(stock_list, MONEY)
            case "HELP":
                print("BUY: Buy stock")
                print("SELL: Sell stock")
                print("INVENTORY: View inventory")
                print("NEXT-DAY: Go to next day")
                print("DISPLAY: Display stock information")
                print("HELP: View help")
            case _:
                print("Invalid command!")
