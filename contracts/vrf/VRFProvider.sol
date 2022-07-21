// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {IBridge} from "../../interfaces/bridge/IBridge.sol";
import {VRFProviderBase} from "./VRFProviderBase.sol";

contract VRFProvider is VRFProviderBase {
    constructor(
        uint8 _minCount,
        uint8 _askCount,
        uint64 _oracleScriptID,
        IBridge _bridge,
        uint256 _minimumFee
    ) VRFProviderBase(_minCount, _askCount, _oracleScriptID, _bridge, _minimumFee) {}
}
