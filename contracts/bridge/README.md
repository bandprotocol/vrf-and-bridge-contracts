# Bridge contract

## Table of contents

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents**

- [Introduction](#introduction)
- [Utility Functions](#utility-functions)
  - sha256
  - ecrecover
- [Dependencies](#dependencies)
  - OBI
  - Protobuf
- [Lite Client Verification Overview](#lite-client-verification-overview)
  - [Getting the proof from Band](#Getting_the_proof_from_Band)
  - [Proof structure](#Proof_structure)
- [Bridge contract](#bridge-contract)
  - [Structs](#structs)
    - [validator_with_power](#validator_with_power)
    - [result](#result)
    - [iavl_merkle_path](#iavl_merkle_path)
    - [multi_store_proof](#multi_store_proof)
    - [block_header_merkle_parts](#block_header_merkle_parts)
    - [tm_signature](#tm_signature)
    - [block_detail](#block_detail)
    - [common_encoded_vote_part](#common_encoded_vote_part)
  - [Storages](#Storages)
    - [total_validator_power](#total_validator_power)
    - [validator_powers](#validator_powers)
    - [block_details](#block_details)
    - [encoded_chain_id](#encoded_chain_id)
  - [Functions](#bridge's-functions)
    - [get_total_validator_power](#get_total_validator_power)
    - [get_number_of_validators](#get_number_of_validators)
    - [get_validators](#get_validators)
    - [get_all_validators](#get_all_validators)
    - [get_oracle_state](#get_oracle_state)
    - [get_validator_power](#get_validator_power)
    - [merkle_leaf_hash](#merkle_leaf_hash)
    - [merkle_inner_hash](#merkle_inner_hash)
    - [encode_varint_unsigned](#encode_varint_unsigned)
    - [encode_varint_signed](#encode_varint_signed)
    - [get_block_header](#get_block_header)
    - [check_parts_and_encoded_common_parts](#check_parts_and_encoded_common_parts)
    - [check_time_and_recover_signer](#check_time_and_recover_signer)
    - [get_parent_hash](#get_parent_hash)
    - [relay_block](#relay_block)
    - [verify_oracle_data](#verify_oracle_data)
    - [verify_requests_count](#verify_requests_count)
    - [relay_and_verify](#relay_and_verify)
    - [relay_and_multi_verify](#relay_and_multi_verify)
    - [relay_and_verify_count](#relay_and_verify_count)
    - [verify_proof](#verify_proof)

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

- **OBI** or Oracle Binary Encoding is the standard way to serialized and deserialize binary data in the BandChain ecosystem.
  - see OBI wiki page [here](https://github.com/bandprotocol/bandchain/wiki/Oracle-Binary-Encoding-(OBI))
  - see example implementations [here](https://github.com/bandprotocol/bandchain/tree/master/obi)

- **ProtobufLib** or Oracle Binary Encoding is the standard way to serialized and deserialize binary data in the BandChain ecosystem.
  - we adopted the lib from [here](https://github.com/lazyledger/protobuf3-solidity-lib/blob/master/contracts/ProtobufLib.sol)
  - see the .sol file [here](./library/ProtobufLib.sol)

## Lite Client Verification Overview

When the client needs external data, they will come to the oracle. In our case, they will come to the Bandchain and make a request transaction. After that, the oracle mechanic behind will gather the result for the request, which will be stored persistently in the chain's state. 
Once the client saw the oracle result, they proceed to verify that the result actually comes from BandChain. 
They do this by gathering a Bandchain's block with enough `signatures` and relaying that block to the `Bridge`. If block relaying was successful, they could verify their result using a Merkle proof-like scheme. This process aims to ensure that the data received is part of BandChain's state and is signed by a sufficient number of BandChain's block validators.

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
                        _________________[I14]_________________                        [G]
                       /                                        \
            _______[I12]______                          _______[I13]________
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
[0] - auth     [1] - authz    [2] - bank    [3] - capability [4] - crisis  [5] - dist
[6] - evidence [7] - feegrant [8] - gov     [9] - ibccore    [A] - mint    [B] - oracle
[C] - params   [D] - slashing [E] - staking [F] - transfer   [G] - upgrade
```

As described above, the entire process can be divided into two parts.
1. **relay_block**: Verify that an `oracle module`<strong><em>[B]</em></strong> root hash module really exist on BandChain at a specific block and then save that root hash into **Bridge**'s state. This process requires the signatures of several validators signed on the block hash in which everyone who signs must have a total voting power greater than or equal to two-thirds of the entire voting power. The block hash is made up of multiple values that come from the BandChain state, where `oracle module`<strong><em>[B]</em></strong> root hash is one of them.
2. **verify_oracle_data**: Verify a specific value that store under `oracle module`<strong><em>[B]</em></strong> is really existed by hashing the corresponding node's from bottom to top.

  - **n** is the height of IAVL merkle tree
  - **value** is bytes, which is the encoded of the actual data stored under the `oracle module`<strong><em>[B]</em></strong>.
  - **H(n)** is an `oracle module`<strong><em>[B]</em></strong> root hash from the previous diagram.
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

### Getting_the_proof_from_Band

Usually the client can use the Tendermint RPC call to ask for the information they need to construct the proof.
However, we have implemented an endpoint to make this process easier. Our proof endpoint on the mainnet is `https://laozi4.bandchain.org/api/oracle/proof` + `/<A_SPECIFIC_REQUEST_ID>`.

Please see this example [proof of the request number 11124603](https://laozi4.bandchain.org/api/oracle/proof/11124603).

### Proof_structure

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

## Bridge contract

### Structs

#### validator_with_power

A structure that encapsulates the public key and the amount of voting power on BandChain of a single validator.

| Field Name  | Type      | Description                                                                                                                           |
| ----------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `validator` | `address` | validator's public key or something unique that is derived from public key such as hash of public key, compression form of public key |
| `power`     | `u64`     | validator's voting power on BandChain                                                                                                 |

#### result

A structure that encapsulates the information about a request on Bandchain.

| Field Name         | Type     | Description                                                                                                                                                     |
| ------------------ | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `client_id`        | `string` | a string that refer to the requester, for example "from_scan", ...                                                                                              |
| `oracle_script_id` | `u64`    | an integer that refer to a specific oracle script on BandChain                                                                                                  |
| `params`           | `bytes`  | an obi encode of the request's parameters, for example "000000034254430000000a" (obi encode of ["BTC", 10])                                                     |
| `ask_count`        | `u64`    | the minimum number of validators necessary for the request to proceed to the execution phase. Therefore the minCount must be less than or equal to the askCount |
| `min_count`        | `u64`    | the number of validators that are requested to respond to this request                                                                                          |
| `request_id`       | `u64`    | an integer that refer to a specific request on BandChain                                            |
| `ans_count`        | `u64`    | a number of answers that was answered by validators                                                 |
| `request_time`     | `u64`    | unix time at which the request was created on BandChain                                             |
| `resolve_time`     | `u64`    | unix time at which the request got a number of reports/answers greater than or equal to `min_count` |
| `resolve_status`   | `u32`    | status of the request (0=Open, 1=Success, 2=Failure, 3=Expired)                                     |
| `result`           | `bytes`  | an obi encode of the request's result, for example "0000aaaa" (obi encode of [ 43690 ])             |

#### iavl_merkle_path

A structure of merkle proof that shows how the data leaf is part of the `oracle module`<strong><em>[B]</em></strong> tree. The proof’s content is the list of “iavl_merkle_path” from the leaf to the root of the tree.

| Field Name         | Type      | Description                                                    |
| ------------------ | --------- | -------------------------------------------------------------- |
| `is_data_on_right` | `bool`    | whether the data is on the right subtree of this internal node |
| `subtree_height`   | `u8`      | the height of this subtree                                     |
| `subtree_size`     | `u64`     | the size of this subtree                                       |
| `subtree_version`  | `u64`     | the latest block height that this subtree has been updated     |
| `sibling_hash`     | `bytes32` | hash of the other child subtree                                |

#### multi_store_proof

A structure that encapsulates sibling module hashes of the 
`app_hash`<strong><em>[α]</em></strong> which are 
**_[B]_**, **_[A]_**, **_[I4]_**, **_[I11]_**, **_[I12]_**, **_[G]_**

| Field Name                              | Type      | Description                                                                            |
| --------------------------------------- | --------- | -------------------------------------------------------------------------------------- |
| `auth_to_fee_grant_stores_merkle_hash`  | `bytes32` | root hash of acc,distr,evidence,gov modules (<strong><em>[ρ5]</em></strong>)           |
| `gov_to_ibc_core_stores_merkle_hash`    | `bytes32` | root hash of main and mint modules (<strong><em>[ρ3]</em></strong>)                    |
| `mint_store_merkle_hash`                | `bytes32` | root hash of params module (<strong><em>[h]</em></strong>)                             |
| `oracle_iavl_state_hash`                | `bytes32` | root hash of oracle module (<strong><em>[B]</em></strong>)                             |
| `params_to_transfer_stores_merkle_hash` | `bytes32` | root hash of slashing,staking,supply,upgrade modules (<strong><em>[ρ10]</em></strong>) |
| `upgrade_store_merkle_hash`             | `bytes32` | root hash of slashing,staking,supply,upgrade modules (<strong><em>[ρ10]</em></strong>) |

#### block_header_merkle_parts

A structure that encapsulates the components of a block header that correspond to height<strong><em>[2]</em></strong> and app hash <strong><em>[A]</em></strong>.

| Field Name                               | Type      | Description                                                                                               |
| ---------------------------------------- | --------- | --------------------------------------------------------------------------------------------------------- |
| `version_and_chain_id_hash`              | `bytes32` | root hash of version and chain id components (<strong><em>[1α]</em></strong>)                             |
| `time_hash`                              | `bytes32` | hash of time component (<strong><em>[3]</em></strong>)                                                    |
| `last_block_id_and_other`                | `bytes32` | root hash of last block id, last commit hash, data hash, validators hash (<strong><em>[2ß]</em></strong>) |
| `next_validator_hash_and_consensus_hash` | `bytes32` | root hash of version and chain id components (<strong><em>[1ε]</em></strong>)                             |
| `last_results_hash`                      | `bytes32` | hash of last results component (<strong><em>[B]</em></strong>)                                            |
| `evidence_and_proposer_hash`             | `bytes32` | hash of evidence and proposer components (<strong><em>[2Δ]</em></strong>)                                 |

#### tm_signature

A structure that encapsulates Tendermint's CanonicalVote
 data and validator's signature for performing signer recovery for ECDSA secp256k1 signature. Tendermint's CanonicalVote data is composed of a block hash and some additional information prepended and appended to the block hash. Most parts of the sign data are the same for all validators except the timestamp. So, most parts are moved out to a single common struct, and the encoded timestamp stays with the signature. 

| Field Name           | Type      | Description                                                      |
| -------------------- | --------- | ---------------------------------------------------------------- |
| `r`                  | `bytes32 `| a part of signature                                              |
| `s`                  | `bytes32` | a part of signature                                              |
| `v`                  | `u8`      | a value that helps reduce the calculation of public key recovery |
| `encoded_timestamp`  | `bytes`   | a protobuf encoded timestamp of each validator                   |

#### block_detail

The `oracle module`<strong><em>[B]</em></strong> state which will be saved on-chain along with the time_second and time_nano_second_fraction of the block.

| Field Name                   | Type      | Description                                                      |
| ---------------------------- | --------- | ---------------------------------------------------------------- |
| `oracle_state`               | `bytes32` | a part of signature                                              |
| `time_second`                | `uint64`  | a part of signature                                              |
| `time_nano_second_fraction`  | `u8`      | a value that helps reduce the calculation of public key recovery |

#### common_encoded_vote_part

Tendermint's CanonicalVote data compose of block hash and some additional information prepended and appended to the block
hash. The prepended part (prefix) and the appended part (suffix) are different for each signer.

| Field Name           | Type                     | Description                                                      |
| -------------------- | ------------------------ | ---------------------------------------------------------------- |
| `signed_data_prefix` | `bytes`                  | The prepended part of Tendermint's precommit data                |
| `signed_data_suffix` | `bytes`                  | The appended part of Tendermint's precommit data                 |               | a protobuf encoded timestamp of each validator                   |

## Bridge's storages

#### total_validator_power

A storage variable that represent the total voting power of all validators.

Example
```solidity
contract Bridge {
    /// The total voting power of active validators currently on duty.
    uint256 public totalValidatorPower;
}
```

#### validator_powers

A storage mapping from address to the struct `validator_with_power`.
In our implementation, we using the EnumerableMap to make the keep tracking of the validators set easier.

Example
```solidity
contract Bridge {
    /// Mapping from an address to its voting power.
    EnumerableMap.AddressToUintMap private validatorPowers;
}
```

#### block_details

A storage mapping that has the ability to map a positive integer (block height of BandChain) to a struct `block_detail`.

Example
```solidity
contract Bridge {
    /// Mapping from block height to the struct that contains block time and hash of "oracle" iAVL Merkle tree.
    mapping(uint256 => BlockDetail) public blockDetails;
}
```

#### encoded_chain_id

A protobuf encoded chain-id of the specific Bandchain (testnet, mainnet, etc). The encoding always assume that the protobuf index is 6 according to the `CanonicalVote` struct.

Example
```solidity
contract Bridge {
    /// The encoded chain's ID of Band.
    bytes public encodedChainID;
}
```

## Bridge's functions

#### get_total_validator_power

Get the total voting power of active validators currently on duty.

params

```
no parameters
```

return values

| Type      | Field Name         | Description                          |
| --------- | ------------------ | ------------------------------------ |
| `uint256` | total voting power | value of `total_validator_power` |

#### get_number_of_validators

Get the total number of active validators currently on duty.

params

```
no parameters
```

return values

| Type      | Field Name           | Description                         |
| --------- | -------------------- | ----------------------------------- |
| `uint256` | number of validators | value of the `number_of_validators` |

#### get_validators

Get the total number of active validators currently on duty.

params

| Type      | Field Name | Description          |
| --------- | ---------- | -------------------- |
| `uint256` | offset     | starting index       |
| `uint256` | size       | amount of validators |

return values

| Type                   | Field Name | Description                               |
| ---------------------- | ---------- | ----------------------------------------- |
| `ValidatorWithPower[]` | validators | an array of struct `validator_with_power` |

#### get_all_validators

The same is `get_validators` but return every active validators.

params

```
no parameters
```

return values

| Type                   | Field Name | Description                               |
| ---------------------- | ---------- | ----------------------------------------- |
| `ValidatorWithPower[]` | validators | an array of struct `validator_with_power` |

#### get_oracle_state

Get the iAVL Merkle tree hash of `oracle module` **_[B]_** from given block height of the BandChain. This function should read value from the storage oracle_states and then return the value.

params

| Type      | Field Name    | Description                                                                                                                 |
| --------- | ------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `uint256` | block height  | The height of block in BandChain that the `oracle module` **_[B]_** hash was relayed on the chain where this Bridge resides |

return values

| Type          | Field Name   | Description                     |
| ------------- | ------------ | ------------------------------- |
| `BlockDetail` | block detail | a struct `block_detail` |

#### get_validator_power

Get voting power of a validator on BandChain from the storage `validator_power`. This function receive the validator's address (or hash of the public key) and then return a struct `validator_with_power`.

params

| Type    | Field Name | Description                                                                                                                                                |
| ------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bytes` | validator  | The public key of a validator or something unique that is derived from public such as hash of public key (in Ethereum block chain, we use type `address`). |

return values

| Type                 | Field Name | Description                     |
| -------------------- | ---------- | ------------------------------- |
| `ValidatorWithPower` | validators | a struct `validator_with_power` |

#### update_validator_powers

Update validator powers by owner. This function receive array of struct `validator_with_power` and then update storages `validator_power` and `total_voting_power` without returning any value. The encoded format of the array of struct `validator_with_power` can be used instead in case the platform does not support the use of the complex type parameters.

params

| Type                 | Field Name            | Description                               |
| -------------------- | --------------------- | ----------------------------------------- |
| `ValidatorWithPower` | validators with power | An array of struct `validator_with_power` |

return values

```
no return value
```

#### merkle_leaf_hash

This function receive any bytes as an `input` and then does these following step.

1. prepend the `input` with a zero byte.
2. return [sha256](#utility-functions) of the result from `1.`.

params

| Type    | Field Name | Description |
| ------- | ---------- | ----------- |
| `bytes` | `input`    | Any bytes   |

return values

| Type                     | Field Name | Description                                |
| ------------------------ | ---------- | ------------------------------------------ |
| `bytes`, fixed size = 32 | result     | [sha256](#utility-functions)(0x00 + input) |

#### merkle_inner_hash

This function takes two parameters `left` and `right`, both of them are bytes, and then does these the following steps.

1. append `left` with `right` and then prepend it with a byte 01.
2. return sha256 of the result from `1.`.

params

| Type    | Field Name | Description |
| ------- | ---------- | ----------- |
| `bytes` | `input`    | Any bytes   |

return values

| Type                     | Field Name | Description                                       |
| ------------------------ | ---------- | ------------------------------------------------- |
| `bytes`, fixed size = 32 | result     | [sha256](#utility-functions)(0x01 + left + right) |

#### encode_varint_unsigned

This function receive an integer as an `input` and then return an [encode varint unsigned of the `input`](#https://developers.google.com/protocol-buffers/docs/encoding).

params

| Type        | Field Name | Description          |
| ----------- | ---------- | -------------------- |
| any integer | `input`    | Any unsigned integer |

return values

| Type    | Field Name | Description                           |
| ------- | ---------- | ------------------------------------- |
| `bytes` | result     | Encode varint unsigned of the `input` |

#### encode_varint_signed

This function receive an integer as an `input` and then return an [`encode varint signed of the input`](#https://developers.google.com/protocol-buffers/docs/encoding). We can say it basically return [encode_varint_unsigned(input ⨯ 2)](#encode_varint_unsigned)

params

| Type        | Field Name | Description        |
| ----------- | ---------- | ------------------ |
| any integer | `input`    | Any signed integer |

return values

| Type    | Field Name | Description                         |
| ------- | ---------- | ----------------------------------- |
| `bytes` | result     | Encode varint signed of the `input` |

#### check_parts_and_encoded_common_parts

This function help bounding the size of the prefix and suffix,
which will reduce the number of valid block hashes to only one.

params

| Type      | Field Name  | Description                        |
| --------- | ----------- | ---------------------------------- |
| `bytes32` | block hash  | a specific block hash on Bandchain |

return values

| Type    | Field Name | Description                                   |
| ------- | ---------- | --------------------------------------------- |
| `bytes` | result     | Encode packed of prefix + block hash + suffix |

#### get_block_header

This function receive 3 parameters which are struct `block_header_merkle_parts`, `app_hash`**_[A]_** and `block_height`**_[2]_**. It will calculate the `BlockHash` according to [`merkle tree`](https://en.wikipedia.org/wiki/Merkle_tree) hashing scheme and then return the `BlockHash`.

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

| Type                     | Field Name  | Description                                   |
| ------------------------ | ----------- | --------------------------------------------- |
| `bytes`, fixed size = 32 | `BlockHash` | The block hash of BancChain at `block_height` |

1. **_[2]_** = [merkle_leaf_hash](#merkle_leaf_hash)([encode_varint_unsigned](#encode_varint_unsigned)(`block_height`))

2. **_[1ß]_** = [merkle_inner_hash](#merkle_inner_hash)(**_[2]_**, `block_header_merkle_parts.time_hash`**_[3]_**)

3. **_[2α]_** = [merkle_inner_hash](#merkle_inner_hash)(`block_header_merkle_parts.version_and_chain_id_hash`**_[1α]_**, **_[1ß]_**)

4. **_[3α]_** = [merkle_inner_hash](#merkle_inner_hash)(**_[2α]_**, `block_header_merkle_parts.last_block_id_and_other`**_[2ß]_**)

5. **_[A]_** = [merkle_leaf_hash](#merkle_leaf_hash)(bytes([32]) + app_hash) // Prepend with a byte of 32 or 0x20

6. **_[1ζ]_** = [merkle_inner_hash](#merkle_inner_hash)(**_[A]_**, `block_header_merkle_parts.last_results_hash`**_[B]_**)

7. **_[2Γ]_** = [merkle_inner_hash](#merkle_inner_hash)(`block_header_merkle_parts.next_validator_hash_and_consensus_hash`**_[1ε]_**, **_[1ζ]_**)

8. **_[3ß]_** = [merkle_inner_hash](#merkle_inner_hash)(**_[2Γ]_**, `block_header_merkle_parts.evidence_and_proposer_hash`**_[2Δ]_**)

9. `BlockHash` = [merkle_inner_hash](#merkle_inner_hash)(**_[3α]_**,**_[3ß]_**)

10. return `BlockHash`

params

| Type                                    | Field Name                  | Description                          |
| --------------------------------------- | --------------------------- | ------------------------------------ |
| `{bytes,bytes,bytes,bytes,bytes,bytes}` | `block_header_merkle_parts` | A struct `block_header_merkle_parts` |
| `bytes`                                 | `input`                     | Any signed integer                   |
| `u64`                                   | `input`                     | Any signed integer                   |

return values

#### get_app_hash

This function receive a struct `multi_store_proof` as an input and then return the `AppHash` by the calculation according to [`merkle tree`](https://en.wikipedia.org/wiki/Merkle_tree) hashing scheme.

```text
                                             ________________[AppHash]_________________
                                            /                                          \
                        _________________[I14]_________________                        [G]
                       /                                        \
            _______[I12]______                          _______[I13]________
           /                  \                        /                    \
      __[I8]__             __[I9]__                __[I10]__              __[I11]__
     /         \          /         \            /          \            /         \
   [I0]       [I1]     [I2]        [I3]        [I4]        [I5]        [I6]       [I7]
  /   \      /   \    /    \      /    \      /    \      /    \      /    \     /    \
[0]   [1]  [2]   [3] [4]   [5]  [6]    [7]  [8]    [9]  [A]    [B]  [C]    [D]  [E]   [F]

# Leafs of AppHash tree
[0] - auth     [1] - authz    [2] - bank    [3] - capability [4] - crisis  [5] - dist
[6] - evidence [7] - feegrant [8] - gov     [9] - ibccore    [A] - mint    [B] - oracle
[C] - params   [D] - slashing [E] - staking [F] - transfer   [G] - upgrade
```

Firstly, calculate double sha256 of multi_store_proof.oracle_iavl_state_hash and then prepend with oracle prefix (uint8(6) + "oracle" + uint8(32)) and then calculate merkle_leaf_hash

1. **_[B]_** = [merkle_leaf_hash](#merkle_leaf_hash)(0x066f7261636c6520 + [sha256](#utility-functions)([sha256](#utility-functions)(`oracleIAVLStateHash`)))

2. **_[I5]_** = [merkle_inner_hash](#merkle_inner_hash)(**_[A]_**, **_[B]_**)

3. **_[I10]_** = [merkle_inner_hash](#merkle_inner_hash)(**_[I4]_**, **_[I5]_**)

4. **_[I13]_** = [merkle_inner_hash](#merkle_inner_hash)(**_[I10]_**, **_[I11]_**)

5. **_[I14]_** = [merkle_inner_hash](#merkle_inner_hash)(**_[I12]_**, **_[I13]_**)

6. `AppHash` = [merkle_inner_hash](#merkle_inner_hash)(**_[I14]_**, **_[G]_**)

7. return `AppHash`

params

| Type                              | Field Name        | Description                  |
| --------------------------------- | ----------------- | ---------------------------- |
| `{bytes,bytes,bytes,bytes,bytes}` | multi_store_proof | A struct `multi_store_proof` |

return values

| Type                   | Field Name | Description   |
| ---------------------- | ---------- | ------------- |
| `bytes`, fix size = 32 | result     | The `AppHash` |

#### check_time_and_recover_signer

This fucntion receive a struct `tm_signature` as an input and return a validator's public key by using [ecrecover](#utility-functions).

params

| Type          | Field Name    | Description                                            |
| ------------- | ------------- | ------------------------------------------------------ |
| `bytes` | common encoded part | An encoded result from the `CommonEncodedVotePart` lib |
| `bytes` | encoded chain id    | The chain id of a specific Bandchain                   |

return values

| Type      | Field Name        | Description                |
| --------- | ----------------- | -------------------------- |
| `address` | validator address | The address of a validator |

#### get_parent_hash

This fucntion receive a struct `iavl_merkle_path` and data_subtree_hash bytes as inputs and return the parent hash of them.

params

| Type                      | Field Name        | Description                     |
| ------------------------- | ----------------- | ------------------------------- |
| `{bool,u8,u64,u64,bytes}` | iavl_merkle_path  | A struct `iavl_merkle_path`     |
| `bytes`                   | data_subtree_hash | The hash of a node in IAVL tree |

return values

| Type                      | Field Name        | Description                     |
| ------------------------- | ----------------- | ------------------------------- |
| `{bool,u8,u64,u64,bytes}` | iavl_merkle_path  | A struct `iavl_merkle_path`     |
| `bytes`                   | data_subtree_hash | The hash of a node in IAVL tree |

#### relay_block

This function relays a new `oracle module` **_[B]_** hash to the `Bridge`.

params

| Type                                    | Field Name                | Description                          |
| --------------------------------------- | ------------------------- | ------------------------------------ |
| `u64`                                   | block_height              | Block height of BancChain            |
| `{bytes,bytes,bytes,bytes,bytes}`       | multi_store_proof         | A struct `multi_store_proof`         |
| `{bytes,bytes,bytes,bytes,bytes,bytes}` | block_header_merkle_parts | A struct `block_header_merkle_parts` |
| `{bytes,bytes}`                         | common_encoded_vote_part  | A struct `common_encoded_vote_part` |
| `[{bytes,bytes,u8,bytes,bytes}]`        | signatures                | An array of struct `signatures`      |

return values

```
no return value
```

1. Calculate `AppHash` by calling [get_app_hash](#get_app_hash)(`multi_store_proof`).

2. Calculate `BlockHash` by calling [get_block_header](#get_block_header)(`block_header_merkle_parts`, `app_hash`, `block_height`).

3. Loop recover every signature from `signatures`. In each round we will get the address of the validator who have signed on the hash of `CanonicalVote`.

   - Check that there is no repeated address.
   - Read validator's voting power from storage [voting_powers](#voting_powers) by the public key that just recovered. If the public key is not found then the voting power should be 0.
   - Accumulate the voting power

4. Check that the accumulate of voting power should be greater than or equal 2/3 of the [total_validator_power](#total_validator_power).

5. Save the `oracle mudule` **_[B]_** hash to the storage [oracle_state](#oracle_state).

#### verify_oracle_data

This function verifies that the given data is a valid data on BandChain as of the given block height.

params

| Type                                                              | Field Name                        | Description                                                                                                       |
| ----------------------------------------------------------------- | --------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `u64`                                                             | block_height                      | Block height of BancChain                                                                                         |
| `{{string,u64,bytes,u64,u64},{string,u64,u64,u64,u64,u32,bytes}}` | request_packet_and_respond_packet | A struct or a tuple of `request_packet` and `response_packet`                                                     |
| `u64`                                                             | version                           | Lastest block height that the data node was updated                                                               |
| `[{bool,u8,u64,u64,bytes}]`                                       | iavl_merkle_paths                 | An array of `iavl_merkle_path` which is the merkle proof that shows how the data leave is part of the oracle iAVL |

return values

| Type                                                              | Field Name                        | Description                                                   |
| ----------------------------------------------------------------- | --------------------------------- | ------------------------------------------------------------- |
| `{{string,u64,bytes,u64,u64},{string,u64,u64,u64,u64,u32,bytes}}` | request_packet_and_respond_packet | A struct or a tuple of `request_packet` and `response_packet` |

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

1. Read the `oracle module` **_[B]_** hash from the given `block_height` to check if it is available or not.

   - If the `oracle module` **_[B]_** hash is not available for the given `block_height` then `revert`
   - Else contiune

2. Calculate `H(0)`

3. Calculate the hash of parent node of H(i) and C(i) hash by hashing from bottom to the top according to [`merkle tree`](https://en.wikipedia.org/wiki/Merkle_tree) hashing scheme.

   - For i ∈ {0,1,2,...,n-1},`H(i+1)` = [get_parent_hash](#get_parent_hash)(C(i), H(i))

4. Check that `H(n)` must equal to `oracle module` **_[B]_** hash that just read from the storage in step 1.

   - If `H(n)` != `oracle module` **_[B]_** hash then `revert`
   - Else continue

5. return `request_packet_and_respond_packet`

#### verify_requests_count

This function verifies that the given request count is a information on BandChain at the given block height.

params

| Type                | Field Name   | Description                                                        |
| ------------------- | ------------ | ------------------------------------------------------------------ |
| `uint256`           | block height | The obi encoded data for oracle state relay and data verification. |
| `uint256`           | count        | The obi encoded data for oracle state relay and data verification. |
| `uint256`           | version      | The obi encoded data for oracle state relay and data verification. |
| `IAVLMerklePath[]`  | block height | The obi encoded data for oracle state relay and data verification. |

return values

| Type                                                              | Field Name                        | Description                                                   |
| ----------------------------------------------------------------- | --------------------------------- | ------------------------------------------------------------- |
| `{{string,u64,bytes,u64,u64},{string,u64,u64,u64,u64,u32,bytes}}` | request_packet_and_respond_packet | A struct or a tuple of `request_packet` and `response_packet` |

#### relay_and_verify

This function performs oracle state relay and oracle data verification in one go. The caller submits the obi encoded proof and receives back the decoded data, ready to be validated and used.

params

| Type    | Field Name | Description                                                        |
| ------- | ---------- | ------------------------------------------------------------------ |
| `bytes` | proof      | The obi encoded data for oracle state relay and data verification. |

return values

| Type                                                              | Field Name                        | Description                                                   |
| ----------------------------------------------------------------- | --------------------------------- | ------------------------------------------------------------- |
| `{{string,u64,bytes,u64,u64},{string,u64,u64,u64,u64,u32,bytes}}` | request_packet_and_respond_packet | A struct or a tuple of `request_packet` and `response_packet` |

1. Decode the `proof` using obi into 7 elements which are `block_height`, `multi_store_proof`, `block_header_merkle_parts`, `signatures`, `request_packet_and_respond_packet`, `version` and `iavl_merkle_paths`.

2. Relay the `oracle module` **_[B]_** to the state by call the function [relay_block](#relay_block) with `block_height`, `multi_store_proof`, `block_header_merkle_parts` and `signatures` as parameters.

3. Return the result from calling function [verify_oracle_data](#verify_oracle_data) with `block_height`,`request_packet_and_respond_packet`, `version` and `iavl_merkle_paths` as parameters.

#### relay_and_multi_verify

This function is like the `relay_and_verify` but the input contain multiple of `IAVLMerklePath[]` for multiple requests.

#### relay_and_verify_count

This function is like the `relay_and_verify` but using the `verify_requests_count` instead of the `verify_oracle_data`.

#### verify_proof

This function is able to verify any data that stored under the `oracle module` **_[B]_** by providing the data hash to the function.
