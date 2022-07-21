// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {Bridge} from "../bridge/Bridge.sol";
import {IBridge} from "../../interfaces/bridge/IBridge.sol";

contract BridgeData {
    Bridge immutable bridge;
    IBridge.Result public res;

    constructor(Bridge _bridge) {
        bridge = _bridge;
    }

    function relayAndSave(bytes calldata data) external {
        res = bridge.relayAndVerify(data);
    }

    function ClientID() external view returns (string memory) {
        return res.clientID;
    }

    function oracleScriptID() external view returns (uint64) {
        return res.oracleScriptID;
    }

    function params() external view returns (bytes memory) {
        return res.params;
    }

    function askCount() external view returns (uint64) {
        return res.askCount;
    }

    function minCount() external view returns (uint64) {
        return res.minCount;
    }

    function requestID() external view returns (uint64) {
        return res.requestID;
    }

    function ansCount() external view returns (uint64) {
        return res.ansCount;
    }

    function requestTime() external view returns (uint64) {
        return res.requestTime;
    }

    function resolveTime() external view returns (uint64) {
        return res.resolveTime;
    }

    function resolveStatus() external view returns (IBridge.ResolveStatus) {
        return res.resolveStatus;
    }

    function result() external view returns (bytes memory) {
        return res.result;
    }
}
