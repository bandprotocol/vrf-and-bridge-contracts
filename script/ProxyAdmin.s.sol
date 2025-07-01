// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;
 
import {Script, console} from "forge-std/Script.sol";
import {ProxyAdmin} from "@openzeppelin/contracts/proxy/transparent/ProxyAdmin.sol";

contract ProxyAdminScript is Script {
 
    function run() public {
        vm.startBroadcast();

        new ProxyAdmin();
        
        vm.stopBroadcast();
    }
}