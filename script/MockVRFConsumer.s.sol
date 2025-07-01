// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;
 
import {Script, console} from "forge-std/Script.sol";
import {MockVRFConsumer} from "contracts/vrf/mocks/MockVRFConsumer.sol";
import {IVRFProvider} from "interfaces/vrf/IVRFProvider.sol";

contract MockVRFConsumerScript is Script {
    MockVRFConsumer public mockVRFConsumer;
 
    function setUp() public {}
 
    function run(address vrfProvider) public {
        vm.startBroadcast();
 
        mockVRFConsumer = new MockVRFConsumer(
            IVRFProvider(vrfProvider)
        );
 
        vm.stopBroadcast();
    }
}