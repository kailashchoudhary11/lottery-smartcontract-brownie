from brownie import Lottery, web3
from scripts.deploy_lottery import deploy_lottery
from scripts.helpers import get_account

def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    print("Stating Lottery...")
    start_tx = lottery.startLottery({"from": account })
    start_tx.wait(1)
    print("Lottery Started!")

def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    print("Entering to lottery...")
    entry_fee = lottery.getEntryFee()
    enter_tx = lottery.enterToLottery({"from": account, "value": entry_fee})
    enter_tx.wait(1)
    print("Successfully entered!")

def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    print("Ending the lottery...")
    end_tx = lottery.endLottery({"from": account})
    end_tx.wait(1)
    print("Lottery ended successfully!")

def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()