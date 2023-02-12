// SPDX-License-Identifier: MIT 

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";
import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";

contract Lottery is Ownable, VRFConsumerBaseV2{

    address payable[] public players;
    address payable public winner;
    mapping(address => uint) public playerToAmount;
    uint256 public entryFeeInUsd;

    enum State {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    State public current_state;

    // Price Feed
    AggregatorV3Interface internal priceFeed;

    // Random Number
    VRFCoordinatorV2Interface Coordinator;
    uint64 s_subscriptionId;
    bytes32 keyHash = 0x79d3d8832d904592c0bf9818b621522c988bb8b0c05cdc3b15aea1b6e8db0c15;
    uint32 callbackGasLimit = 100000;
    uint16 requestConfirmations = 3;
    uint32 numWords = 1;

    uint256 public randomWord;

    event RequestedRandomness(uint256 requestId);
     
    constructor(address _priceFeed, uint64 _subscriptionId, bytes32 _keyHash, address _coordinator) VRFConsumerBaseV2(_coordinator) {
        entryFeeInUsd = 50 * (10**18);
        current_state = State.CLOSED;

        priceFeed = AggregatorV3Interface(_priceFeed);

        s_subscriptionId = _subscriptionId;
        keyHash = _keyHash;
        Coordinator = VRFCoordinatorV2Interface(
            _coordinator
        );
    }

    function startLottery() public onlyOwner {
        require(current_state == State.CLOSED , "Cannot start a lottery yet!");
        current_state = State.OPEN;
    }

    function enterToLottery() public payable{
        require(current_state == State.OPEN, "No more entries are allowed!");
        require(getEntryFee() <= msg.value, "You need to spend more ETH!");
        players.push(payable(msg.sender));
        playerToAmount[msg.sender] += msg.value;
    }

    function getEntryFee() public view returns (uint256) {
        uint256 adjustedPrice = getPrice();
        uint256 costToEnter = (entryFeeInUsd * 10**18) / adjustedPrice;
        return costToEnter;
    }

    function getPrice() public view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        return uint256(price) * 10**10;
    }

    function endLottery() public returns(uint256){
        require(current_state == State.OPEN, "The lottery is not open!");
        current_state = State.CALCULATING_WINNER;
        uint256 requestId = calculateWinner();
        emit RequestedRandomness(requestId);
        return requestId;
    }

    function calculateWinner() internal returns(uint256){
        require(current_state == State.CALCULATING_WINNER, "Cannot calculate the winner yet!");
        uint256 requestId = Coordinator.requestRandomWords(
            keyHash,
            s_subscriptionId,
            requestConfirmations,
            callbackGasLimit,
            numWords
        );
        return requestId;
    }

    function fulfillRandomWords(
        uint256 _requestId,
        uint256[] memory _randomWords
    ) internal override {
        randomWord = _randomWords[0];
        uint256 winnerIndex = randomWord % players.length;

        winner = players[winnerIndex];
        winner.transfer(address(this).balance);

        players = new address payable[](0);

        current_state = State.CLOSED;
    }
}