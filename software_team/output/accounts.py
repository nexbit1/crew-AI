from datetime import datetime
from typing import Dict, List, Any, Optional

class AccountError(Exception):
    pass

class InsufficientFundsError(AccountError):
    pass

class InsufficientHoldingsError(AccountError):
    pass

class InvalidQuantityError(AccountError):
    pass

class UnknownSymbolError(AccountError):
    pass

class Transaction:
    def __init__(self, transaction_type: str, timestamp: datetime, symbol: Optional[str], quantity: Optional[float], price: Optional[float], amount: float):
        self.transaction_type = transaction_type
        self.timestamp = timestamp
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.amount = amount

    def __repr__(self):
        return f"Transaction(type={self.transaction_type}, timestamp={self.timestamp}, symbol={self.symbol}, quantity={self.quantity}, price={self.price}, amount={self.amount})"

TEST_PRICES = {
    "RELIANCE": 2300.00,
    "TCS": 3500.00,
    "INFY": 1800.00,
    "HDFCBANK": 1600.00
}

def get_share_price(symbol: str) -> float:
    symbol = symbol.upper()
    if symbol not in TEST_PRICES:
        raise UnknownSymbolError(f"Unknown symbol: {symbol}")
    return TEST_PRICES[symbol]

class Account:
    def __init__(self, owner: str, initial_deposit: float, account_id: Optional[str] = None) -> None:
        if initial_deposit <= 0:
            raise InvalidQuantityError("Initial deposit must be greater than zero.")
        self.account_id = account_id if account_id else f"ACC-{id(self)}"
        self.owner = owner
        self.balance = initial_deposit
        self.initial_deposit = initial_deposit
        self.holdings = {}
        self.transactions = []
        self.transactions.append(Transaction("DEPOSIT", datetime.now(), None, None, None, initial_deposit))

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise InvalidQuantityError("Deposit amount must be greater than zero.")
        self.balance += amount
        self.transactions.append(Transaction("DEPOSIT", datetime.now(), None, None, None, amount))

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise InvalidQuantityError("Withdrawal amount must be greater than zero.")
        if self.balance - amount < 0:
            raise InsufficientFundsError("Insufficient funds for withdrawal.")
        self.balance -= amount
        self.transactions.append(Transaction("WITHDRAW", datetime.now(), None, None, None, amount))

    def buy(self, symbol: str, quantity: float) -> None:
        symbol = symbol.upper()
        if quantity <= 0:
            raise InvalidQuantityError("Quantity must be greater than zero.")
        price = get_share_price(symbol)
        total_cost = price * quantity
        if self.balance < total_cost:
            raise InsufficientFundsError("Insufficient funds to buy shares.")
        self.balance -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        self.transactions.append(Transaction("BUY", datetime.now(), symbol, quantity, price, total_cost))

    def sell(self, symbol: str, quantity: float) -> None:
        symbol = symbol.upper()
        if quantity <= 0:
            raise InvalidQuantityError("Quantity must be greater than zero.")
        current_holdings = self.holdings.get(symbol, 0)
        if current_holdings < quantity:
            raise InsufficientHoldingsError("Insufficient holdings to sell shares.")
        price = get_share_price(symbol)
        total_proceeds = price * quantity
        self.holdings[symbol] = current_holdings - quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        self.balance += total_proceeds
        self.transactions.append(Transaction("SELL", datetime.now(), symbol, quantity, price, total_proceeds))

    def get_portfolio_value(self) -> float:
        return sum(self.holdings.get(symbol, 0) * get_share_price(symbol) for symbol in self.holdings)

    def get_total_value(self) -> float:
        return self.get_portfolio_value() + self.balance

    def get_profit_loss(self) -> float:
        return self.get_total_value() - self.initial_deposit

    def report_holdings(self) -> Dict[str, float]:
        return dict(self.holdings)

    def list_transactions(self) -> List[Transaction]:
        return list(self.transactions)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "account_id": self.account_id,
            "owner": self.owner,
            "balance": self.balance,
            "holdings": self.holdings,
            "total_value": self.get_total_value(),
            "profit_loss": self.get_profit_loss(),
            "transactions": self.list_transactions()
        }