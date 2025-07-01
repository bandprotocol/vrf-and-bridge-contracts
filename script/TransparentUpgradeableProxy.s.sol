// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {Script, console} from "forge-std/Script.sol";
import {TransparentUpgradeableProxy} from "@openzeppelin/contracts/proxy/transparent/TransparentUpgradeableProxy.sol";
import {Bridge} from "contracts/bridge/Bridge.sol";

contract TransparentUpgradeableProxyScript is Script {
    Bridge.ValidatorWithPower[] validators;

    function run(string memory validatorsPath, bytes memory encodedChainID, address logic, address admin) public {
        string memory jsonRaw = vm.readFile(validatorsPath);

        uint256 i = 0;
        while (true) {
            string memory addrKey = string(
                abi.encodePacked(".validators[", vm.toString(i), "].address")
            );
            string memory powerKey = string(
                abi.encodePacked(".validators[", vm.toString(i), "].voting_power")
            );

            try vm.parseJsonAddress(jsonRaw, addrKey) returns (address valAddr) {
                uint256 valPower = vm.parseJsonUint(jsonRaw, powerKey);
                validators.push(
                    Bridge.ValidatorWithPower({addr: valAddr, power: valPower})
                );
                i++;
            } catch {
                break;
            }
        }

        vm.startBroadcast();

        bytes memory initData = abi.encodeCall(
            Bridge.initialize,
            (
                validators,
                encodedChainID
            )
        );

        new TransparentUpgradeableProxy(
            logic,
            admin,
            initData
        );

        vm.stopBroadcast();
    }
}