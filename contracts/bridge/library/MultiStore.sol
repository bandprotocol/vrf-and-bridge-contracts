// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;
import {Utils} from "./Utils.sol";


// MultiStoreProof stores a compact of other Cosmos-SDK modules' storage hash in multistore to
// compute (in combination with oracle store hash) Tendermint's application state hash at a given block.
//                                              ________________[AppHash]_________________
//                                             /                                          \
//                         _________________[I14]_________________                        [G]
//                        /                                        \
//             _______[I12]______                          _______[I13]________
//            /                  \                        /                    \
//       __[I8]__             __[I9]__                __[I10]__              __[I11]__
//      /         \          /         \            /          \            /         \
//    [I0]       [I1]     [I2]        [I3]        [I4]        [I5]        [I6]       [I7]
//   /   \      /   \    /    \      /    \      /    \      /    \      /    \     /    \
// [0]   [1]  [2]   [3] [4]   [5]  [6]    [7]  [8]    [9]  [A]    [B]  [C]    [D]  [E]   [F]
// [0] - auth     [1] - authz    [2] - bank    [3] - capability [4] - crisis  [5] - dist
// [6] - evidence [7] - feegrant [8] - gov     [9] - ibccore    [A] - mint    [B] - oracle
// [C] - params   [D] - slashing [E] - staking [F] - transfer   [G] - upgrade
// Notice that NOT all leaves of the Merkle tree are needed in order to compute the Merkle
// root hash, since we only want to validate the correctness of [B] In fact, only
// [A], [I4], [I11], [I12], and [G] are needed in order to compute [AppHash].

library MultiStore {
    struct Data {
        bytes32 authToFeeGrantStoresMerkleHash; // [I12]
        bytes32 govToIbcCoreStoresMerkleHash; // [I4]
        bytes32 mintStoreMerkleHash; // [A]
        bytes32 oracleIAVLStateHash; // [B]
        bytes32 paramsToTransferStoresMerkleHash; // [I11]
        bytes32 upgradeStoreMerkleHash; // [G]
    }

    function getAppHash(Data memory self) internal pure returns (bytes32) {
        return
            Utils.merkleInnerHash( // [AppHash]
                Utils.merkleInnerHash( // [I14]
                    self.authToFeeGrantStoresMerkleHash, // [I12]
                    Utils.merkleInnerHash( // [I13]
                        Utils.merkleInnerHash( // [I10]
                            self.govToIbcCoreStoresMerkleHash, // [I4]
                            Utils.merkleInnerHash( // [I5]
                                self.mintStoreMerkleHash, // [A]
                                Utils.merkleLeafHash( // [B]
                                    abi.encodePacked(
                                        hex"066f7261636c6520", // oracle prefix (uint8(6) + "oracle" + uint8(32))
                                        sha256(
                                            abi.encodePacked(
                                                self.oracleIAVLStateHash
                                            )
                                        )
                                    )
                                )
                            )
                        ),
                        self.paramsToTransferStoresMerkleHash // [I11]
                    )
                ),
                self.upgradeStoreMerkleHash // [G]
            );
    }
}
