from brownie import network, VRFCoordinatorV2Mock, accounts, MockV3Aggregator, config, web3

# Aggregator 
DECIMALS = 8
INITIAL_VALUE = 200000000000

# Coordinator
BASE_FEE = 100000000000000000
GAS_PRICE_LINK = 1e9
FUND_AMOUNT = 1e18

LOCAL_BLOCKCHAIN_NETWORK = ["development"]
ACTIVE_NETWORK = network.show_active()

contract_to_mock = {
    "price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorV2Mock,
}

def get_account():
    if ACTIVE_NETWORK in LOCAL_BLOCKCHAIN_NETWORK:
        return accounts[0]
    return accounts.add(config["wallet"]["from_key"])

def get_contract_address(contract_name):
    contract = contract_to_mock.get(contract_name)
    if contract is not None:
        if ACTIVE_NETWORK not in LOCAL_BLOCKCHAIN_NETWORK:
            return config["networks"][ACTIVE_NETWORK][contract_name]
        if len(contract) <= 0:
            deploy_mocks()
        return contract[-1].address

def deploy_mocks():
    print("Current Active newtork is", ACTIVE_NETWORK)
    account = get_account()

    print("Deploying Aggregator Mock...")
    MockV3Aggregator.deploy(DECIMALS, INITIAL_VALUE, {"from": account})
    print("Aggregator Mock Deployed!")

    print("Deploying Coordinator Mock...")
    VRFCoordinatorV2Mock.deploy(BASE_FEE, GAS_PRICE_LINK, {"from": account})
    print("Coordinator Mock Deployed!")

def get_key_hash():
    return config["networks"][ACTIVE_NETWORK]["keyhash"]

def get_sub_id():
    if ACTIVE_NETWORK not in LOCAL_BLOCKCHAIN_NETWORK:
        return config["networks"][ACTIVE_NETWORK]["sub_id"]

    if len(VRFCoordinatorV2Mock) <= 0:
        deploy_mocks()

    coordinator = VRFCoordinatorV2Mock[-1]

    print("Creating Subscription...")
    sub_tx = coordinator.createSubscription()
    sub_tx.wait(1)
    print("Subscription Created!")
    sub_id = sub_tx.events["SubscriptionCreated"]["subId"]
    # sub_id = sub_tx.return_value
    return sub_id

def add_consumer(sub_id, consumer):
    if len(VRFCoordinatorV2Mock) <= 0:
        deploy_mocks()

    coordinator = VRFCoordinatorV2Mock[-1]

    print("Adding consumer...")
    add_tx = coordinator.addConsumer(sub_id, consumer, {"from": get_account()})
    add_tx.wait(1)
    print("Consumer Added!")

def fund_subscription(sub_id):
    if len(VRFCoordinatorV2Mock) <= 0:
        deploy_mocks()
    coordinator = VRFCoordinatorV2Mock[-1]
    coordinator.fundSubscription(sub_id, FUND_AMOUNT, {"from": get_account()})
