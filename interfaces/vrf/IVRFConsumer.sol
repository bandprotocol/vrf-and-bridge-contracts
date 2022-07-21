// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

/// @title IVRFConsumer interface
/// @notice Interface for the VRF consumer base
interface IVRFConsumer {
    /// @dev The function is called by the VRF provider in order to deliver results to the consumer.
    /// @param seed Any string that used to initialize the randomizer.
    /// @param time Timestamp where the random data was created.
    /// @param result A random bytes for given seed anfd time.
    function consume(
        string calldata seed,
        uint64 time,
        bytes32 result
    ) external;
}
