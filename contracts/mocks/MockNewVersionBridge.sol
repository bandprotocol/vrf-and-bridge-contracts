// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.14;

import {EnumerableMap} from "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
import {Bridge} from "../bridge/Bridge.sol";

/// @title MockNewVersionBridge contract
/// @notice This contract is for testing the process of upgrading the Bridge from an older version to a newer one.
/// As you can see, this mock contract is assumed to be the newer one, which includes a new reset functionality.
contract MockNewVersionBridge is Bridge {
    using EnumerableMap for EnumerableMap.AddressToUintMap;

    function resetValidatorsAndChainID()
        external
        onlyRole(getRoleAdmin(DEFAULT_ADMIN_ROLE))
    {
        ValidatorWithPower[] memory validators = getValidators(
            0,
            getNumberOfValidators()
        );
        for (uint256 idx = 0; idx < validators.length; idx++) {
            validatorPowers.remove(validators[idx].addr);
        }

        totalValidatorPower = 0;
        encodedChainID = "";
    }
}
