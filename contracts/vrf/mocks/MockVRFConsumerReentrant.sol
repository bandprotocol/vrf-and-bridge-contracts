// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {IVRFProvider} from "../../../interfaces/vrf/IVRFProvider.sol";
import {VRFConsumerBaseStaticProvider} from "../VRFConsumerBaseStaticProvider.sol";

interface IVRFProviderExtended {
    function requestRandomData(string calldata seed) external payable;
    function relayProof(bytes calldata proof, uint64 nonce) external;
}

contract MockVRFConsumerReentrant is VRFConsumerBaseStaticProvider {
    event RandomDataRequested(address provider, string seed, uint256 bounty);
    event Consume(string seed, uint64 time, bytes32 result);
    event SaveProof(uint256 proofSize);
    event FlipReentrantFlag(bool currentReentrantFlag);

    bytes public proofStorage;
    uint64 nonceStorage;
    uint256 public entranceCount = 0;
    bool public reentrantFlag = false;

    constructor(IVRFProvider _provider) VRFConsumerBaseStaticProvider(_provider) {}

    function requestRandomDataFromProvider(string calldata _seed) external payable {
        provider.requestRandomData{value: msg.value}(_seed);
        emit RandomDataRequested(address(provider), _seed, msg.value);
    }

    function saveProofAndNonce(bytes memory proof, uint64 nonce) external {
        proofStorage = proof;
        nonceStorage = nonce;
        emit SaveProof(proof.length);
    }

    function flipReentrantFlag() external {
        reentrantFlag = !reentrantFlag;
        emit FlipReentrantFlag(reentrantFlag);
    }

    function relayProofReentrant() external {
        IVRFProviderExtended(address(provider)).relayProof(proofStorage, nonceStorage);
    }

    function _consume(string calldata seed, uint64 time, bytes32 result) internal override {
        entranceCount = entranceCount + 1;

        if (entranceCount < 2) {
            if (reentrantFlag) {
                IVRFProviderExtended(address(provider)).requestRandomData("random_string_seed");
            } else {
                IVRFProviderExtended(address(provider)).relayProof(proofStorage, nonceStorage);
            }
        }

        entranceCount = 0;

        emit Consume(seed, time, result);
    }

    fallback() external payable {}
}
