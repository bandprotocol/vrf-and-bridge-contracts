// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {IVRFProvider} from "../../../interfaces/vrf/IVRFProvider.sol";
import {VRFConsumerBaseStaticProvider} from "../VRFConsumerBaseStaticProvider.sol";

contract MockVRFConsumer is VRFConsumerBaseStaticProvider {
    string public latestSeed;
    uint64 public latestTime;
    bytes32 public latestResult;

    event RandomDataRequested(address provider, string seed, uint256 bounty);
    event Consume(string seed, uint64 time, bytes32 result);

    constructor(IVRFProvider _provider) VRFConsumerBaseStaticProvider(_provider) {}

    function requestRandomDataFromProvider(string calldata _seed)
        external
        payable
    {
        provider.requestRandomData{value: msg.value}(_seed);

        emit RandomDataRequested(address(provider), _seed, msg.value);
    }

    function _consume(
        string calldata _seed,
        uint64 _time,
        bytes32 _result
    ) internal override {
        latestSeed = _seed;
        latestTime = _time;
        latestResult = _result;

        emit Consume(_seed, _time, _result);
    }
}
