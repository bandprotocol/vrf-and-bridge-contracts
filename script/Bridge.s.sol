// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;
 
import {Script, console} from "forge-std/Script.sol";

import {Bridge} from "contracts/bridge/Bridge.sol";

contract BridgeScript is Script {
    
    function run() public {
        vm.startBroadcast();
        
        new Bridge();
        
        vm.stopBroadcast();
    }
}