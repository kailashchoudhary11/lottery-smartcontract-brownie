from brownie import network, VRFCoordinatorV2Mock, accounts, MockV3Aggregator, config, Contract

# Aggregator 
DECIMALS = 8
INITIAL_VALUE = 200000000000

# Coordinator
BASE_FEE = 100000000000000000
GAS_PRICE_LINK = 1e9
FUND_AMOUNT = 1e18
SUB_ID = None

LOCAL_BLOCKCHAIN_NETWORK = ["development", "ganache-local"]
ACTIVE_NETWORK = network.show_active()

contract_to_mock = {
    "price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorV2Mock,
}

def get_account(index=None, id=None):
    if index is not None:
        return accounts[index]

    if id is not None:
        return accounts.get(id)
    
    if network.show_active() in LOCAL_BLOCKCHAIN_NETWORK:
        return accounts[0]

    return accounts.add(config["wallet"]["from_key"])

def get_contract_address(contract_name):
    contract = contract_to_mock.get(contract_name)
    if contract is not None:
        if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORK:
            return config["networks"][network.show_active()][contract_name]
        if len(contract) <= 0:
            deploy_mocks()
        return contract[-1].address

def deploy_mocks():
    print("Current Active newtork is", network.show_active())
    account = get_account()

    print("Deploying Aggregator Mock...")
    MockV3Aggregator.deploy(DECIMALS, INITIAL_VALUE, {"from": account})
    print("Aggregator Mock Deployed!")

    print("Deploying Coordinator Mock...")
    VRFCoordinatorV2Mock.deploy(BASE_FEE, GAS_PRICE_LINK, {"from": account})
    print("Coordinator Mock Deployed!")

def get_key_hash():
    return config["networks"][network.show_active()]["keyhash"]

def get_sub_id():
    global SUB_ID

    if SUB_ID is not None:
        return SUB_ID
    
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORK:
        return config["networks"][network.show_active()]["sub_id"]

    if len(VRFCoordinatorV2Mock) <= 0:
        deploy_mocks()

    coordinator = VRFCoordinatorV2Mock[-1]

    print("Creating Subscription...")
    sub_tx = coordinator.createSubscription({'from': get_account()})
    sub_tx.wait(1)
    print("Subscription Created!")
    sub_id = sub_tx.events["SubscriptionCreated"]["subId"]
    SUB_ID = sub_id
    return sub_id

def add_consumer(consumer):
    coordinator = get_coordinator()

    print("Adding consumer...")
    print("Subscription id is:", get_sub_id())
    add_tx = coordinator.addConsumer(get_sub_id(), consumer, {"from": get_account()})
    add_tx.wait(1)
    print("Consumer Added!")

def fund_subscription(sub_id, fund_amount=FUND_AMOUNT):
    coordinator = get_coordinator()
    coordinator.fundSubscription(sub_id, fund_amount, {"from": get_account()})

def fulfill_request(request_id, consumer):
    coordinator = get_coordinator()
    coordinator.fulfillRandomWords(request_id, consumer, {"from": get_account()})

def remove_consumer(consumer):
    print("Removing consumer...")
    coordinator = get_coordinator()
    add_tx = coordinator.removeConsumer(get_sub_id(), consumer, {"from": get_account()})
    add_tx.wait(1)
    print("Consumer removed!")

def get_sub_ids(address):
    coordinator = get_coordinator()
    return coordinator.getSubscriptionIds(address)
    
def get_coordinator():
    if network.show_active() in LOCAL_BLOCKCHAIN_NETWORK:
        if len(VRFCoordinatorV2Mock) <= 0:
            deploy_mocks()

        return VRFCoordinatorV2Mock[-1]
    return Contract.from_abi("VRFCoordinatorV2", get_contract_address("vrf_coordinator"), VRFCoordinatorV2Mock.abi)
