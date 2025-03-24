// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;
import {Utils} from "./Utils.sol";


// MultiStoreProof stores a compact of other Cosmos-SDK modules' storage hash in multistore to
// compute (in combination with oracle store hash) Tendermint's application state hash at a given block.

library MultiStore {

    struct Data {
        bytes32 oracleIAVLStateHash;
        bytes32 mintStoreMerkleHash;
        bytes32 paramsToRestakeStoresMerkleHash;
        bytes32 rollingseedToTransferStoresMerkleHash;
        bytes32 tssToUpgradeStoresMerkleHash;
        bytes32 authToIcahostStoresMerkleHash;
    }

    function getAppHash(Data memory self) internal pure returns (bytes32) {
        return Utils.merkleInnerHash(
            self.authToIcahostStoresMerkleHash,
            Utils.merkleInnerHash(
                Utils.merkleInnerHash(
                    Utils.merkleInnerHash(
                        Utils.merkleInnerHash(
                            self.mintStoreMerkleHash,
                            Utils.merkleLeafHash(
                                abi.encodePacked(
                                    hex"066f7261636c6520", // oracle prefix (uint8(6) + "oracle" + uint8(32))
                                    sha256(abi.encodePacked(self.oracleIAVLStateHash))
                                )
                            )
                        ),
                        self.paramsToRestakeStoresMerkleHash
                    ),
                    self.rollingseedToTransferStoresMerkleHash
                ),
                self.tssToUpgradeStoresMerkleHash
            )
        );
    }
}
