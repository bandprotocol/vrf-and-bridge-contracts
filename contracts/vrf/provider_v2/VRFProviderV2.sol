// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {IBridge} from "../../../interfaces/bridge/IBridge.sol";
import {VRFProviderBaseV2} from "./VRFProviderBaseV2.sol";

contract VRFProviderV2 is VRFProviderBaseV2 {
    constructor(
        uint64 _oracleScriptID,
        IBridge _bridge,
        uint256 _minimumFee
    ) VRFProviderBaseV2(_oracleScriptID, _bridge, _minimumFee) {}
}
