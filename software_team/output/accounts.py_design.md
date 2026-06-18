# Design Document for accounts.py

Goal
- Provide a self-contained Python module accounts.py implementing a simple account management system for a trading simulation platform.
- Expose a single class Account (as required) with a clear, testable API.
- Include a test price provider for get_share_price(symbol) that returns fixed prices for RELIANCE, TCS, INFY, and HDFCBANK.
- Support deposits, withdrawals (with negative-balance prevention), buy/sell of shares (with balance/holding checks), portfolio value calculation, profit/loss reporting against the initial deposit, holdings reporting, and transaction history.

High-level API Overview
- Module: accounts.py
- Public class: Account
- Public function: get_share_price(symbol) -> float
- Supporting types: Transaction (data structure), custom exceptions (for clarity)

Design R1 Highlights
- Data model:
  - Each Account tracks its balance, initial_deposit, holdings, and an immutable transaction history.
  - Holdings map symbol -> quantity (float, to support fractional shares if desired).
  - Transactions capture all money movements and share trades with timestamps.
- Core behavior:
  - Deposit: increase balance, record DEPOSIT transaction.
  - Withdraw: decrease balance if sufficient funds exist; otherwise raise an exception; record WITHDRAWAL transaction.
  - Buy: ensure balance >= price(symbol) * quantity; deduct cash, increase holdings, record BUY transaction.
  - Sell: ensure holdings[symbol] >= quantity; add cash, decrease holdings, record SELL transaction.
  - Portfolio valuation: sum(symbol quantity * get_share_price(symbol)) for all holdings.
  - Total value: portfolio value + cash balance.
  - Profit/Loss (P/L): total value - initial_deposit.
  - Reports: holdings snapshot and full transaction history.
- Price feed:
  - get_share_price(symbol) returns the current price via an internal test price map for deterministic testing.
  - Unknown symbols raise a clear error.
- Validation and errors:
  - Negative or zero amounts/quantities rejected with meaningful exceptions.
  - Insufficient funds or insufficient holdings raise precise exceptions to allow UI to react gracefully.

Detailed Class and Function Signatures

1) Custom Exceptions (for clean error handling)
- class AccountError(Exception)
  - Base exception for account-related errors.

- class InsufficientFundsError(AccountError)
  - Raised when a withdrawal or purchase would overdraw the account.

- class InsufficientHoldingsError(AccountError)
  - Raised when attempting to sell more shares than owned.

- class InvalidQuantityError(AccountError)
  - Raised when quantity is not positive for operations that require positive amounts.

- class UnknownSymbolError(AccountError)
  - Raised when get_share_price is invoked with a symbol not in the known test set.

2) Data structure: Transaction
- A lightweight data container describing a single financial event.

- Signature (conceptual, to guide implementation; actual Python code may use @dataclass)
  - class Transaction:
      - type: str                   # "DEPOSIT", "WITHDRAW", "BUY", "SELL"
      - timestamp: datetime
      - symbol: Optional[str]       # e.g., "RELIANCE" for BUY/SELL, None for DEPOSIT/WITHDRAW
      - quantity: Optional[float]   # quantity for BUY/SELL, None for DEPOSIT/WITHDRAW
      - price: Optional[float]        # price per share at the time of the transaction (for BUY/SELL)
      - amount: float                 # total amount involved (for DEPOSIT/WITHDRAW: amount; for BUY: quantity*price; for SELL: quantity*price)

3) Function: get_share_price
- Public function used by Account to fetch current prices for holdings/value computation.

- Signature:
  - def get_share_price(symbol: str) -> float

- Behavior:
  - Accepts a symbol, case-insensitive.
  - Uses a built-in test price map:
    - RELIANCE -> fixed_price_ RELIANCE
    - TCS -> fixed_price_TCS
    - INFY -> fixed_price_INFY
    - HDFCBANK -> fixed_price_HDFCBANK
  - If symbol is not in the map, raise UnknownSymbolError or ValueError (preferred: UnknownSymbolError to be consistent with the exception design).
  - This function is designed to be trivially replaceable by a real price feed in production.

- Test price map (internal to accounts.py):
  - RELIANCE: 2300.00
  - TCS: 3500.00
  - INFY: 1800.00
  - HDFCBANK: 1600.00

4) Class: Account
- Purpose:
  - Represent a single user’s trading account with cash balance, holdings, and a transaction history.

- Signature:
  - class Account:
      - def __init__(self, owner: str, initial_deposit: float, account_id: Optional[str] = None) -> None
      - Optional: def __repr__(self) -> str
      - def deposit(self, amount: float) -> None
      - def withdraw(self, amount: float) -> None
      - def buy(self, symbol: str, quantity: float) -> None
      - def sell(self, symbol: str, quantity: float) -> None
      - def get_portfolio_value(self) -> float
      - def get_total_value(self) -> float
      - def get_profit_loss(self) -> float
      - def report_holdings(self) -> Dict[str, float]
      - def list_transactions(self) -> List[Transaction]
      - def to_dict(self) -> Dict[str, Any]   # optional helper for UI/testing

- Attributes (internal state):
  - account_id: str
  - owner: str
  - balance: float
  - initial_deposit: float
  - holdings: Dict[str, float]       # symbol -> quantity
  - transactions: List[Transaction]
  - created_at: datetime

