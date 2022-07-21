// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {
    BlockHeaderMerkleParts
} from "../bridge/library/BlockHeaderMerkleParts.sol";

contract MockBlockHeaderMerkleParts {
    function getBlockHeader(
        BlockHeaderMerkleParts.Data memory _self,
        bytes32 _appHash
    ) public pure returns (bytes32) {
        return BlockHeaderMerkleParts.getBlockHeader(_self, _appHash);
    }
}
