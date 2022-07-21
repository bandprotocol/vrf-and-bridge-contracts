// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

/// @dev Library for performing concatenation of all common parts together into a single common part.
/// The common part is used for the signature verification process, and it should be the same bytes for all validators.
/// The library also performs a sanity check to ensure the integrity of the data.
///
/// ================================ Original structs on Tendermint ================================
///
/// type SignedMsgType int32
///
/// type CanonicalPartSetHeader struct {
///        Total uint32 `protobuf:"varint,1,opt,name=total`
///        Hash  []byte `protobuf:"bytes,2,opt,name=hash`
/// }
///
/// type CanonicalBlockID struct {
///        Hash          []byte                 `protobuf:"bytes,1,opt,name=hash`
///        PartSetHeader CanonicalPartSetHeader `protobuf:"bytes,2,opt,name=part_set_header`
/// }
///
/// type CanonicalVote struct {
///        Type      SignedMsgType     `protobuf:"varint,1,opt,name=type`
///        Height    int64             `protobuf:"fixed64,2,opt,name=height`
///        Round     int64             `protobuf:"fixed64,3,opt,name=round`
///        BlockID   *CanonicalBlockID `protobuf:"bytes,4,opt,name=block_id`
///        Timestamp time.Time         `protobuf:"bytes,5,opt,name=timestamp`
///        ChainID   string            `protobuf:"bytes,6,opt,name=chain_id`
/// }
///
/// ================================ Original structs on Tendermint ================================
///
library CommonEncodedVotePart {
    struct Data {
        bytes signedDataPrefix;
        bytes signedDataSuffix;
    }

    /// @dev Returns the address that signed on the given block hash.
    /// @param blockHash The block hash that the validator signed data on.
    function checkPartsAndEncodedCommonParts(Data memory self, bytes32 blockHash)
        internal
        pure
        returns (bytes memory)
    {
        // We need to limit the possible size of the prefix and suffix to ensure only one possible block hash.

        // There are only two possible prefix sizes.
        // 1. If Round == 0, the prefix size should be 15 because the encoded Round was cut off.
        // 2. If not then the prefix size should be 24 (15 + 9).
        require(
            self.signedDataPrefix.length == 15 || self.signedDataPrefix.length == 24,
            "CommonEncodedVotePart: Invalid prefix's size"
        );

        // The suffix is encoded of a CanonicalPartSetHeader, which has a fixed size in practical.
        // There are two reasons why.
        // 1. The maximum value of CanonicalPartSetHeader.Total is 48 (3145728 / 65536) because Band's MaxBlockSizeBytes
        // is 3145728 bytes, and the max BlockPartSizeBytes's size is 65536 bytes.
        // 2. The CanonicalPartSetHeader.Hash's size is fixed (32 bytes) because it is a product of SHA256.
        // Therefore, the overall size is fixed.
        require(self.signedDataSuffix.length == 38, "CommonEncodedVotePart: Invalid suffix's size");

        return abi.encodePacked(
            self.signedDataPrefix,
            blockHash,
            self.signedDataSuffix
        );
    }
}
