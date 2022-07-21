// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;
import {CommonEncodedVotePart} from "../bridge/library/CommonEncodedVotePart.sol";

contract MockCommonEncodedVotePart {
    function checkPartsAndEncodedCommonParts(
        CommonEncodedVotePart.Data memory _data,
        bytes32 _blockHash
    ) public pure returns (bytes memory) {
        return CommonEncodedVotePart.checkPartsAndEncodedCommonParts(_data, _blockHash);
    }
}
