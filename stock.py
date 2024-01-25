"""
Stock Market Simulator
README:
    Please install prettytable before running this script:
    `pip install prettytable`

USAGE:
    python stock.py [number of stocks (default: 10)]

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
VERSION = "2024.01.25-3"
PRECISION = 1


def pseudo_norm():
    """Generate a value between 1-10000 in a normal distribution"""
    # https://stackoverflow.com/a/70780909
    count = random.randint(1, 6) * random.randint(1, 6)
    values = sum((random.randint(1, 10000) for _ in range(count)))
    return round(values / count)


def get_random_name() -> str:
    """Generate a random company name"""
    list_of_endings = [
        " Inc.",
        " Corp.",
        " Ltd.",
        " Co.",
        " LLC",
        " & Co.",
        " Group",
        " Holdings",
        " Corporation",
        " Company",
        " Enterprises",
        " International",
    ]
    final_name = [chr(random.randint(65, 90)) for _ in range(3)]
    final_name += random.choice(list_of_endings)
    # easter egg
    if random.randint(1, 30) == 1:
        final_name = random.choice(["GameStop", "Eric15342335", "原神，启动！"])
    return "".join(final_name)


class Stock:
    """Stock class representing a real life stock with price, (player) inventory,
    and price history"""

    def __init__(self, order: int) -> None:
        """Set stock price, initialize inventory count, stock history"""
        self.price = round(random.uniform(10, random.uniform(100, 200)), PRECISION)
        self.inventory = 0
        self.history = [self.price]
        self.index = order
        self.name = get_random_name()

    def purchase_test(self, amount: int, balance: float) -> bool:
        """Return True if player has enough money to buy {amount} stocks"""
        return balance - self.actual_price(amount) >= 0

    def actual_price(self, amount: int) -> float:
        """Return actual price of {amount} stocks"""
        return amount * self.price * (1 + STOCK_TRADE_FEE_PERCENTAGE / 100)

    def purchase(
        self, amount: int, balance: float, trading_fees_percentage: float
    ) -> tuple[float, float]:
        """Deduct money and increase inventory, and return new balance value
        Warning! This assumes player has enough money to purchase!"""
        self.inventory += amount
        if amount < 0:
            trading_fees_percentage = -trading_fees_percentage
        fee_cost = round(amount * self.price * trading_fees_percentage / 100, PRECISION)
        return (
            balance - amount * self.price * (1 + trading_fees_percentage / 100),
            fee_cost,
        )

    def get_affordance(self, balance: float) -> int:
        """Return amount of stock that can be bought with current balance"""
        return int(balance / self.actual_price(1))

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
STOCK_COUNT = 10
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
        "Index",
        "Stock name",
        "Price",
        "Change",
        "Inventory",
        "Affordable amount",
        "Avg price (5d)",
    ]
    for stock_objects in stock_list_variable:
        # formatting
        _a = stock_objects.get_price_change()
        to_be_printed.add_row(
            [
                stock_objects.index,
                stock_objects.name,
                round(stock_objects.price, PRECISION),
                f"{_a[0] if _a[0] < 0 else '+' + str(_a[0])}"
                " "
                f"({_a[1] if _a[1] < 0 else '+' + str(_a[1])}%)",
                stock_objects.inventory,
                stock_objects.get_affordance(balance),
                stock_objects.get_average_price(5),
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
            case "BUY" | "B":
                stock_to_buy = int(input("Input stock index to buy: "))
                amount_to_buy = int(input("Input amount of stock to buy: "))
                if stock_list[stock_to_buy - 1].purchase_test(amount_to_buy, MONEY):
                    MONEY, fee_deducted = stock_list[stock_to_buy - 1].purchase(
                        amount_to_buy, MONEY, STOCK_TRADE_FEE_PERCENTAGE
                    )
                    print(
                        f"Successfully bought {amount_to_buy} stock(s)!",
                        f"Paid {fee_deducted} for trading fees.",
                    )
                else:
                    print("You do not have enough MONEY to buy!")
            case "SELL" | "S":
                stock_to_sell = int(input("Input stock index to sell: "))
                amount_to_sell = int(input("Input amount of stock to sell: "))
                if amount_to_sell > stock_list[stock_to_sell - 1].inventory:
                    print("You do not have enough stock to sell!")
                else:
                    MONEY, fee_deducted = stock_list[stock_to_sell - 1].purchase(
                        0 - amount_to_sell, MONEY, STOCK_TRADE_FEE_PERCENTAGE
                    )
                    print(
                        f"Successfully sold {amount_to_sell} stock(s)!",
                        f"Paid {fee_deducted} for trading fees.",
                    )
            case "INVENTORY" | "INV":
                print(f"Your current balance is {MONEY}")
                print("Your current inventory is:")
                inventory_table = prettytable.PrettyTable()
                inventory_table.field_names = ["Stock Name", "Inventory"]
                for stocks in stock_list:
                    inventory_table.add_row([stocks.name, stocks.inventory])
                print(inventory_table)
            case "NEXT-DAY" | "ND":
                print()
                for stocks in stock_list:
                    stocks.next_day()
                break
            case "DISPLAY" | "D":
                display_stock_information_table(stock_list, MONEY)
            case "HELP" | "H":
                print("BUY/B: Buy stock")
                print("SELL/S: Sell stock")
                print("INVENTORY/INV: View inventory")
                print("NEXT-DAY/ND: Go to next day")
                print("DISPLAY/D: Display stock information")
                print("HELP/H: View help")
            case _:
                print("Invalid command!")
