"""
Stock Market Simulator
README:
    Please install prettytable before running this script:
    `pip install prettytable`

USAGE:
    python stock.py [number of stocks (default: 10)]

MISC:
    Formatting: Black
    Linting: PyCharm and Pylint

Hobby project, nothing serious here
"""

import random
import sys

import prettytable

# year-month-day-version
VERSION = "2024.01.25-4"
# how many decimal places we want the stock price & percentage change to have
PRECISION = 1


def pseudo_norm() -> float:
    """Generate a value between 1-10000 in a normal distribution"""
    # https://stackoverflow.com/a/70780909
    # count is the number of dice rolls
    count = random.randint(1, 6) * random.randint(1, 6)
    # Central Limit Theorem
    # Sum of 2 dice rolls is similar to a normal distribution
    # 10000 because we want more precision for stock price change
    # e.g. +1.14%
    values = sum((random.randint(1, 10000) for _ in range(count)))
    # return the average of the values
    return values / count


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
    # Generate 3 character name, e.g. 'ABC' 'XYZ' 'BYD'
    # 65-90 is A-Z in ASCII
    final_name = [chr(random.randint(65, 90)) for _ in range(3)]
    # Append the ending
    final_name += random.choice(list_of_endings)
    # Easter egg
    # 1/30 chance of appearing
    if random.randint(1, 30) == 1:
        # instead of a random name, we pick a funny name from the list below
        final_name = random.choice(["GameStop", "Eric15342335", "原神，启动！"])
    # Join the strings inside the list final_name
    # return the name as a string
    return "".join(final_name)


class Stock:
    """Stock class representing a real life stock with price, (player) inventory,
    and price history"""

    def __init__(self, order: int) -> None:
        """Set stock price, initialize inventory count, stock history, stock name"""
        # Generate a stock starting price
        # We want stock price above 100 to appear less often
        # so there is a nested random.uniform
        self.price = round(random.uniform(10, random.uniform(100, 200)), PRECISION)
        # No starting stock
        self.inventory = 0
        # Stock.history is a list of stock prices
        # where [-1] is the most recent price
        self.history = [self.price]
        # index is used for buying stocks
        # and simplify a lot of things
        self.index = order
        # Generate a random stock name
        self.name = get_random_name()

    def purchase_test(self, amount: int, balance: float) -> bool:
        """Return True if player has enough money to buy {amount} stocks"""
        # note: if amount is negative, it means player is selling,
        # so we need to check if player has enough stock to sell
        if amount < 0:
            return self.inventory >= -amount
        return balance - self.actual_price(amount) >= 0

    def sell_test(self, amount: int, balance: float) -> bool:
        """Just an alias of Stock.purchase_test()"""
        return self.purchase_test(amount, balance)

    def actual_price(self, amount: int) -> float:
        """Return actual price of {amount} stocks, including trading fees"""
        return amount * self.price * (1 + STOCK_TRADE_FEE_PERCENTAGE / 100)

    def purchase(
            self, amount: int, balance: float, trading_fees_percentage: float
    ) -> tuple[float, float]:
        """Deduct money and increase inventory, and return new balance value
        Warning! This assumes player has enough money to purchase!
        You should use Stock.purchase_test() or Stock.sell_Test() before using this function!"""
        # Increase stock count in inventory
        assert amount != 0, "Amount cannot be 0!"
        assert amount.is_integer(), "Amount must be an integer!"
        self.inventory += amount
        if amount < 0:
            # If amount is negative, it means player is selling,
            # so we need to change the sign of trading_fees_percentage
            # otherwise the player will get more money than the stock value
            # Instead of losing money when selling a stock
            trading_fees_percentage = -trading_fees_percentage
        fee_cost = round(amount * self.price * trading_fees_percentage / 100, PRECISION)
        # return the fee_cost for display trading fees to player
        return (
            balance - amount * self.price - fee_cost,
            fee_cost,
        )

    def get_affordance(self, balance: float) -> int:
        """Return amount of stock that can be bought with current balance"""
        # Since we introduced trading fees, we need to calculate the actual price
        # int() is used to round down the value
        return int(balance / self.actual_price(1))

    def next_day(self) -> None:
        """Generate new stock price based on current stock price
        the new stock price is a random value between -50% and 50% of the current stock price"""
        self.price += round(self.price * (pseudo_norm() - 5000) / 10000, PRECISION)
        # Boundary checking
        # Well...
        assert self.price > 0, "Stock price cannot be negative!"
        # Insert new stock price into stock history
        self.update_stock_history()

    def update_stock_history(self) -> list:
        """Insert current stock value into its history list"""
        # Insert new stock price as the end of the list [-1]
        self.history += [self.price]
        # If someone wants to see the history of the stock
        # Here it is
        return self.history

    def get_average_price(self, days: int) -> float:
        """Return average stock value of the most recent {days} days"""
        # If stock history is shorter than {days}, return average of all stock history
        if days > len(self.history):
            days = len(self.history)
        # First, revert the list using [::-1]
        # Next, get the first {days} elements using [0:days]
        return round(sum(self.history[::-1][0:days]) / days, PRECISION)

    def get_price_change(self) -> tuple[float, float]:
        """Return change in price and percentage change in price"""
        # If stock history is shorter than 2 days, return 0
        # No price change so
        if len(self.history) < 2:
            return 0, 0
        # Numerical change
        change = self.history[-1] - self.history[-2]
        # Percentage change
        percentage = change / self.history[-2]
        assert percentage < 1, "Percentage change cannot be greater than 1!"
        assert percentage > -1, "Percentage change cannot be less than -1!"
        # Return rounded values
        return round(change, PRECISION), round(percentage * 100, PRECISION)


