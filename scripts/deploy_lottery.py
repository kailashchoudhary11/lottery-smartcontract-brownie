from brownie import Lottery
from scripts.helpers import get_account, get_contract_address, get_sub_id, get_key_hash, ACTIVE_NETWORK, LOCAL_BLOCKCHAIN_NETWORK, fund_subscription, add_consumer

def deploy_lottery():
    account = get_account()
    price_feed = get_contract_address("price_feed")
    key_hash = get_key_hash()
    coordinator = get_contract_address("vrf_coordinator")
    sub_id = get_sub_id()

    print("Deploying Lottery...")
    lottery = Lottery.deploy(price_feed, sub_id, key_hash, coordinator, {"from": account})
    print("Lottery deployed!")

    if ACTIVE_NETWORK in LOCAL_BLOCKCHAIN_NETWORK:
        fund_subscription(sub_id)

    add_consumer(Lottery[-1].address)
    
    return lottery
    

def main():
    deploy_lottery()