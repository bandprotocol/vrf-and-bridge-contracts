// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {ProtobufLib} from "./library/ProtobufLib.sol";
import {BlockHeaderMerkleParts} from "./library/BlockHeaderMerkleParts.sol";
import {MultiStore} from "./library/MultiStore.sol";
import {CommonEncodedVotePart} from "./library/CommonEncodedVotePart.sol";
import {EnumerableMap} from "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
import {Initializable} from "@openzeppelin/contracts/proxy/utils/Initializable.sol";
import {IAVLMerklePath} from "./library/IAVLMerklePath.sol";
import {TMSignature} from "./library/TMSignature.sol";
import {Utils} from "./library/Utils.sol";
import {ResultCodec} from "./library/ResultCodec.sol";
import {IBridge} from "../../interfaces/bridge/IBridge.sol";
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";

/// @title BandChain Bridge
/// @author Band Protocol Team
contract Bridge is Initializable, IBridge, AccessControl {
    using BlockHeaderMerkleParts for BlockHeaderMerkleParts.Data;
    using MultiStore for MultiStore.Data;
    using IAVLMerklePath for IAVLMerklePath.Data;
    using CommonEncodedVotePart for CommonEncodedVotePart.Data;
    using TMSignature for TMSignature.Data;
    using EnumerableMap for EnumerableMap.AddressToUintMap;

    struct ValidatorWithPower {
        address addr;
        uint256 power;
    }

    struct BlockDetail {
        bytes32 oracleState;
        uint64 timeSecond;
        uint32 timeNanoSecondFraction; // between 0 to 10^9
    }

    /// The 'VALIDATORS UPDATER ROLE' has the authority to modify the validator set.
    bytes32 public constant VALIDATORS_UPDATER_ROLE =
        keccak256("VALIDATORS_UPDATER_ROLE");

    /// Mapping from block height to the struct that contains block time and hash of "oracle" iAVL Merkle tree.
    mapping(uint256 => BlockDetail) public blockDetails;
    /// Mapping from an address to its voting power.
    EnumerableMap.AddressToUintMap internal validatorPowers;
    /// The total voting power of active validators currently on duty.
    uint256 public totalValidatorPower;
    /// The encoded chain's ID of Band.
    bytes public encodedChainID;

    /// Initializes an oracle bridge to BandChain.
    /// @param validators The initial set of BandChain active validators.
    function initialize(
        ValidatorWithPower[] memory validators,
        bytes memory _encodedChainID
    ) public initializer {
        for (uint256 idx = 0; idx < validators.length; ++idx) {
            ValidatorWithPower memory validator = validators[idx];
            require(
                validatorPowers.set(validator.addr, validator.power),
                "DUPLICATION_IN_INITIAL_VALIDATOR_SET"
            );
            totalValidatorPower += validator.power;
        }
        encodedChainID = _encodedChainID;

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    /// Get number of validators.
    function getNumberOfValidators() public view returns (uint256) {
        return validatorPowers.length();
    }

    /// Get validators by specifying an offset index and a chunk's size.
    /// @param offset An offset index of validators mapping.
    /// @param size The size of the validators chunk.
    function getValidators(
        uint256 offset,
        uint256 size
    ) public view returns (ValidatorWithPower[] memory) {
        ValidatorWithPower[] memory validatorWithPowerList;
        uint256 numberOfValidators = getNumberOfValidators();

        if (offset >= numberOfValidators) {
            // return an empty list
            return validatorWithPowerList;
        } else if (offset + size > numberOfValidators) {
            // reduce size of the entire list
            size = numberOfValidators - offset;
        }

        validatorWithPowerList = new ValidatorWithPower[](size);
        for (uint256 idx = 0; idx < size; ++idx) {
            (address addr, uint256 power) = validatorPowers.at(idx + offset);
            validatorWithPowerList[idx] = ValidatorWithPower({
                addr: addr,
                power: power
            });
        }
        return validatorWithPowerList;
    }

    /// Get all validators with power.
    function getAllValidatorPowers()
        external
        view
        returns (ValidatorWithPower[] memory)
    {
        return getValidators(0, getNumberOfValidators());
    }

    /// Get validator by address
    /// @param addr is an address of the specific validator.
    function getValidatorPower(
        address addr
    ) public view returns (uint256 power) {
        (, power) = validatorPowers.tryGet(addr);
    }

    /// Set the encodedChainID
    /// @param _encodedChainID is a new encodedChainID.
    function updateEncodedChainID(
        bytes memory _encodedChainID
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        encodedChainID = _encodedChainID;
    }

    /// Update validator powers by owner.
    /// @param validators The changed set of BandChain validators.
    /// @param expectedTotalPower The value that the totalValidatorPower should be after updating.
    function updateValidatorPowers(
        ValidatorWithPower[] calldata validators,
        uint256 expectedTotalPower
    ) external onlyRole(VALIDATORS_UPDATER_ROLE) {
        uint256 _totalValidatorPower = totalValidatorPower;
        for (uint256 idx = 0; idx < validators.length; ++idx) {
            ValidatorWithPower memory validator = validators[idx];
            (bool found, uint256 oldPower) = validatorPowers.tryGet(
                validator.addr
            );
            if (found) {
                _totalValidatorPower -= oldPower;
            }

            if (validator.power > 0) {
                validatorPowers.set(validator.addr, validator.power);
                _totalValidatorPower += validator.power;
            } else {
                validatorPowers.remove(validator.addr);
            }
        }

        require(
            _totalValidatorPower == expectedTotalPower,
            "TOTAL_POWER_CHECKING_FAIL"
        );
        totalValidatorPower = _totalValidatorPower;
    }

    /// Perform checking of the block's validity by verify signatures and accumulate the voting power on Band.
    /// @param multiStore Extra multi store to compute app hash. See MultiStore lib.
    /// @param merkleParts Extra merkle parts to compute block hash. See BlockHeaderMerkleParts lib.
    /// @param commonEncodedVotePart The common part of a block that all validators agree upon.
    /// @param signatures The signatures signed on this block, sorted alphabetically by address.
    function verifyBlockHeader(
        MultiStore.Data memory multiStore,
        BlockHeaderMerkleParts.Data memory merkleParts,
        CommonEncodedVotePart.Data memory commonEncodedVotePart,
        TMSignature.Data[] memory signatures
    ) internal view returns (bytes32) {
        // Computes Tendermint's block header hash at this given block.
        bytes32 blockHeader = merkleParts.getBlockHeader(
            multiStore.getAppHash()
        );
        // Verify the prefix, suffix and then compute the common encoded part.
        bytes memory commonEncodedPart = commonEncodedVotePart
            .checkPartsAndEncodedCommonParts(blockHeader);
        // Create a local variable to prevent reading that state repeatedly.
        bytes memory _encodedChainID = encodedChainID;

        // Counts the total number of valid signatures signed by active validators.
        address lastSigner = address(0);
        uint256 sumVotingPower = 0;
        for (uint256 idx = 0; idx < signatures.length; ++idx) {
            address signer = signatures[idx].checkTimeAndRecoverSigner(
                commonEncodedPart,
                _encodedChainID
            );
            require(signer > lastSigner, "INVALID_SIGNATURE_SIGNER_ORDER");
            (bool success, uint256 power) = validatorPowers.tryGet(signer);
            if (success) {
                sumVotingPower += power;
            }
            lastSigner = signer;
        }
        // Verifies that sufficient validators signed the block and saves the oracle state.
        require(
            sumVotingPower * 3 > totalValidatorPower * 2,
            "INSUFFICIENT_VALIDATOR_SIGNATURES"
        );

        return multiStore.oracleIAVLStateHash;
    }

    /// Relays a detail of Bandchain block to the bridge contract.
    /// @param multiStore Extra multi store to compute app hash. See MultiStore lib.
    /// @param merkleParts Extra merkle parts to compute block hash. See BlockHeaderMerkleParts lib.
    /// @param commonEncodedVotePart The common part of a block that all validators agree upon.
    /// @param signatures The signatures signed on this block, sorted alphabetically by address.
    function relayBlock(
        MultiStore.Data calldata multiStore,
        BlockHeaderMerkleParts.Data calldata merkleParts,
        CommonEncodedVotePart.Data calldata commonEncodedVotePart,
        TMSignature.Data[] calldata signatures
    ) public {
        if (
            blockDetails[merkleParts.height].oracleState ==
            multiStore.oracleIAVLStateHash &&
            blockDetails[merkleParts.height].timeSecond ==
            merkleParts.timeSecond &&
            blockDetails[merkleParts.height].timeNanoSecondFraction ==
            merkleParts.timeNanoSecondFraction
        ) return;

        blockDetails[merkleParts.height] = BlockDetail({
            oracleState: verifyBlockHeader(
                multiStore,
                merkleParts,
                commonEncodedVotePart,
                signatures
            ),
            timeSecond: merkleParts.timeSecond,
            timeNanoSecondFraction: merkleParts.timeNanoSecondFraction
        });
    }

    /// Verifies that the given data is a valid data for the given oracleStateRoot.
    /// @param oracleStateRoot The root hash of the oracle store.
    /// @param version Lastest block height that the data node was updated.
    /// @param result The result of this request.
    /// @param merklePaths Merkle proof that shows how the data leave is part of the oracle iAVL.
    function verifyResultWithRoot(
        bytes32 oracleStateRoot,
        uint256 version,
        Result memory result,
        IAVLMerklePath.Data[] memory merklePaths
    ) internal pure returns (Result memory) {
        // Computes the hash of leaf node for iAVL oracle tree.
        bytes32 dataHash = sha256(ResultCodec.encode(result));

        // Verify proof
        require(
            verifyProof(
                oracleStateRoot,
                version,
                abi.encodePacked(uint8(255), result.requestID),
                dataHash,
                merklePaths
            ),
            "INVALID_ORACLE_DATA_PROOF"
        );

        return result;
    }

    /// Verifies that the given data is a valid data on BandChain as of the relayed block height.
    /// @param blockHeight The block height. Someone must already relay this block.
    /// @param result The result of this request.
    /// @param version Lastest block height that the data node was updated.
    /// @param merklePaths Merkle proof that shows how the data leave is part of the oracle iAVL.
    function verifyOracleData(
        uint256 blockHeight,
        Result calldata result,
        uint256 version,
        IAVLMerklePath.Data[] calldata merklePaths
    ) public view returns (Result memory) {
        bytes32 oracleStateRoot = blockDetails[blockHeight].oracleState;
        require(
            oracleStateRoot != bytes32(uint256(0)),
            "NO_ORACLE_ROOT_STATE_DATA"
        );

        return
            verifyResultWithRoot(oracleStateRoot, version, result, merklePaths);
    }

    /// Verifies that the given data is a valid data on BandChain as of the relayed block height.
    /// @param blockHeight The block height. Someone must already relay this block.
    /// @param count The requests count on the block.
    /// @param version Lastest block height that the data node was updated.
    /// @param merklePaths Merkle proof that shows how the data leave is part of the oracle iAVL.
    function verifyRequestsCount(
        uint256 blockHeight,
        uint256 count,
        uint256 version,
        IAVLMerklePath.Data[] memory merklePaths
    ) public view returns (uint64, uint64) {
        BlockDetail memory blockDetail = blockDetails[blockHeight];
        bytes32 oracleStateRoot = blockDetail.oracleState;
        require(
            oracleStateRoot != bytes32(uint256(0)),
            "NO_ORACLE_ROOT_STATE_DATA"
        );

        // Encode and calculate hash of count
        bytes32 dataHash = sha256(abi.encodePacked(uint64(count)));

        // Verify proof
        require(
            verifyProof(
                oracleStateRoot,
                version,
                hex"0052657175657374436f756e74",
                dataHash,
                merklePaths
            ),
            "INVALID_ORACLE_DATA_PROOF"
        );

        return (blockDetail.timeSecond, uint64(count));
    }

    /// Performs oracle state relay and oracle data verification in one go. The caller submits
    /// the encoded proof and receives back the decoded data, ready to be validated and used.
    /// @param data The encoded data for oracle state relay and data verification.
    function relayAndVerify(
        bytes calldata data
    ) external override returns (Result memory) {
        (bytes memory relayData, bytes memory verifyData) = abi.decode(
            data,
            (bytes, bytes)
        );
        (bool relayOk, ) = address(this).call(
            abi.encodePacked(this.relayBlock.selector, relayData)
        );
        require(relayOk, "RELAY_BLOCK_FAILED");
        (bool verifyOk, bytes memory verifyResult) = address(this).staticcall(
            abi.encodePacked(this.verifyOracleData.selector, verifyData)
        );
        require(verifyOk, "VERIFY_ORACLE_DATA_FAILED");
        return abi.decode(verifyResult, (Result));
    }

    /// Performs oracle state extraction and verification without saving root hash to storage in one go.
    /// The caller submits the encoded proof and receives back the decoded data, ready to be validated and used.
    /// @param data The encoded data for oracle state relay and data verification.
    function verifyOracleResult(
        bytes calldata data
    ) external view returns (Result memory) {
        (bytes memory relayData, bytes memory verifyData) = abi.decode(
            data,
            (bytes, bytes)
        );

        (
            MultiStore.Data memory multiStore,
            BlockHeaderMerkleParts.Data memory merkleParts,
            CommonEncodedVotePart.Data memory commonEncodedVotePart,
            TMSignature.Data[] memory signatures
        ) = abi.decode(
                relayData,
                (
                    MultiStore.Data,
                    BlockHeaderMerkleParts.Data,
                    CommonEncodedVotePart.Data,
                    TMSignature.Data[]
                )
            );

        (
            ,
            Result memory result,
            uint256 version,
            IAVLMerklePath.Data[] memory merklePaths
        ) = abi.decode(
                verifyData,
                (uint256, Result, uint256, IAVLMerklePath.Data[])
            );

        return
            verifyResultWithRoot(
                verifyBlockHeader(
                    multiStore,
                    merkleParts,
                    commonEncodedVotePart,
                    signatures
                ),
                version,
                result,
                merklePaths
            );
    }

    /// Performs oracle state relay and many times of oracle data verification in one go. The caller submits
    /// the encoded proof and receives back the decoded data, ready to be validated and used.
    /// @param data The encoded data for oracle state relay and an array of data verification.
    function relayAndMultiVerify(
        bytes calldata data
    ) external override returns (Result[] memory) {
        (bytes memory relayData, bytes[] memory manyVerifyData) = abi.decode(
            data,
            (bytes, bytes[])
        );
        (bool relayOk, ) = address(this).call(
            abi.encodePacked(this.relayBlock.selector, relayData)
        );
        require(relayOk, "RELAY_BLOCK_FAILED");

        Result[] memory results = new Result[](manyVerifyData.length);
        for (uint256 i = 0; i < manyVerifyData.length; i++) {
            (bool verifyOk, bytes memory verifyResult) = address(this)
                .staticcall(
                    abi.encodePacked(
                        this.verifyOracleData.selector,
                        manyVerifyData[i]
                    )
                );
            require(verifyOk, "VERIFY_ORACLE_DATA_FAILED");
            results[i] = abi.decode(verifyResult, (Result));
        }

        return results;
    }

    /// Performs oracle state relay and requests count verification in one go. The caller submits
    /// the encoded proof and receives back the decoded data, ready to be validated and used.
    /// @param data The encoded data
    function relayAndVerifyCount(
        bytes calldata data
    ) external override returns (uint64, uint64) {
        (bytes memory relayData, bytes memory verifyData) = abi.decode(
            data,
            (bytes, bytes)
        );
        (bool relayOk, ) = address(this).call(
            abi.encodePacked(this.relayBlock.selector, relayData)
        );
        require(relayOk, "RELAY_BLOCK_FAILED");

        (bool verifyOk, bytes memory verifyResult) = address(this).staticcall(
            abi.encodePacked(this.verifyRequestsCount.selector, verifyData)
        );
        require(verifyOk, "VERIFY_REQUESTS_COUNT_FAILED");

        return abi.decode(verifyResult, (uint64, uint64));
    }

    /// Verifies validity of the given data in the Oracle store. This function is used for both
    /// querying an oracle request and request count.
    /// @param rootHash The expected rootHash of the oracle store.
    /// @param version Lastest block height that the data node was updated.
    /// @param key The encoded key of an oracle request or request count.
    /// @param dataHash Hashed data corresponding to the provided key.
    /// @param merklePaths Merkle proof that shows how the data leave is part of the oracle iAVL.
    function verifyProof(
        bytes32 rootHash,
        uint256 version,
        bytes memory key,
        bytes32 dataHash,
        IAVLMerklePath.Data[] memory merklePaths
    ) private pure returns (bool) {
        bytes memory encodedVersion = Utils.encodeVarintSigned(version);

        bytes32 currentMerkleHash = sha256(
            abi.encodePacked(
                uint8(0), // Height of tree (only leaf node) is 0 (signed-varint encode)
                uint8(2), // Size of subtree is 1 (signed-varint encode)
                encodedVersion,
                uint8(key.length), // Size of data key
                key,
                uint8(32), // Size of data hash
                dataHash
            )
        );

        // Goes step-by-step computing hash of parent nodes until reaching root node.
        for (uint256 idx = 0; idx < merklePaths.length; ++idx) {
            currentMerkleHash = merklePaths[idx].getParentHash(
                currentMerkleHash
            );
        }

        // Verifies that the computed Merkle root matches what currently exists.
        return currentMerkleHash == rootHash;
    }
}
