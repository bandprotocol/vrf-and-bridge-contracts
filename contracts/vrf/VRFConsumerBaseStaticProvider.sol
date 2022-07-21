// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {IVRFProvider} from "../../interfaces/vrf/IVRFProvider.sol";
import {IVRFConsumer} from "../../interfaces/vrf/IVRFConsumer.sol";

abstract contract VRFConsumerBaseStaticProvider is IVRFConsumer {
    IVRFProvider public immutable provider;

    constructor(IVRFProvider _provider) {
        provider = _provider;
    }

    function consume(
        string calldata _seed,
        uint64 _time,
        bytes32 _result
    ) external override {
        require(msg.sender == address(provider), "VRFConsumerBaseStaticProvider: The sender is not the provider");
        _consume(_seed, _time, _result);
    }

    function _consume(
        string calldata _seed,
        uint64 _time,
        bytes32 _result
    ) internal virtual {
        revert("VRFConsumerBaseStaticProvider: Unimplemented");
    }
}
