from brownie import web3, network, exceptions
from scripts.deploy_lottery import deploy_lottery
from scripts.helpers import get_account, LOCAL_BLOCKCHAIN_NETWORK, get_coordinator, fund_subscription, get_sub_id
import pytest 

def test_get_entry_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORK:
        pytest.skip()
    # Arrange 
    lottery = deploy_lottery()
    # Act
    observed_value = lottery.getEntryFee()
    expected_value = web3.toWei(0.025, "ether")
    # Assert 
    assert observed_value == expected_value

def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORK:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enterToLottery({"from": get_account(), "value": lottery.getEntryFee()})

def test_can_start_and_enter():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORK:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()

    # Act
    lottery.startLottery({"from": account})
    lottery.enterToLottery({"from": account, "value": lottery.getEntryFee()})

    # Assert 
    assert lottery.players(0) == account.address
    assert lottery.balance() == lottery.getEntryFee()

def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORK:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()

    # Act
    lottery.startLottery({"from": account})
    lottery.enterToLottery({"from": account, "value": lottery.getEntryFee()})
    lottery.endLottery({"from": account})

    # Assert 
    assert lottery.current_state() == 2

def test_can_pick_winner_correctly():
    # Arrange 
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORK:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()

    # Act
    lottery.startLottery({"from": account})
    lottery.enterToLottery({"from": account, "value": lottery.getEntryFee()})
    lottery.enterToLottery({"from": get_account(1), "value": lottery.getEntryFee()})
    lottery.enterToLottery({"from": get_account(2), "value": lottery.getEntryFee()})
    fund_subscription(get_sub_id(), 1e18)
    end_tx = lottery.endLottery({"from": account})
    request_id = end_tx.events["RequestedRandomness"]["requestId"]
    STATIC_RANDOM_WORD = 777
    account_balance = account.balance()
    lottery_balance = lottery.balance()
    get_coordinator().fulfillRandomWordsWithOverride(request_id, lottery.address, [STATIC_RANDOM_WORD], {"from": account})

    # Assert 
    assert lottery.winner() == get_account(0)
    assert account.balance() == (account_balance + lottery_balance)
    

    