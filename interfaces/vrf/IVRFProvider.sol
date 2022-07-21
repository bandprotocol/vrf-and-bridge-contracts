// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

/// @title IVRFProvider interface
/// @notice Interface for the BandVRF provider
interface IVRFProvider {
    /// @dev The function for consumers who want random data.
    /// Consumers can simply make requests to get random data back later.
    /// @param seed Any string that used to initialize the randomizer.
    function requestRandomData(string calldata seed) external payable;
}
