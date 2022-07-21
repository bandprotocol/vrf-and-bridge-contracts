// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {MultiStore} from "../bridge/library/MultiStore.sol";

contract MockMultiStore {
    function getAppHash(MultiStore.Data memory _self)
        public
        pure
        returns (bytes32)
    {
        return MultiStore.getAppHash(_self);
    }
}