- Behavior details:
  - __init__(owner, initial_deposit, account_id=None)
    - Validate initial_deposit > 0
    - Set balance = initial_deposit
    - Set initial_deposit = initial_deposit
    - Initialize holdings = {}
    - Initialize transactions with a DEPOSIT transaction reflecting the initial deposit
    - Assign account_id (auto-generated if not provided)

  - deposit(amount)
    - Validate amount > 0
    - balance += amount
    - Append Transaction(type="DEPOSIT", timestamp=now, symbol=None, quantity=None, price=None, amount=amount)

  - withdraw(amount)
    - Validate amount > 0
    - If balance - amount < 0: raise InsufficientFundsError
    - balance -= amount
    - Append Transaction(type="WITHDRAW", timestamp=now, symbol=None, quantity=None, price=None, amount=amount)

  - buy(symbol, quantity)
    - Normalize symbol to uppercase
    - Validate quantity > 0
    - price = get_share_price(symbol)
    - total_cost = price * quantity
    - If balance < total_cost: raise InsufficientFundsError
    - balance -= total_cost
    - holdings[symbol] = holdings.get(symbol, 0) + quantity
    - Append Transaction(type="BUY", timestamp=now, symbol=symbol, quantity=quantity, price=price, amount=total_cost)

  - sell(symbol, quantity)
    - Normalize symbol to uppercase
    - Validate quantity > 0
    - current = holdings.get(symbol, 0)
    - If current < quantity: raise InsufficientHoldingsError
    - price = get_share_price(symbol)
    - total_proceeds = price * quantity
    - holdings[symbol] = current - quantity
    - If holdings[symbol] == 0: remove symbol from holdings
    - balance += total_proceeds
    - Append Transaction(type="SELL", timestamp=now, symbol=symbol, quantity=quantity, price=price, amount=total_proceeds)

  - get_portfolio_value()
    - Compute sum(holdings.get(sym, 0) * get_share_price(sym) for sym in holdings)
    - Return value as float

  - get_total_value()
    - Return get_portfolio_value() + balance

  - get_profit_loss()
    - Return get_total_value() - initial_deposit

  - report_holdings()
    - Return a shallow copy of holdings (symbol -> quantity)
    - If helpful, return a sorted representation for deterministic UI.

  - list_transactions()
    - Return a list copy of self.transactions (in chronological order)

  - to_dict()
    - Return a dict capturing a snapshot of the account (id, owner, balance, holdings, total_value, profit_loss, transactions)

Notes on Time and Ordering
- Timestamps use datetime.datetime.now() at the moment of the operation.
- Transactions are appended in chronological order; UI can filter/sort if needed.

Testing and Extensibility Considerations
- In tests, you can override get_share_price via dependency injection by temporarily monkey-patching or by designing an optional price_provider hook. The core interface, however, remains get_share_price(symbol) as specified.
- To switch to a live price feed later, replace get_share_price with a real API call without changing Account’s API.
- The initial_deposit is fixed at account creation and is used as the baseline for P/L calculation as described above. Withdrawals and additional deposits affect P/L through their impact on total value.

Usage Scenarios (illustrative)
- Create account:
  - acc = Account(owner="Alice", initial_deposit=10000.0)
- Deposit:
  - acc.deposit(2000.0)
- Withdraw:
  - acc.withdraw(1500.0)
- Buy shares:
  - acc.buy("RELIANCE", 3)  # 3 shares at price from get_share_price("RELIANCE")
- Sell shares:
  - acc.sell("RELIANCE", 1)
- Portfolio value:
  - pv = acc.get_portfolio_value()
- Total value:
  - tv = acc.get_total_value()
- Profit/Loss:
  - pl = acc.get_profit_loss()
- Holdings report:
  - holdings = acc.report_holdings()
- Transactions:
  - txs = acc.list_transactions()

Notes for Implementation Plan (hand-off guidance)
- Implement Transaction as a small @dataclass for readability and equality-testing in tests.
- Implement Account with straightforward Python types; keep methods small and focused.
- Keep get_share_price in the module scope with a deterministic TEST_PRICES mapping for testing. Document that this is a test/stub price feed and that production should inject a real provider.
- Ensure error messages are clear to aid UI/CLI integration.

Representative Interfaces (concise recap)
- get_share_price(symbol: str) -> float
- class Account:
  - __init__(self, owner: str, initial_deposit: float, account_id: Optional[str] = None) -> None
  - deposit(self, amount: float) -> None
  - withdraw(self, amount: float) -> None
  - buy(self, symbol: str, quantity: float) -> None
  - sell(self, symbol: str, quantity: float) -> None
  - get_portfolio_value(self) -> float
  - get_total_value(self) -> float
  - get_profit_loss(self) -> float
  - report_holdings(self) -> Dict[str, float]
  - list_transactions(self) -> List[Transaction]
  - to_dict(self) -> Dict[str, Any]

This design provides a complete, self-contained backend API in one module (accounts.py) with a single class Account and a test-price feed function get_share_price(symbol). It satisfies all requirements:
- Account creation, deposits, withdrawals (with protection against negative balance)
- Buy/Sell with quantity handling and validation
- Portfolio value calculation and P/L relative to the initial deposit
- Holdings reporting and transaction history
- A built-in test price provider for deterministic testing with RELIANCE, TCS, INFY, and HDFCBANK

If you’d like, I can then convert this design into an actual, fully self-contained Python module (accounts.py) with concrete implementations, unit tests, and a small CLI or simple UI harness.