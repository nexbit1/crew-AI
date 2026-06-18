import unittest
from datetime import datetime
from accounts import Account, InsufficientFundsError, InvalidQuantityError, UnknownSymbolError, InsufficientHoldingsError

class TestAccount(unittest.TestCase):
    
    def setUp(self):
        self.account = Account("Test User", 10000.0)

    def test_initial_deposit(self):
        self.assertEqual(self.account.balance, 10000.0)

    def test_deposit(self):
        self.account.deposit(5000.0)
        self.assertEqual(self.account.balance, 15000.0)

    def test_deposit_invalid(self):
        with self.assertRaises(InvalidQuantityError):
            self.account.deposit(-100.0)

    def test_withdraw(self):
        self.account.withdraw(2000.0)
        self.assertEqual(self.account.balance, 8000.0)

    def test_withdraw_insufficient_funds(self):
        with self.assertRaises(InsufficientFundsError):
            self.account.withdraw(20000.0)

    def test_withdraw_invalid(self):
        with self.assertRaises(InvalidQuantityError):
            self.account.withdraw(-100.0)

    def test_buy(self):
        self.account.buy("RELIANCE", 2)
        self.assertEqual(self.account.holdings["RELIANCE"], 2)
        self.assertEqual(self.account.balance, 10000.0 - (2 * 2300.0))

    def test_buy_insufficient_funds(self):
        self.account.withdraw(8000.0)  # Withdraw enough to leave less than the price for buying
        with self.assertRaises(InsufficientFundsError):
            self.account.buy("RELIANCE", 5)

    def test_buy_invalid_quantity(self):
        with self.assertRaises(InvalidQuantityError):
            self.account.buy("RELIANCE", -1)

    def test_sell(self):
        self.account.buy("RELIANCE", 2)
        self.account.sell("RELIANCE", 1)
        self.assertEqual(self.account.holdings["RELIANCE"], 1)
        self.assertEqual(self.account.balance, 10000.0 - (1 * 2300.0))

    def test_sell_insufficient_holdings(self):
        with self.assertRaises(InsufficientHoldingsError):
            self.account.sell("RELIANCE", 1)

    def test_sell_invalid_quantity(self):
        with self.assertRaises(InvalidQuantityError):
            self.account.sell("RELIANCE", -1)

    def test_get_portfolio_value(self):
        self.account.buy("RELIANCE", 2)
        self.assertEqual(self.account.get_portfolio_value(), 2 * 2300.0)

    def test_get_total_value(self):
        self.account.deposit(500.0)
        self.account.buy("RELIANCE", 2)
        self.assertEqual(self.account.get_total_value(), (2 * 2300.0) + 500.0)

    def test_get_profit_loss(self):
        self.account.deposit(500.0)
        self.account.buy("RELIANCE", 2)
        self.assertEqual(self.account.get_profit_loss(), (2 * 2300.0 + 500.0) - 10000.0)

    def test_report_holdings(self):
        self.account.buy("RELIANCE", 2)
        self.assertEqual(self.account.report_holdings(), {"RELIANCE": 2})

    def test_list_transactions(self):
        self.account.deposit(500.0)
        transactions = self.account.list_transactions()
        self.assertEqual(len(transactions), 2)  # Initial deposit + one deposit

    def test_to_dict(self):
        self.account.deposit(500.0)
        account_dict = self.account.to_dict()
        self.assertEqual(account_dict["owner"], "Test User")
        self.assertEqual(account_dict["balance"], 10500.0)

    def test_unknown_symbol_error(self):
        with self.assertRaises(UnknownSymbolError):
            get_share_price("UNKNOWN")

if __name__ == "__main__":
    unittest.main()