// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;
import {Utils} from "../bridge/library/Utils.sol";

contract MockUtils {
    function merkleLeafHash(bytes memory value) public pure returns (bytes32) {
        return Utils.merkleLeafHash(value);
    }

    function merkleInnerHash(bytes32 left, bytes32 right)
        public
        pure
        returns (bytes32)
    {
        return Utils.merkleInnerHash(left, right);
    }

    function encodeVarintSigned(uint256 _value)
        public
        pure
        returns (bytes memory)
    {
        return Utils.encodeVarintSigned(_value);
    }

    function encodeVarintUnsigned(uint256 _value)
        public
        pure
        returns (bytes memory)
    {
        return Utils.encodeVarintUnsigned(_value);
    }

    function encodeTime(uint64 second, uint32 nanoSecond)
        public
        pure
        returns (bytes memory)
    {
        return Utils.encodeTime(second, nanoSecond);
    }
}
