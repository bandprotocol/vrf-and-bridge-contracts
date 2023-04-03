// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {Bridge} from "../bridge/Bridge.sol";
import {IBridge} from "../../interfaces/bridge/IBridge.sol";

/// @dev Mock OracleBridge that allows setting oracle iAVL state at a given height directly.
contract MockBridge is Bridge {
    constructor(
        ValidatorWithPower[] memory _validators,
        bytes memory _encodedChainID
    ) {
        initialize(_validators, _encodedChainID);
    }

    function setOracleState(
        uint256 _blockHeight,
        bytes32 _oracleIAVLStateHash
    ) public {
        blockDetails[_blockHeight].oracleState = _oracleIAVLStateHash;
    }
}

contract MockReceiver {
    Bridge.Result public latestRes;
    Bridge.Result[] public latestResults;
    IBridge immutable bridge;

    constructor(IBridge _bridge) {
        bridge = _bridge;
    }

    function relayAndSafe(bytes calldata _data) external {
        latestRes = bridge.relayAndVerify(_data);
    }

    function relayAndMultiSafe(bytes calldata _data) external {
        Bridge.Result[] memory results = bridge.relayAndMultiVerify(_data);
        delete latestResults;
        for (uint256 i = 0; i < results.length; i++) {
            latestResults.push(results[i]);
        }
    }
}
