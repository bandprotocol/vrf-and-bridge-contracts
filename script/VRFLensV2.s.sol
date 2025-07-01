// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;
 
import {Script, console} from "forge-std/Script.sol";
import {VRFLensV2, IVRFProviderViewOnly} from "contracts/vrf/helpers/VRFLensV2.sol";

contract VRFLensV2Script is Script { 
    function run(address vrfAddress) public {
        vm.startBroadcast();

        IVRFProviderViewOnly vrfProvider = IVRFProviderViewOnly(vrfAddress);
        new VRFLensV2(vrfProvider);
 
        vm.stopBroadcast();
    }
}