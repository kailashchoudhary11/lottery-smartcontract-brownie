from brownie import Lottery, web3
from scripts.deploy_lottery import deploy_lottery
from scripts.helpers import get_account, fulfill_request, ACTIVE_NETWORK, LOCAL_BLOCKCHAIN_NETWORK, remove_consumer
import time

def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    print("Starting Lottery...")

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
    print("The lottery balance is:", lottery.balance())
    print("The account balance is:", account.balance())

def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    print("Ending the lottery...")
    end_tx = lottery.endLottery({"from": account})
    end_tx.wait(1)
    
    if ACTIVE_NETWORK in LOCAL_BLOCKCHAIN_NETWORK:
        request_id = end_tx.events["RandomWordsRequested"]["requestId"]
        fulfill_request(request_id, lottery.address)
    else:
        time.sleep(80)

    print("The random number is:", lottery.randomWord())
    print("Lottery ended successfully!")
    winner_details()

    remove_consumer(lottery.address)
    

def winner_details():
    lottery = Lottery[-1]
    print("The winner is:", lottery.winner())
    print("The lottery balance is: ", lottery.balance())
    print("The account balance is: ", get_account().balance())

def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
    