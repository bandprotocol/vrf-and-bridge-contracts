// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {IBridge} from "../../../interfaces/bridge/IBridge.sol";
import {VRFProviderBaseV1} from "../provider_v1/VRFProviderBaseV1.sol";

contract MockVRFProviderV1 is VRFProviderBaseV1 {
    constructor(
        uint8 _minCount,
        uint8 _askCount,
        uint64 _oracleScriptID,
        IBridge _bridge,
        uint256 _minimumFee
    ) VRFProviderBaseV1(_minCount, _askCount, _oracleScriptID, _bridge, _minimumFee) {}

    function getBlockTime() public view override returns (uint64) {
        // Only return a constant timestamp for the testing purpose
        return uint64(1655972425);
    }

    function getBlockLatestHash() public view override returns (bytes32) {
        // Only return a constant random hash for the testing purpose
        return hex"defbfd2812ce28404dc436710582118cfa12cd4c0fa3694323209f012ca36243";
    }

    function getChainID() public view override returns(uint256) {
        // Only return a constant chain id for the testing purpose
        return 112;
    }
}
