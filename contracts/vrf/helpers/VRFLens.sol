// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {VRFProviderBase} from "../VRFProviderBase.sol";

interface IVRFProviderViewOnly {
    function tasks(uint64 nonce) external view returns(
        bool, uint64, address, uint256, bytes32, string memory, bytes memory, bytes memory
    );
    function oracleScriptID() external view returns(uint64);
    function minCount() external view returns(uint8);
    function askCount() external view returns(uint8);
}

contract VRFLens is Ownable {

    IVRFProviderViewOnly public provider;

    constructor(IVRFProviderViewOnly _provider) {
        provider = _provider;
    }

    function setProvider(IVRFProviderViewOnly _provider) external onlyOwner {
        provider = _provider;
    }

    function getTasksBulk(uint64[] calldata nonces) external view returns(VRFProviderBase.Task[] memory) {
        uint256 len = nonces.length;
        VRFProviderBase.Task[] memory tasks = new VRFProviderBase.Task[](len);
        for (uint256 i = 0; i < len; i++) {
            (
                bool a, uint64 b, address c, uint256 d, bytes32 e, string memory f, bytes memory g, bytes memory h
            ) = provider.tasks(nonces[i]);
            tasks[i] = VRFProviderBase.Task(a,b,c,d,e,f,g,h);
        }
        return tasks;
    }

    function getProviderConfig() external view returns(uint64, uint8, uint8) {
        return (provider.oracleScriptID(), provider.minCount(), provider.askCount());
    }
}
