// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

/// @dev Helper utility library for calculating Merkle proof and managing bytes.
library Utils {
    /// @dev Returns the hash of a Merkle leaf node.
    function merkleLeafHash(bytes memory value)
        internal
        pure
        returns (bytes32)
    {
        return sha256(abi.encodePacked(uint8(0), value));
    }

    /// @dev Returns the hash of internal node, calculated from child nodes.
    function merkleInnerHash(bytes32 left, bytes32 right)
        internal
        pure
        returns (bytes32)
    {
        return sha256(abi.encodePacked(uint8(1), left, right));
    }

    /// @dev Returns the encoded bytes using signed varint encoding of the given input.
    function encodeVarintSigned(uint256 value)
        internal
        pure
        returns (bytes memory)
    {
        return encodeVarintUnsigned(value * 2);
    }

    /// @dev Returns the encoded bytes using unsigned varint encoding of the given input.
    function encodeVarintUnsigned(uint256 value)
        internal
        pure
        returns (bytes memory)
    {
        // Computes the size of the encoded value.
        uint256 tempValue = value;
        uint256 size = 0;
        while (tempValue > 0) {
            ++size;
            tempValue >>= 7;
        }
        // Allocates the memory buffer and fills in the encoded value.
        bytes memory result = new bytes(size);
        tempValue = value;
        for (uint256 idx = 0; idx < size; ++idx) {
            result[idx] = bytes1(uint8(128) | uint8(tempValue & 127));
            tempValue >>= 7;
        }
        result[size - 1] &= bytes1(uint8(127)); // Drop the first bit of the last byte.
        return result;
    }

    /// @dev Returns the encoded bytes follow how tendermint encode time.
    function encodeTime(uint64 second, uint32 nanoSecond)
        internal
        pure
        returns (bytes memory)
    {
        bytes memory result =
            abi.encodePacked(hex"08", encodeVarintUnsigned(uint256(second)));
        if (nanoSecond > 0) {
            result = abi.encodePacked(
                result,
                hex"10",
                encodeVarintUnsigned(uint256(nanoSecond))
            );
        }
        return result;
    }
}
