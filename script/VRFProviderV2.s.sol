// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;
 
import {Script, console} from "forge-std/Script.sol";
import {VRFProviderV2} from "contracts/vrf/provider_v2/VRFProviderV2.sol";
import {IBridge} from "interfaces/bridge/IBridge.sol";

contract VRFProviderV2Script is Script { 
    function run(uint64 _oracleScriptID, address _bridge, uint256 _minimumFee) public {
        vm.startBroadcast();
 
        new VRFProviderV2(
            _oracleScriptID, 
            IBridge(_bridge),
            _minimumFee
        );
 
        vm.stopBroadcast();
    }
}