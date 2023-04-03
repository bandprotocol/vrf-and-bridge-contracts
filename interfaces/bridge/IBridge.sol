// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

interface IBridge {
    enum ResolveStatus {
        RESOLVE_STATUS_OPEN_UNSPECIFIED,
        RESOLVE_STATUS_SUCCESS,
        RESOLVE_STATUS_FAILURE,
        RESOLVE_STATUS_EXPIRED
    }
    /// Result struct is similar packet on Bandchain using to re-calculate result hash.
    struct Result {
        string clientID;
        uint64 oracleScriptID;
        bytes params;
        uint64 askCount;
        uint64 minCount;
        uint64 requestID;
        uint64 ansCount;
        uint64 requestTime;
        uint64 resolveTime;
        ResolveStatus resolveStatus;
        bytes result;
    }

    /// Performs oracle state relay and oracle data verification in one go. The caller submits
    /// the encoded proof and receives back the decoded data, ready to be validated and used.
    /// @param data The encoded data for oracle state relay and data verification.
    function relayAndVerify(
        bytes calldata data
    ) external returns (Result memory);

    /// Performs oracle state relay and many times of oracle data verification in one go. The caller submits
    /// the encoded proof and receives back the decoded data, ready to be validated and used.
    /// @param data The encoded data for oracle state relay and an array of data verification.
    function relayAndMultiVerify(
        bytes calldata data
    ) external returns (Result[] memory);

    /// Performs oracle state extraction and verification without saving root hash to storage in one go.
    /// The caller submits the encoded proof and receives back the decoded data, ready to be validated and used.
    /// NOTED: This is a new function. Cannot call this function on the lastet deployed contract.
    /// @param data The encoded data for oracle state relay and data verification.
    function verifyOracleResult(
        bytes calldata data
    ) external view returns (Result memory);

    // Performs oracle state relay and requests count verification in one go. The caller submits
    /// the encoded proof and receives back the decoded data, ready tobe validated and used.
    /// @param data The encoded data for oracle state relay and requests count verification.
    function relayAndVerifyCount(
        bytes calldata data
    ) external returns (uint64, uint64); // block time, requests count
}