# Game settings
# How many stocks to choose?
STOCK_COUNT = 10
# Starting money
MONEY = 1000
# Stock trading fees in percentage
STOCK_TRADE_FEE_PERCENTAGE = 0.1
# support command line argument $1 for STOCK_COUNT
if len(sys.argv) == 2:
    STOCK_COUNT = int(sys.argv[1])

# initialize stock
# \n looks ugly
print()
print("Initializing game....")

# Initialize all Stocks object and put them into a list
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
    """Display stock information table
    We put it into a separate function because It is used in both
    next-day and display command"""
    print("Current stock price:")
    # See prettytable manual for explanation
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
    # for each stock
    for stock_objects in stock_list_variable:
        # reduce the variable length
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
        # match case is a new feature
        # so use it
        match inputted_command:
            # note: | stands for OR
            # Allows user to type shorter commands
            case "BUY" | "B":
                stock_to_buy = int(input("Input stock index to buy: "))
                amount_to_buy = int(input("Input amount of stock to buy: "))
                # See Stock.purchase_test() for explanation
                if stock_list[stock_to_buy - 1].purchase_test(amount_to_buy, MONEY):
                    MONEY, fee_deducted = stock_list[stock_to_buy - 1].purchase(
                        amount_to_buy, MONEY, STOCK_TRADE_FEE_PERCENTAGE
                    )
                    print(
                        f"Successfully bought {amount_to_buy} stock(s)!",
                        f"Paid {fee_deducted} for trading fees.",
                    )
                else:
                    print("You do not have enough money to buy!")
            case "SELL" | "S":
                stock_to_sell = int(input("Input stock index to sell: "))
                amount_to_sell = int(input("Input amount of stock to sell: "))
                if stock_list[stock_to_sell - 1].sell_test(amount_to_sell, MONEY):
                    MONEY, fee_deducted = stock_list[stock_to_sell - 1].purchase(
                        0 - amount_to_sell, MONEY, STOCK_TRADE_FEE_PERCENTAGE
                    )
                    print(
                        f"Successfully sold {amount_to_sell} stock(s)!",
                        f"Paid {fee_deducted} for trading fees.",
                    )
                else:
                    print("You do not have enough stock to sell!")
            case "INVENTORY" | "INV":
                # I think we can remove this part of code in newer versions
                # Since the user can use DISPLAY command to view inventory
                # This is redundant
                # But I will keep it here for now
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
                # Break the loop to display information table again
                break
            case "DISPLAY" | "D":
                display_stock_information_table(stock_list, MONEY)
            case "HELP" | "H":
                # Display explanation of commands
                # and their aliases
                print("BUY/B: Buy stock")
                print("SELL/S: Sell stock")
                print("INVENTORY/INV: View inventory")
                print("NEXT-DAY/ND: Go to next day")
                print("DISPLAY/D: Display stock information")
                print("HELP/H: View help")
            case _:
                print("Invalid command!")
