# Bridge contract

## Table of contents

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Bridge contract](#bridge-contract)
  - [Table of contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Utility Functions](#utility-functions)
  - [Dependencies](#dependencies)
  - [Lite Client Verification Overview](#lite-client-verification-overview)
    - [Getting the proof from BandChain](#getting-the-proof-from-bandchain)
    - [Proof Structure](#proof-structure)
  - [Bridge Data structure \& storage](#bridge-data-structure--storage)
    - [Structs](#structs)
      - [ValidatorWithPower](#validatorwithpower)
      - [Result](#result)
      - [BlockDetail](#blockdetail)
      - [IAVLMerklePath](#iavlmerklepath)
      - [MultiStoreProof](#multistoreproof)
      - [BlockHeaderMerkleParts](#blockheadermerkleparts)
      - [TMSignature](#tmsignature)
      - [CommonEncodedVotePart](#commonencodedvotepart)
    - [Storages](#storages)
      - [totalValidatorPower](#totalvalidatorpower)
      - [validatorPowers](#validatorpowers)
      - [blockDetails](#blockdetails)
      - [encodedChainID](#encodedchainid)
  - [Brige Functions](#brige-functions)
    - [getNumberOfValidators](#getnumberofvalidators)
    - [getValidators](#getvalidators)
    - [getAllValidatorPowers](#getallvalidatorpowers)
    - [getValidatorPower](#getvalidatorpower)
    - [updateValidatorPowers](#updatevalidatorpowers)
    - [relayBlock](#relayblock)
    - [verifyOracleData](#verifyoracledata)
    - [verifyRequestsCount](#verifyrequestscount)
    - [relayAndVerify](#relayandverify)
    - [relayAndMultiVerify](#relayandmultiverify)
    - [relayAndVerifyCount](#relayandverifycount)
    - [verifyProof](#verifyproof)
  - [Util Functions](#util-functions)
    - [merkleLeafHash](#merkleleafhash)
    - [merkleInnerHash](#merkleinnerhash)
    - [encodeVarintUnsigned](#encodevarintunsigned)
    - [encodeVarintSigned](#encodevarintsigned)
    - [encodeTime](#encodetime)
    - [getParentHash](#getparenthash)
    - [getBlockHeader](#getblockheader)
    - [getAppHash](#getapphash)
    - [checkPartsAndEncodedCommonParts](#checkpartsandencodedcommonparts)
    - [checkTimeAndRecoverSigner](#checktimeandrecoversigner)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

Band Protocol provide a way for other blockchains to access off-chain information through our decentralized oracle. As part of that offering, we also provide a specification of lite client verification for anyone who requested data from our oracle to verify the validity of the result they received. We call the instance of lite client that is existed on other blockchains **Bridge**. The implementation of **Bridge** can be a smart contract (additional logic published by user) or a module (build in logic of a blockchain).

## Utility Functions

To implement the **Bridge** we only need two utility functions.

- 1. [sha256](https://en.wikipedia.org/wiki/SHA-2)
  - see python example implementation [here](../../example_utils_functions/sha256.py)
- 2. [ecrecover](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)
  - see python example implementation [here](../../example_utils_functions/secp256k1.py)

## Dependencies

- **OBI** or Oracle Binary Encoding is the standard way to serialize and deserialize binary data in the Bandchain ecosystem.
  - see OBI wiki page [here](https://github.com/bandprotocol/bandchain/wiki/Oracle-Binary-Encoding-(OBI))
  - see example implementations [here](https://github.com/bandprotocol/bandchain/tree/master/obi)

- **ProtobufLib** or Oracle Binary Encoding is the standard way to serialize and deserialize binary data in the BandChain ecosystem.
  - we adopted the lib from [here](https://github.com/lazyledger/protobuf3-solidity-lib/blob/master/contracts/ProtobufLib.sol)
  - see the .sol file [here](./library/ProtobufLib.sol)

## Lite Client Verification Overview

When the client needs external data, they will come to the oracle. In our case, they will come to the Bandchain and make a request transaction. After that, the oracle mechanic behind will gather the result for the request, which will be stored persistently in the chain's state.
Once the client saw the oracle result, they proceed to verify that the result actually comes from Bandchain.
They do this by gathering a Bandchain's block with enough `signatures` and relaying that block to the `Bridge`. If block relaying was successful, they could verify their result using a Merkle proof-like scheme. This process aims to ensure that the data received is part of Bandchain's state and is signed by a sufficient number of Bandchain's block validators.

The signatures were created by validators signing the message on [Tendermint](https://github.com/tendermint/tendermint/tree/v0.34.x) called [CanonicalVote](https://github.com/tendermint/tendermint/blob/v0.34.x/spec/core/data_structures.md#canonicalvote). The [CanonicalVote](https://github.com/tendermint/tendermint/blob/v0.34.x/spec/core/data_structures.md#canonicalvote) is composed of six fields. Some of those fields have their sub-fields containing the block hash. The diagram below help explain the [CanonicalVote](https://github.com/tendermint/tendermint/blob/v0.34.x/spec/core/data_structures.md#canonicalvote) message by expanding its struct, which includes the structs of the internal fields as well.

```go
type SignedMsgType int32

type CanonicalPartSetHeader struct {
    Total   uint32  `protobuf:"varint,1,opt,name=total`
    Hash    []byte  `protobuf:"bytes,2,opt,name=hash`
}

type CanonicalBlockID struct {
    // This is the block hash
    Hash            []byte                  `protobuf:"bytes,1,opt,name=hash`
    PartSetHeader   CanonicalPartSetHeader  `protobuf:"bytes,2,opt,name=part_set_header`
}

type CanonicalVote struct {
    Type        SignedMsgType       `protobuf:"varint,1,opt,name=type`
    Height      int64               `protobuf:"fixed64,2,opt,name=height`
    Round       int64               `protobuf:"fixed64,3,opt,name=round`
    BlockID     *CanonicalBlockID   `protobuf:"bytes,4,opt,name=block_id`
    Timestamp   time.Time           `protobuf:"bytes,5,opt,name=timestamp`
    ChainID     string              `protobuf:"bytes,6,opt,name=chain_id`
}
```

As the validators must sign on the [CanonicalVote](https://github.com/tendermint/tendermint/blob/v0.34.x/spec/core/data_structures.md#canonicalvote), most fields and sub-fields are the same for all validators except the `Timestamp`. Each validator can come up with their own `Timestamp`, which can be different from others.
Most of the [CanonicalVote](https://github.com/tendermint/tendermint/blob/v0.34.x/spec/core/data_structures.md#canonicalvote) 's parts can be included directly in the lite-client-proof except the `block hash` (`CanonicalVote.BlockID.Hash`), which need to be calculated on the client chain.
In the diagram below, the `block hash` will be calculated by hashing the raw data from the bottom of the tree upwards to the root.

```text
                                            __ [BlockHash] __
                                  _________|                 |___________
                                 |                                       |
                               [3α]                                    [3ß]
                       ________|  |_______                     ________|  |________
                      |                   |                   |                    |
                  _ [2α] _            _ [2ß] _             _ [2Γ] _               [2Δ]
                 |        |          |        |           |        |              |  |
               [1α]      [1ß]      [1Γ]      [1Δ]       [1ε]      [1ζ]          [γ]  [ω]
               |  |      |  |      |  |      |  |       |  |      |  |
             [0]  [1]  [2]  [3]  [4]  [5]  [6]  [7]   [8]  [9]  [α]  [β]
                                                                 |
                                                                 |
                                                                 |
                                             ________________[AppHash]_________________
                                            /                                          \
                        _________________[I14]_________________                     __[I15]__
                       /                                        \				           /         \
            _______[I12]______                          _______[I13]________     [G]         [H]
           /                  \                        /                    \
      __[I8]__             __[I9]__                __[I10]__              __[I11]__
     /         \          /         \            /          \            /         \
   [I0]       [I1]     [I2]        [I3]        [I4]        [I5]        [I6]       [I7]
  /   \      /   \    /    \      /    \      /    \      /    \      /    \     /    \
[0]   [1]  [2]   [3] [4]   [5]  [6]    [7]  [8]    [9]  [A]    [B]  [C]    [D]  [E]   [F]

# Leafs of BlockHash tree
[0] - version               [1] - chain_id            [2] - height        [3] - time
[4] - last_block_id         [5] - last_commit_hash    [6] - data_hash     [7] - validators_hash
[8] - next_validators_hash  [9] - consensus_hash      [α] - app_hash      [β] - last_results_hash
[γ] - evidence_hash         [ω] - proposer_address

# Leafs of AppHash tree
[0] - acc (auth) [1] - authz    [2] - bank     [3] - capability [4] - crisis   [5] - dist
[6] - evidence   [7] - feegrant [8] - gov      [9] - ibccore    [A] - icahost  [B] - mint
[C] - oracle     [D] - params   [E] - slashing [F] - staking    [G] - transfer [H] - upgrade
```

As described above, the entire process can be divided into two parts.

1. **relay_block**: Verify that an `oracle module` **_[C]_** root hash module really exist on Bandchain at a specific block and then save that root hash into **Bridge**'s state. This process requires the signatures of several validators signed on the block hash in which everyone who signs must have a total voting power greater than or equal to two-thirds of the entire voting power. The block hash is made up of multiple values that come from the Bandchain state, where `oracle module`**_[C]_** root hash is one of them.
2. **verify_oracle_data**: Verify a specific value that store under `oracle module`**_[C]_** is really existed by hashing the corresponding node's from bottom to top.

- **n** is the height of IAVL merkle tree
- **value** is bytes, which is the encoded of the actual data stored under the `oracle module` **_[C]_**.
- **H(n)** is an `oracle module` **_[C]_** root hash from the previous diagram.
  - **H(0)** is derived from the **value**
- **C(i)** is a corresponding node to H(i) where **i ∈ {0,1,2,...,n-1}** .

  ```text
                      H(n) is the same as [B] from the previous diagram
  
                            _______________[H(n)]_______________
                          /                                      \
              _______[H(n-1)]______                             [C(n-1)]
            /                      \                          /        \
        [C(n-2)]                    \                       ...        ...
       /        \                    .
     ...        ...                   .
                                       .
                                        \
                                         \
                                _______[H(2)]______
                              /                    \
                           [H(1)]                 [C(1)]
                         /        \             /        \
                      [H(0)]     [C(0)]       ...        ...
                      [value]
  ```

### Getting the proof from BandChain

Usually, the client can use the Tendermint RPC call to ask for the information they need to construct the proof.
However, we have implemented an endpoint to make this process easier. Our proof endpoint on the mainnet is `https://laozi4.bandchain.org/api/oracle/proof` + `/<A_SPECIFIC_REQUEST_ID>`.

Please see this example [proof of the request number 11124603](https://laozi4.bandchain.org/api/oracle/proof/11124603).

### Proof Structure

Example proof struct

**_Please note that this example cut out some of the `merkle_paths` and `signatures` to make it easier to read._**

```json
{
    "block_height":"9023063",
    "oracle_data_proof":{
        "result":{
            "oracle_script_id":"37",
            "calldata":"AAAAIN8cxc1vvrIbADsPV8GCSs5LhNVrln97PJVTl25QjoqyAAAAAGK0IkkAAAAUAGMEZobkbcbxWRi2GuKxIUWFNKU=",
            "ask_count":"16",
            "min_count":"1",
            "request_id":"11124603",
            "ans_count":"13",
            "request_time":"1661414867",
            "resolve_time":"1661414873",
            "resolve_status":1,
            "result":"AAAAUMLDALuONqBE8bh9vcXMZxtS2z2aFEyCTwRxz8rawrix4E9ApDNCcFv5o3NMyb666tyIrNYkN1XiKu/1SBKUbI783wBkUzYdtqMAJ4bhKpUKAAAAQLx5jr83yZAYwkq0AJBypNfuMRWa/iaE9oW82KLlZ4IinQlOmVtWnh/ZR1O2RNtbBbe5FZfkHDVWa1gjPYLEcEw="
        },
        "version":"9023058",
        "merkle_paths":[
            {
                "is_data_on_right":true,
                "subtree_height":1,
                "subtree_size":"2",
                "subtree_version":"9023058",
                "sibling_hash":"BC49843DE942EFC722E33DF11A0F2D5F535C46E88BC0A73619ACE776DE30FF81"
            },
            {
                "is_data_on_right":true,
                "subtree_height":3,
                "subtree_size":"5",
                "subtree_version":"9023059",
                "sibling_hash":"40E1F726F0A1C5CB8589A22A665E9CA9C5D09468A746ED78D20D2E7DB0946831"
            }
        ]
    },
    "block_relay_proof":{
        "multi_store_proof":{
            "auth_to_fee_grant_stores_Merkle_hash":"12BC0C7C74ABB52A53B80DCD2006077842ABDD6370A765C37A1AA607B05EB08F",
            "gov_to_ibc_core_stores_merkle_hash":"901C6E9F2615AECEACCA2CB2E5AEB9FD6BAA411637E04C79D8AC3FC6BE852A52",
            "mint_store_merkle_hash":"96AC1DE3D6B0DB2E725C2797396917B0EB4C5EE924BA115F985F026BF56BD33E",
            "oracle_iavl_State_hash":"CED5C04B645F2FC4FE09390D4CB10D945F3D8D1EFCB7A5D0C03CE4A62ECB344C",
            "params_to_transfer_stores_merkle_hash":"02A2938AB10B9470FD0F6D6FE9FBDA3E9158CA305C9C862C786D63BB3E56C46A",
            "upgrade_store_merkle_hash":"C9C8849ED125CC7681329C4D27B83B1FC8ACF7A865C9D1D1DF575CCA56F48DBE"
        },
        "block_header_merkle_parts":{
            "version_and_chain_id_hash":"327BB8E7C548CDA20A3F9330131E658F4BCB5BE238F5EE94D79FD5019E3F7559",
            "height":"9023063",
            "time_second":"1661414887",
            "time_nano_second":925334537,
            "last_block_id_and_other":"5CC36D89F15B2CE914E82BC8A6FAFCE35E9A2DD9F403A0119465AE27923A01C1",
            "next_validator_hash_and_consensus_hash":"0CCD14362C66E03A8E99E6CB25F523DF17DD5375521E92CD96686EAB2A2E5AE0",
            "last_results_hash":"2AD670892C7CEEDFFA685848433C20487F736029D95F4B2EA8F87FFA35031AF0",
            "evidence_and_proposer_hash":"F168695977991FEBB011BF7B88B3482C1E8352F3DBE40DE3FECE87E678EA7D98"
        },
        "common_encoded_vote_part":{
            "signed_data_prefix":"08021157AE89000000000022480A20",
            "signed_data_suffix":"1224080112208A906920FEE879E49590274DAE39CA3C7027D5AB645AF6946E316F9C51F55C0E"
        },
        "signatures":[
            {
                "r":"CE3A3511742253465E4CF8E66435D4EF3024E066C085E2FE259D12FD51B3885F",
                "s":"31C943EEC7517CF5431A1C8BB792F0D5185B69DA7F8CDDF4339636472833B0EE",
                "v":28,
                "encoded_timestamp":"08EADB9C980610B5F8A9F802"
            },
            {
                "r":"62E1DE88CBB581B5798D682F4CCD9A8E1C81C7C323D5E5DD32445633931ABD6A",
                "s":"76B6013A16AAE1FB4A4272E081ED64E81C9A462EC6D675D3E3790781BD7205F0",
                "v":27,
                "encoded_timestamp":"08EADB9C98061097C398F402"
            },
            {
                "r":"9B17F1A2338CE7079878BA2D58BFC2378C54A18AB8EBC3880A347FD5546EF9D1",
                "s":"0F2915E06D3CA4267DE2F102642DD9529CA9679D3A64B2288DAEBEB2ED9AEE91",
                "v":27,
                "encoded_timestamp":"08EADB9C980610F59AC9F702"
            }
        ]
    }
}
```

## Bridge Data structure & storage

### Structs

#### ValidatorWithPower

A structure that encapsulates the public key and the amount of voting power on Bandchain of a single validator.

| Field Name | Type      | Description                                                                                                                           |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `addr`     | `address` | validator's public key or something unique that is derived from public key such as hash of public key, compression form of public key |
| `power`    | `uint256` | validator's voting power on Bandchain                                                                                                 |

#### Result

A structure that encapsulates the information about a request on Bandchain.

| Field Name       | Type     | Description                                                                                                                                                     |
| ---------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `clientID`       | `string` | a string that refer to the requester, for example "from_scan", ...                                                                                              |
| `oracleScriptID` | `uint64` | an integer that refer to a specific oracle script on Bandchain                                                                                                  |
| `params`         | `bytes`  | an obi encode of the request's parameters, for example "000000034254430000000a" (obi encode of ["BTC", 10])                                                     |
| `askCount`       | `uint64` | the minimum number of validators necessary for the request to proceed to the execution phase. Therefore the minCount must be less than or equal to the askCount |
| `minCount`       | `uint64` | the number of validators that are requested to respond to this request                                                                                          |
| `requestID`      | `uint64` | an integer that refer to a specific request on Bandchain                                                                                                        |
| `ansCount`       | `uint64` | a number of answers that was answered by validators                                                                                                             |
| `requestTime`    | `uint64` | unix time at which the request was created on Bandchain                                                                                                         |
| `resolveTime`    | `uint64` | unix time at which the request got a number of reports/answers greater than or equal to `min_count`                                                             |
| `resolveStatus`  | `uint32` | status of the request (0=Open, 1=Success, 2=Failure, 3=Expired)                                                                                                 |
| `result`         | `bytes`  | an obi encode of the request's result, for example "0000aaaa" (obi encode of [ 43690 ])                                                                         |

#### BlockDetail

The `oracle module`**_[C]_** state which will be saved on-chain along with the time_second and time_nano_second_fraction of the block.

| Field Name               | Type      | Description                                 |
| ------------------------ | --------- | ------------------------------------------- |
| `oracleState`            | `bytes32` | oracle state root hash at this height       |
| `timeSecond`             | `uint64`  | second part of block time                   |
| `timeNanoSecondFraction` | `uint8`   | sub-second part of block time in nanasecond |

#### IAVLMerklePath

A structure of merkle proof that shows how the data leaf is part of the `oracle module`**_[C]_** tree. The proof’s content is the list of “iavl_merkle_path” from the leaf to the root of the tree.

| Field Name       | Type      | Description                                                    |
| ---------------- | --------- | -------------------------------------------------------------- |
| `isDataOnRight`  | `bool`    | whether the data is on the right subtree of this internal node |
| `subtreeHeight`  | `uint8`   | the height of this subtree                                     |
| `subtreeSize`    | `uint64`  | the size of this subtree                                       |
| `subtreeVersion` | `uint64`  | the latest block height that this subtree has been updated     |
| `siblingHash`    | `bytes32` | hash of the other child subtree                                |

#### MultiStoreProof

A structure that encapsulates sibling module hashes of the
`app_hash` **_[C]_** which are
**_[D]_**, **_[I7]_**, **_[I10]_**, **_[I12]_**, **_[I15]_**

| Field Name                          | Type      | Description                                                 |
| ----------------------------------- | --------- | ----------------------------------------------------------- |
| `oracleIAVLStateHash`               | `bytes32` | root hash of oracle state (**_[C]_**)                       |
| `paramsStoreMerkleHash`             | `bytes32` | leaf hash represents params module (**_[D]_**)              |
| `slashingToStakingStoresMerkleHash` | `bytes32` | internal node of slashing and staking modules (**_[I7]_**)  |
| `govToMintStoresMerkleHash`         | `bytes32` | internal node of gov to mint (4) modules (**_[I10]_**)      |
| `authToFeegrantStoresMerkleHash`    | `bytes32` | internal node of auth to feegrant (8) modules (**_[I12]_**) |
| `transferToUpgradeStoresMerkleHash` | `bytes32` | internal node of transfer and upgrade modules (**_[I15]_**) |

#### BlockHeaderMerkleParts

A structure that encapsulates the components of a block header that correspond to height**_[2]_** and app hash **_[A]_**.

| Field Name                          | Type      | Description                                                                           |
| ----------------------------------- | --------- | ------------------------------------------------------------------------------------- |
| `versionAndChainIdHash`             | `bytes32` | root hash of version and chain id components (**_[1α]_**)                             |
| `height`                            | `uint64`  | block height (**_[2]_**)                                                              |
| `timeSecond`                        | `uint64`  | second part of block time   (**_[3]_**)                                               |
| `timeNanoSecondFraction`            | `uint32`  | decimal part of block time in nanasecond (**_[3]_**)                                  |
| `lastBlockIdAndOther`               | `bytes32` | root hash of last block id, last commit hash, data hash, validators hash (**_[2ß]_**) |
| `nextValidatorHashAndConsensusHash` | `bytes32` | root hash of version and chain id components (**_[1ε]_**)                             |
| `lastResultsHash`                   | `bytes32` | hash of last results component (**_[B]_**)                                            |
| `evidenceAndProposerHash`           | `bytes32` | hash of evidence and proposer components (**_[2Δ]_**)                                 |

#### TMSignature

A structure that encapsulates Tendermint's CanonicalVote
 data and validator's signature for performing signer recovery for ECDSA secp256k1 signature. Tendermint's CanonicalVote data is composed of a block hash and some additional information prepended and appended to the block hash. Most parts of the sign data are the same for all validators except the timestamp. So, most parts are moved out to a single common struct, and the encoded timestamp stays with the signature.

| Field Name         | Type      | Description                                                      |
| ------------------ | --------- | ---------------------------------------------------------------- |
| `r`                | `bytes32` | a part of signature                                              |
| `s`                | `bytes32` | a part of signature                                              |
| `v`                | `uint8`   | a value that helps reduce the calculation of public key recovery |
| `encodedTimestamp` | `bytes`   | a protobuf encoded timestamp of each validator                   |

#### CommonEncodedVotePart

Tendermint's CanonicalVote data compose of block hash and some additional information prepended and appended to the block
hash. The prepended part (prefix) and the appended part (suffix) are different for each signer.

| Field Name         | Type    | Description                                       |
| ------------------ | ------- | ------------------------------------------------- |
| `signedDataPrefix` | `bytes` | The prepended part of Tendermint's precommit data |
| `signedDataSuffix` | `bytes` | The appended part of Tendermint's precommit data  |

### Storages

#### totalValidatorPower

A storage public variable that represents the total voting power of all validators.

Example

```solidity
contract Bridge {
    /// The total voting power of active validators currently on duty.
    uint256 public totalValidatorPower;
}
```

#### validatorPowers

A storage internal mapping from address to their voting power.
In our implementation, we using the EnumerableMap to make the keep tracking of the validators set easier.

Example

```solidity
contract Bridge {
    /// Mapping from an address to its voting power.
    EnumerableMap.AddressToUintMap private validatorPowers;
}
```

#### blockDetails

A storage public mapping that has the ability to map a positive integer (block height of Bandchain) to a struct `BlockDetail`.

Example

```solidity
contract Bridge {
    /// Mapping from block height to the struct that contains block time and hash of "oracle" iAVL Merkle tree.
    mapping(uint256 => BlockDetail) public blockDetails;
}
```

#### encodedChainID

A storage public variable that represents protobuf encoded chain_id of the specific Bandchain (testnet, mainnet, etc). The encoding always assume that the protobuf index is 6 according to the `CanonicalVote` struct.

Example

```solidity
contract Bridge {
    /// The encoded chain's ID of Band.
    bytes public encodedChainID;
}
```

## Brige Functions

### getNumberOfValidators

Get the total number of active validators currently on duty.

**params**

```
no parameters
```

**return values**

| Type      | Description              |
| --------- | ------------------------ |
| `uint256` | The number of validators |

### getValidators

Get the total number of active validators currently on duty.

**params**

| Type      | Field Name | Description          |
| --------- | ---------- | -------------------- |
| `uint256` | offset     | starting index       |
| `uint256` | size       | amount of validators |

**return values**

| Type                   | Description                             |
| ---------------------- | --------------------------------------- |
| `ValidatorWithPower[]` | an array of struct `validatorWithPower` |

### getAllValidatorPowers

The same is `getValidators` but return every active validators.

**params**

```
no parameters
```

**return values**

| Type                   | Description                             |
| ---------------------- | --------------------------------------- |
| `ValidatorWithPower[]` | an array of struct `validatorWithPower` |

### getValidatorPower

Get voting power of a validator on Bandchain from the storage `validatorPowers`. This function receive the validator's address (or hash of the public key) and then return a struct `validatorWithPower`.

**params**

| Type      | Field Name | Description                        |
| --------- | ---------- | ---------------------------------- |
| `address` | validator  | The Ethreum address of a validator |

**return values**

| Type                 | Description                   |
| -------------------- | ----------------------------- |
| `ValidatorWithPower` | a struct `validatorWithPower` |

### updateValidatorPowers

Update validator powers by `VALIDATORS_UPDATER_ROLE`. This function receives an array of struct `validatorWithPower` and then updates storages `validatorPowers`` and `totalVotingPower`. The encoded format of the array of struct `validatorWithPower` can be used instead in case the platform does not support the use of the complex type parameters.

**params**

| Type                 | Field Name | Description                             |
| -------------------- | ---------- | --------------------------------------- |
| `ValidatorWithPower` | validators | An array of struct `validatorWithPower` |

**return values**

```
no return value
```

### relayBlock

This function relays a new `oracle module` **_[B]_** hash to the `Bridge`.

**params**

| Type                     | Field Name            | Description                                               |
| ------------------------ | --------------------- | --------------------------------------------------------- |
| `MultiStore`             | multiStore            | Extra multi store to compute app hash                     |
| `BlockHeaderMerkleParts` | merkleParts           | Extra merkle parts to compute block hash                  |
| `CommonEncodedVotePart`  | commonEncodedVotePart | The common part of a block that all validators agree upon |
| `TMSignature`            | signatures            | The signatures signed on this block                       |

**return values**

```
no return value
```

1. Calculate `AppHash` by calling [getAppHash](#getAppHash)(`MultiStoreProof`).

2. Calculate `BlockHash` by calling [getBlockHeader](#getBlockHeader)(`data`, `appHash`).

3. Loop to recover every signature from `signatures`. In each round, we will get the address of the validator who has signed on the hash of `CanonicalVote`.

   - Check that there is no repeated address.
   - Read validator's voting power from storage [votingPowers](#votingPowers) by the public key that just recovered. If the public key is not found then the voting power should be 0.
   - Accumulate the voting power

4. Check that the accumulation of voting power should be greater than or equal 2/3 of the [totalValidatorPower](#totalValidatorPower).

5. Save the `oracle module` **_[B]_** hash to the storage [oracleState](#oracleState).


### verifyOracleData

This function verifies that the given data is valid data on Bandchain as of the given block height.

**params**

| Type               | Field Name  | Description                                                           |
| ------------------ | ----------- | --------------------------------------------------------------------- |
| `uint256`          | blockHeight | Block height of BancChain                                             |
| `Result`           | result      | The result of the request                                             |
| `uint256`          | version     | Lastest block height that the data node was updated                   |
| `IAVLMerklePath[]` | merklePaths | Merkle proof that shows how the data leave is part of the oracle iAVL |

**return values**

| Type     | Description               |
| -------- | ------------------------- |
| `Result` | The result of the request |

```text
n is the height of IAVL merkle tree.

H(0) is sha256(bytes([0]) + bytes([2]) + encode_varint_signed(version) + bytes([9]) + b"\xff" + request_id.to_bytes(8,'big') + bytes([32]) + sha256(obi_encode(request_packet_and_respond_packet)))

H(n) is an oracle module root hash from the previous diagram.

C(i) is a corresponding node to H(i) where i ∈ {0,1,2,...,n-1}.

H(i+1) is get_parent_hash(C(i), H(i)).

                      _______________[H(n)]_______________
                    /                                      \
        _______[H(n-1)]______                             [C(n-1)]
      /                      \                          /        \
  [C(n-2)]                    \                       ...        ...
  /        \                    .
...        ...                   .
                                  .
                                  \
                                    \
                          _______[H(2)]______
                        /                    \
                      [H(1)]                 [C(1)]
                    /        \             /        \
                 [H(0)]     [C(0)]       ...        ...
                 [value]
```

1. Read the `oracle module` **_[C]_** hash from the given `blockHeight` to check if it is available or not.

   - If the `oracle module` **_[C]_** hash is not available for the given `blockHeight` then `revert`
   - Else contiune

2. Calculate `H(0)`

3. Calculate the hash of the parent node of H(i) and C(i) hash by hashing from the bottom to the top according to [`merkle tree`](https://en.wikipedia.org/wiki/Merkle_tree) hashing scheme.

   - For i ∈ {0,1,2,...,n-1},`H(i+1)` = [getParentHash](#getParentHash)(C(i), H(i))

4. Check that `H(n)` must equal to `oracle module` **_[C]_** hash that just read from the storage in step 1.

   - If `H(n)` != `oracle module` **_[C]_** hash then `revert`
   - Else continue

5. return `result`

### verifyRequestsCount

This function verifies that the given request count is information on Bandchain at the given block height.

**params**

| Type               | Field Name  | Description                                                           |
| ------------------ | ----------- | --------------------------------------------------------------------- |
| `uint256`          | blockHeight | The block height                                                      |
| `uint256`          | count       | The requests count on the block                                       |
| `uint256`          | version     | Lastest block height that the data node was updated                   |
| `IAVLMerklePath[]` | merklePaths | Merkle proof that shows how the data leave is part of the oracle iAVL |

**return values**

| Type     | Description        |
| -------- | ------------------ |
| `uint64` | time of the block  |
| `uint64` | The requests count |

### relayAndVerify

This function performs oracle state relay and oracle data verification in one go. The caller submits the obi encoded proof and receives back the decoded data, ready to be validated and used.

**params**

| Type    | Field Name | Description                                                   |
| ------- | ---------- | ------------------------------------------------------------- |
| `bytes` | data       | The encoded data for oracle state relay and data verification |

**return values**

| Type     | Description                      |
| -------- | -------------------------------- |
| `Result` | The result of the oracle request |

1. Decode the `proof` using obi into 7 elements which are `blockHeight`, `multiStore`, `merkleParts`, `signatures`, `result`, `version` and `merklePaths`.

2. Relay the `oracle module` **_[C]_** to the state by calling the function [relayBlock](#relayBlock) with `multiStore`, `merkleParts`, `commonEncodedVotePart` and `signatures` as parameters.

3. Return the result from calling function [verifyOracleData](#verifyOracleData) with `blockHeight`,`result`, `version` and `merklePaths` as parameters.

### relayAndMultiVerify

This function is like the `relayAndVerify` but the input contains multiple of `IAVLMerklePath[]` for multiple requests.

### relayAndVerifyCount
This function is like the `relayAndVerify` but uses the `verifyRequestsCount` instead of the `verifyOracleData`.

### verifyProof

This function is able to verify any data stored under the `oracle module` **_[C]_** by providing the data hash to the function.


## Util Functions

### merkleLeafHash

This function receives bytes and then does the following steps.

1. prepend the `input` with a zero byte.
2. return [sha256](#utility-functions) of the result from `1.`.

**params**

| Type    | Field Name | Description |
| ------- | ---------- | ----------- |
| `bytes` | value      | Any bytes   |

**return values**

| Type      | Description                                |
| --------- | ------------------------------------------ |
| `bytes32` | [sha256](#utility-functions)(0x00 + input) |

### merkleInnerHash

This function takes two bytes `left` and `right` and then do these the following steps.

1. append `left` with `right` and then prepend it with a byte 01.
2. return sha256 of the result from `1.`.

**params**

| Type    | Field Name | Description |
| ------- | ---------- | ----------- |
| `bytes` | value      | Any bytes   |

**return values**

| Type      | Description                                       |
| --------- | ------------------------------------------------- |
| `bytes32` | [sha256](#utility-functions)(0x01 + left + right) |

### encodeVarintUnsigned

This function receives an integer as an input and then returns an [encode varint unsigned integer`](https://protobuf.dev/programming-guides/encoding/#varints).

**params**

| Type      | Field Name | Description          |
| --------- | ---------- | -------------------- |
| `uint256` | value      | Any unsigned integer |

**return values**

| Type    | Description                         |
| ------- | ----------------------------------- |
| `bytes` | Encode varint unsigned of the value |

### encodeVarintSigned

This function receives an integer as an `input` and then returns an [`encode varint signed integer`](https://protobuf.dev/programming-guides/encoding/#signed-ints). We can say it basically returns the result of encode_varint_unsigned on input ⨯ 2

**params**

| Type      | Field Name | Description        |
| --------- | ---------- | ------------------ |
| `uint256` | value      | Any signed integer |

**return values**

| Type    | Description                       |
| ------- | --------------------------------- |
| `bytes` | Encode varint signed of the value |


### encodeTime

This function takes a second and sub-second and returns tendermint time encoded.

**params**

| Type     | Field Name | Description              |
| -------- | ---------- | ------------------------ |
| `uint64` | second     | time in second           |
| `uint32` | nanoSecond | sub-second in nanosecond |

**return values**

| Type    | Description |
| ------- | ----------- |
| `bytes` | Encode time |

### getParentHash

This function takes a struct `IAVLMerklePath` (sibling of current node) and current subtree hash, then return the parent hash of them.

**params**

| Type             | Field Name      | Description                     |
| ---------------- | --------------- | ------------------------------- |
| `IAVLMerklePath` | data            | A struct `iavl_merkle_path`     |
| `bytes`          | dataSubtreeHash | The hash of a node in IAVL tree |

**return values**

| Type      | Description                   |
| --------- | ----------------------------- |
| `bytes32` | The paremt hash of both nodes |

### getBlockHeader

This function receives 2 parameters which are struct `BlockHeaderMerkleParts` and `appHash`**_[A]_**. It will calculate and return the `BlockHash` according to [`merkle tree`](https://en.wikipedia.org/wiki/Merkle_tree) hashing scheme.

```text
                                __ [BlockHash] __
                      _________|                 |___________
                     |                                       |
                   [3α]                                    [3ß]
           ________|  |_______                     ________|  |________
          |                   |                   |                    |
      _ [2α] _            _ [2ß] _             _ [2Γ] _               [2Δ]
     |        |          |        |           |        |              |  |
   [1α]      [1ß]      [1Γ]      [1Δ]       [1ε]      [1ζ]          [γ]  [ω]
   |  |      |  |      |  |      |  |       |  |      |  |
 [0]  [1]  [2]  [3]  [4]  [5]  [6]  [7]   [8]  [9]  [α]  [β]

# Leafs of BlockHash tree
[0] - version               [1] - chain_id            [2] - height        [3] - time
[4] - last_block_id         [5] - last_commit_hash    [6] - data_hash     [7] - validators_hash
[8] - next_validators_hash  [9] - consensus_hash      [α] - app_hash      [β] - last_results_hash
[γ] - evidence_hash         [ω] - proposer_address
```

1. **_[2]_** = [merkleLeafHash](#merkleLeafHash)([encodeVarintUnsigned](#encodeVarintUnsigned)(`block_height`))

2. **_[3]_** = [merkleLeafHash](#merkleLeafHash)([encodeTime](#encodeTime)(`time_second, time_nano_second`))

3. **_[1ß]_** = [merkleInnerHash](#merkleInnerHash)(**_[2]_**, **_[3]_**)

4. **_[2α]_** = [merkleInnerHash](#merkleInnerHash)(`version_and_chain_id_hash`**_[1α]_**, **_[1ß]_**)

5. **_[3α]_** = [merkleInnerHash](#merkleInnerHash)(**_[2α]_**, `last_block_id_and_other`**_[2ß]_**)

6. **_[A]_** = [merkleLeafHash](#merkleLeafHash)(bytes([32]) + `app_hash`) // Prepend with a byte of 32 or 0x20

7. **_[1ζ]_** = [merkleInnerHash](#merkleInnerHash)(**_[A]_**, `last_results_hash`**_[B]_**)

8. **_[2Γ]_** = [merkleInnerHash](#merkleInnerHash)(`next_validator_hash_and_consensus_hash`**_[1ε]_**, **_[1ζ]_**)

9. **_[3ß]_** = [merkleInnerHash](#merkleInnerHash)(**_[2Γ]_**, `evidence_and_proposer_hash`**_[2Δ]_**)

10. `BlockHash` = [merkleInnerHash](#merkleInnerHash)(**_[3α]_**,**_[3ß]_**)

11. return `BlockHash`

**params**

| Type                     | Field Name | Description                       |
| ------------------------ | ---------- | --------------------------------- |
| `BlockHeaderMerkleParts` | data       | A struct `BlockHeaderMerkleParts` |
| `bytes32`                | appHash    | Application root hash             |

**return values**

| Type      | Description                          |
| --------- | ------------------------------------ |
| `bytes32` | The block hash calculated from input |

### getAppHash

This function receives a struct `MultiStoreProof` as an input and then returns the `AppHash` by the calculation according to [`merkle tree`](https://en.wikipedia.org/wiki/Merkle_tree) hashing scheme.

```text
                                             ________________[AppHash]_________________
                                            /                                          \
                        _________________[I14]_________________                     __[I15]__
                       /                                        \				           /         \
            _______[I12]______                          _______[I13]________     [G]         [H]
           /                  \                        /                    \
      __[I8]__             __[I9]__                __[I10]__              __[I11]__
     /         \          /         \            /          \            /         \
   [I0]       [I1]     [I2]        [I3]        [I4]        [I5]        [I6]       [I7]
  /   \      /   \    /    \      /    \      /    \      /    \      /    \     /    \
[0]   [1]  [2]   [3] [4]   [5]  [6]    [7]  [8]    [9]  [A]    [B]  [C]    [D]  [E]   [F]

# Leafs of AppHash tree
[0] - acc (auth) [1] - authz    [2] - bank     [3] - capability [4] - crisis   [5] - dist
[6] - evidence   [7] - feegrant [8] - gov      [9] - ibccore    [A] - icahost  [B] - mint
[C] - oracle     [D] - params   [E] - slashing [F] - staking    [G] - transfer [H] - upgrade
```

Firstly, calculate double sha256 of MultiStoreProof.oracle_iavl_state_hash and then prepend with oracle prefix (uint8(6) + "oracle" + uint8(32)) and then calculate merkleLeafHash

1. **_[C]_** = [merkleLeafHash](#merkleLeafHash)(0x066f7261636c6520 + [sha256](#utility-functions)([sha256](#utility-functions)(`oracleIAVLStateHash`)))

2. **_[I6]_** = [merkleInnerHash](#merkleInnerHash)(**_[C]_**, **_[D]_**)

3. **_[I11]_** = [merkleInnerHash](#merkleInnerHash)(**_[I6]_**, **_[I7]_**)

4. **_[I13]_** = [merkleInnerHash](#merkleInnerHash)(**_[I10]_**, **_[I11]_**)

5. **_[I14]_** = [merkleInnerHash](#merkleInnerHash)(**_[I12]_**, **_[I13]_**)

6. `AppHash` = [merkleInnerHash](#merkleInnerHash)(**_[I14]_**, **_[I15]_**)

7. return `AppHash`

**params**

| Type              | Field Name | Description                |
| ----------------- | ---------- | -------------------------- |
| `MultiStoreProof` | data       | A struct `MultiStoreProof` |

**return values**

| Type      | Description           |
| --------- | --------------------- |
| `bytes32` | Application root hash |

### checkPartsAndEncodedCommonParts

This function helps bounding the size of the prefix and suffix, which will reduce the number of valid block hashes to only one and return a common part of the message for verifying the validator signature.

**params**

| Type                    | Field Name | Description                        |
| ----------------------- | ---------- | ---------------------------------- |
| `CommonEncodedVotePart` | data       | a common encoded vote part         |
| `bytes32`               | blockHash  | a specific block hash on Bandchain |

**return values**

| Type    | Description                                   |
| ------- | --------------------------------------------- |
| `bytes` | Encode packed of prefix + block hash + suffix |

### checkTimeAndRecoverSigner

This function receives a struct `TmSignature` as an input and returns a validator's public key by using [ecrecover](#utility-functions).

**params**

| Type          | Field Name        | Description                           |
| ------------- | ----------------- | ------------------------------------- |
| `TMSignature` | data              | Signature of the validator            |
| `bytes`       | commonEncodedPart | The common part of vote on this block |
| `bytes`       | encodedChainID    | The chain id of a specific Bandchain  |

**return values**

| Type      | Description                |
| --------- | -------------------------- |
| `address` | The address of a validator |
