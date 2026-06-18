from datetime import datetime
import gradio as gr
from accounts import Account, get_share_price

def create_account(owner, initial_deposit):
    return Account(owner, initial_deposit)

def deposit_funds(account, amount):
    account.deposit(amount)
    return account.balance

def withdraw_funds(account, amount):
    account.withdraw(amount)
    return account.balance

def buy_shares(account, symbol, quantity):
    account.buy(symbol, quantity)
    return account.report_holdings()

def sell_shares(account, symbol, quantity):
    account.sell(symbol, quantity)
    return account.report_holdings()

def report_holdings(account):
    return account.report_holdings()

def report_profit_loss(account):
    return account.get_profit_loss()

def list_transactions(account):
    transactions = account.list_transactions()
    return [str(transaction) for transaction in transactions]

def main():
    with gr.Blocks() as demo:
        gr.Markdown("## Trading Simulation Platform Account Management")
        owner = gr.Textbox(label="Owner Name")
        initial_deposit = gr.Number(label="Initial Deposit", value=10000)
        
        create_btn = gr.Button("Create Account")
        account = gr.State(value=None)

        def on_create_account(owner, initial_deposit):
            new_account = create_account(owner, initial_deposit)
            return new_account

        create_btn.click(on_create_account, inputs=[owner, initial_deposit], outputs=account)

        amount = gr.Number(label="Amount")
        deposit_btn = gr.Button("Deposit")
        withdraw_btn = gr.Button("Withdraw")

        deposit_btn.click(deposit_funds, inputs=[account, amount], outputs=account)
        withdraw_btn.click(withdraw_funds, inputs=[account, amount], outputs=account)

        symbol = gr.Textbox(label="Share Symbol (RELIANCE, TCS, INFY, HDFCBANK)")
        quantity = gr.Number(label="Quantity")
        buy_btn = gr.Button("Buy Shares")
        sell_btn = gr.Button("Sell Shares")

        buy_btn.click(buy_shares, inputs=[account, symbol, quantity], outputs=account)
        sell_btn.click(sell_shares, inputs=[account, symbol, quantity], outputs=account)

        holdings_btn = gr.Button("Report Holdings")
        profit_loss_btn = gr.Button("Report Profit/Loss")
        transactions_btn = gr.Button("List Transactions")

        holdings_btn.click(report_holdings, inputs=account, outputs=account)
        profit_loss_btn.click(report_profit_loss, inputs=account, outputs=account)
        transactions_btn.click(list_transactions, inputs=account, outputs=account)

    demo.launch()

if __name__ == "__main__":
    main()