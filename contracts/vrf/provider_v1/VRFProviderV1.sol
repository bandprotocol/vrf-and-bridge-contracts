// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {IBridge} from "../../../interfaces/bridge/IBridge.sol";
import {VRFProviderBaseV1} from "./VRFProviderBaseV1.sol";

contract VRFProviderV1 is VRFProviderBaseV1 {
    constructor(
        uint8 _minCount,
        uint8 _askCount,
        uint64 _oracleScriptID,
        IBridge _bridge,
        uint256 _minimumFee
    ) VRFProviderBaseV1(_minCount, _askCount, _oracleScriptID, _bridge, _minimumFee) {}
}
