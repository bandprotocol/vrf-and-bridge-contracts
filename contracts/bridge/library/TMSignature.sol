// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

/// @dev Library for performing signer recovery for ECDSA secp256k1 signature. Note that the
/// library is written specifically for signature signed on Tendermint's precommit data, which
/// includes the block hash and some additional information prepended and appended to the block
/// hash. The prepended part (prefix) and the appended part (suffix) are different for each signer
/// (including signature size, machine clock, validator index, etc).
///
library TMSignature {
    struct Data {
        bytes32 r;
        bytes32 s;
        uint8 v;
        bytes encodedTimestamp;
    }

    /// @dev Returns the address that signed on the given encoded canonical vote message on Cosmos.
    /// @param commonEncodedPart The first common part of the encoded canonical vote.
    /// @param encodedChainID The last part of the encoded canonical vote.
    function checkTimeAndRecoverSigner(Data memory self, bytes memory commonEncodedPart, bytes memory encodedChainID)
        internal
        pure
        returns (address)
    {
        // We need to limit the possible size of the encodedCanonicalVote to ensure only one possible block hash.
        // The size of the encodedTimestamp will be between 6 and 12 according to the following two constraints.
        // 1. The size of an encoded Unix's second is 6 bytes until over a thousand years in the future.
        // 2. The NanoSecond size can vary from 0 to 6 bytes.
        // Therefore, 6 + 0 <= the size <= 6 + 6.
        require(
            6 <= self.encodedTimestamp.length && self.encodedTimestamp.length <= 12,
            "TMSignature: Invalid timestamp's size"
        );
        bytes memory encodedCanonicalVote = abi.encodePacked(
            commonEncodedPart,
            uint8(42),
            uint8(self.encodedTimestamp.length),
            self.encodedTimestamp,
            encodedChainID
        );
        return
            ecrecover(
                sha256(abi.encodePacked(uint8(encodedCanonicalVote.length), encodedCanonicalVote)),
                self.v,
                self.r,
                self.s
            );
    }
}
