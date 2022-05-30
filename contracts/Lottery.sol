// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/mocks/OwnableMock.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase, Ownable{

    address payable[] public players;
    address payable public recentWinner;
    uint256 public entryFee;
    AggregatorV3Interface internal ethusd;
    enum LOTTERY_STATE {
        OPEN, CLOSED, CALC_WINNER
    }
    LOTTERY_STATE public lotr_state;
    uint256 public fee;
    bytes32 public keyHash;
    event RequestRandomness(bytes32 requestId);

    constructor(
        address _pf_addr, address _vrf_addr, address _link_tkn, uint256 _fee, bytes32 _keyHash
     )  public VRFConsumerBase(_vrf_addr, _link_tkn) {        
        entryFee = 50*(10**18);
        ethusd = AggregatorV3Interface(_pf_addr);
        lotr_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyHash = _keyHash;

    }

    function enter() public payable{
        require(lotr_state == LOTTERY_STATE.OPEN);
        require(msg.value >= getEntranceFee(), "Not enuf ETH!");
        players.push(msg.sender);
    }

    function getEntranceFee()  public view returns (uint256) {
        (,int price,,,) = ethusd.latestRoundData();
        uint256 aprice = uint256(price); // 10**10;
        uint256 costtoEnter = (entryFee * 10**18) / aprice;
        return costtoEnter;
    }

    function startLotr() public onlyOwner{
        require(lotr_state == LOTTERY_STATE.CLOSED);
        lotr_state = LOTTERY_STATE.OPEN;
    }

    function endLotr() public onlyOwner{
        // below code noob as it's deterministic
        // uint256(
        //     keccack256(
        //         abi.encodePacked(nonce, msg.sender, block.difficulty, block.timestamp)
        //     ) % players.length;
        // )
        lotr_state = LOTTERY_STATE.CALC_WINNER;
        bytes32 requestId = requestRandomness(keyHash, fee);        

        emit RequestRandomness(requestId);

    }

    function fulfillRandomness(bytes32 _reqid, uint256 _randomness) internal override{
        require(lotr_state == LOTTERY_STATE.CALC_WINNER, "You aren't there yet");
        require(_randomness > 0, "random not found");
        uint256 winner = _randomness % players.length;
        recentWinner = players[winner];
        recentWinner.transfer(address(this).balance);

        //reset
        players = new address payable[](0);
    }
}