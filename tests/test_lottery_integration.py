from brownie import network
from scripts.deploy_lottery import deploy_lottery
from scripts.helpers import LOCAL_BLOCKCHAIN_NETWORK, get_account, remove_consumer
import pytest 
import time

def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_NETWORK:
        pytest.skip()
    
    lottery = deploy_lottery()
    account = get_account()

    lottery.startLottery({"from": account})
    lottery.enterToLottery({"from": account, "value": lottery.getEntryFee()})
    lottery.enterToLottery({"from": account, "value": lottery.getEntryFee()})
    account_balance = account.balance()
    lottery_balance = lottery.balance()
    lottery.endLottery({"from": account})
    time.sleep(60)
    remove_consumer(lottery.address)
    assert lottery.winner() == account.address
    assert lottery.balance() == 0
    # assert account.balance() == lottery_balance + account_balance

